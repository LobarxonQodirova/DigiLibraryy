"""Views for the borrowing app."""

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsLibrarianOrAdmin, IsOwnerOrLibrarian
from apps.books.models import BookCopy

from .models import Borrowing, BorrowingHistory, Fine, Reservation, ReturnRecord
from .serializers import (
    BorrowingHistorySerializer,
    BorrowingSerializer,
    CheckoutSerializer,
    FineSerializer,
    PayFineSerializer,
    RenewSerializer,
    ReservationSerializer,
    ReturnBookSerializer,
    ReturnRecordSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    """
    Manage book borrowings (checkouts, renewals, returns).
    """

    serializer_class = BorrowingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Borrowing.objects.select_related(
            "user", "book_copy", "book_copy__book", "checked_out_by"
        )
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        return qs.filter(user=self.request.user)

    @action(detail=False, methods=["post"])
    def checkout(self, request):
        """Check out a book copy to a member."""
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        book_copy = BookCopy.objects.get(id=serializer.validated_data["book_copy_id"])

        # Determine the borrowing user
        if request.user.role in ("admin", "librarian"):
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_id = serializer.validated_data.get("user_id")
            if user_id:
                user = User.objects.get(id=user_id)
            else:
                user = request.user
        else:
            user = request.user

        # Check borrowing eligibility
        if hasattr(user, "member_profile") and not user.member_profile.can_borrow:
            return Response(
                {"error": "You are not eligible to borrow. Check membership status or outstanding fines."},
                status=status.HTTP_403_FORBIDDEN,
            )

        loan_days = getattr(settings, "LOAN_PERIOD_DAYS", 14)
        with transaction.atomic():
            borrowing = Borrowing.objects.create(
                user=user,
                book_copy=book_copy,
                due_date=timezone.now() + timedelta(days=loan_days),
                checked_out_by=request.user if request.user.role in ("admin", "librarian") else None,
                notes=serializer.validated_data.get("notes", ""),
            )
            book_copy.status = BookCopy.Status.CHECKED_OUT
            book_copy.save(update_fields=["status", "updated_at"])

        return Response(
            BorrowingSerializer(borrowing).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"])
    def renew(self, request):
        """Renew an active borrowing."""
        serializer = RenewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        borrowing = Borrowing.objects.get(id=serializer.validated_data["borrowing_id"])

        if borrowing.user != request.user and request.user.role not in ("admin", "librarian"):
            return Response(
                {"error": "You can only renew your own loans."},
                status=status.HTTP_403_FORBIDDEN,
            )

        loan_days = getattr(settings, "LOAN_PERIOD_DAYS", 14)
        borrowing.due_date = timezone.now() + timedelta(days=loan_days)
        borrowing.renewals_count += 1
        borrowing.save(update_fields=["due_date", "renewals_count", "updated_at"])

        return Response(BorrowingSerializer(borrowing).data)

    @action(detail=False, methods=["post"], url_path="return")
    def return_book(self, request):
        """Process a book return."""
        serializer = ReturnBookSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            borrowing = Borrowing.objects.get(
                id=serializer.validated_data["borrowing_id"],
                status=Borrowing.Status.ACTIVE,
            )
        except Borrowing.DoesNotExist:
            return Response(
                {"error": "Active borrowing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        with transaction.atomic():
            now = timezone.now()
            fine_amount = 0

            # Calculate overdue fine
            if now > borrowing.due_date:
                days_late = (now - borrowing.due_date).days
                daily_rate = getattr(settings, "DAILY_FINE_RATE", 0.50)
                max_fine = getattr(settings, "MAX_FINE_AMOUNT", 25.00)
                fine_amount = min(days_late * daily_rate, max_fine)

            # Create return record
            return_record = ReturnRecord.objects.create(
                borrowing=borrowing,
                returned_date=now,
                condition_on_return=serializer.validated_data["condition_on_return"],
                processed_by=request.user if request.user.role in ("admin", "librarian") else None,
                damage_notes=serializer.validated_data.get("damage_notes", ""),
                fine_assessed=fine_amount,
            )

            # Update borrowing
            borrowing.status = Borrowing.Status.RETURNED
            borrowing.return_date = now
            borrowing.save(update_fields=["status", "return_date", "updated_at"])

            # Update book copy status
            borrowing.book_copy.status = BookCopy.Status.AVAILABLE
            borrowing.book_copy.save(update_fields=["status", "updated_at"])

            # Create fine if applicable
            if fine_amount > 0:
                Fine.objects.create(
                    user=borrowing.user,
                    borrowing=borrowing,
                    amount=fine_amount,
                    reason=Fine.Reason.OVERDUE,
                    description=f"Overdue return: {(now - borrowing.due_date).days} days late",
                )

            # Create history entry
            BorrowingHistory.objects.create(
                user=borrowing.user,
                book=borrowing.book_copy.book,
                borrowing=borrowing,
                checkout_date=borrowing.checkout_date,
                return_date=now,
                was_overdue=fine_amount > 0,
                fine_amount=fine_amount,
            )

        return Response(ReturnRecordSerializer(return_record).data)


class ReservationViewSet(viewsets.ModelViewSet):
    """Manage book reservations / holds."""

    serializer_class = ReservationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Reservation.objects.select_related("user", "book", "book_copy")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        return qs.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Assign queue position
        book = serializer.validated_data["book"]
        last_position = (
            Reservation.objects.filter(book=book, status=Reservation.Status.PENDING)
            .order_by("-queue_position")
            .values_list("queue_position", flat=True)
            .first()
        ) or 0

        serializer.save(
            user=self.request.user,
            queue_position=last_position + 1,
        )

    @action(detail=True, methods=["post"])
    def cancel(self, request, pk=None):
        """Cancel a reservation."""
        reservation = self.get_object()
        if reservation.status not in (Reservation.Status.PENDING, Reservation.Status.READY):
            return Response(
                {"error": "Only pending or ready reservations can be cancelled."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        reservation.status = Reservation.Status.CANCELLED
        reservation.save(update_fields=["status", "updated_at"])
        return Response(ReservationSerializer(reservation).data)


class BorrowingHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Read-only access to borrowing history."""

    serializer_class = BorrowingHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = BorrowingHistory.objects.select_related("user", "book")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        return qs.filter(user=self.request.user)


class FineViewSet(viewsets.ModelViewSet):
    """Manage fines."""

    serializer_class = FineSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Fine.objects.select_related("user", "borrowing")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        return qs.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        """Process a fine payment."""
        fine = self.get_object()
        serializer = PayFineSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payment_amount = serializer.validated_data["amount"]
        if payment_amount > fine.balance:
            return Response(
                {"error": f"Payment amount exceeds balance of ${fine.balance}."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        fine.amount_paid += payment_amount
        if fine.amount_paid >= fine.amount:
            fine.status = Fine.Status.PAID
            fine.paid_date = timezone.now()
        else:
            fine.status = Fine.Status.PARTIALLY_PAID
        fine.save(update_fields=["amount_paid", "status", "paid_date", "updated_at"])

        # Update member profile total fines
        if hasattr(fine.user, "member_profile"):
            profile = fine.user.member_profile
            profile.total_fines_owed = (
                Fine.objects.filter(user=fine.user, status__in=["pending", "partial"])
                .values_list("amount", flat=True)
            )
            total_owed = sum(
                f.balance for f in Fine.objects.filter(
                    user=fine.user, status__in=["pending", "partial"]
                )
            )
            profile.total_fines_owed = total_owed
            profile.save(update_fields=["total_fines_owed", "updated_at"])

        return Response(FineSerializer(fine).data)

    @action(detail=True, methods=["post"])
    def waive(self, request, pk=None):
        """Waive a fine (librarian/admin only)."""
        if request.user.role not in ("admin", "librarian"):
            return Response(
                {"error": "Only librarians can waive fines."},
                status=status.HTTP_403_FORBIDDEN,
            )
        fine = self.get_object()
        reason = request.data.get("reason", "")
        fine.status = Fine.Status.WAIVED
        fine.waived_by = request.user
        fine.waived_reason = reason
        fine.save(update_fields=["status", "waived_by", "waived_reason", "updated_at"])
        return Response(FineSerializer(fine).data)

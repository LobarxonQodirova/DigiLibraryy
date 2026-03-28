"""Serializers for the borrowing app."""

from django.conf import settings
from rest_framework import serializers

from apps.books.serializers import BookCopySerializer, BookListSerializer

from .models import Borrowing, BorrowingHistory, Fine, Reservation, ReturnRecord


class BorrowingSerializer(serializers.ModelSerializer):
    book_copy_detail = BookCopySerializer(source="book_copy", read_only=True)
    book_title = serializers.CharField(source="book_copy.book.title", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    days_overdue = serializers.IntegerField(read_only=True)
    can_renew = serializers.BooleanField(read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id", "user", "user_name", "book_copy", "book_copy_detail",
            "book_title", "checkout_date", "due_date", "return_date",
            "status", "status_display", "renewals_count",
            "is_overdue", "days_overdue", "can_renew",
            "checked_out_by", "notes", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "checkout_date", "renewals_count",
            "checked_out_by", "created_at", "updated_at",
        ]


class CheckoutSerializer(serializers.Serializer):
    """Serializer for checking out a book copy."""

    book_copy_id = serializers.UUIDField()
    user_id = serializers.UUIDField(required=False, help_text="Required for librarian checkouts")
    notes = serializers.CharField(required=False, allow_blank=True, default="")

    def validate_book_copy_id(self, value):
        from apps.books.models import BookCopy
        try:
            copy = BookCopy.objects.get(id=value)
        except BookCopy.DoesNotExist:
            raise serializers.ValidationError("Book copy not found.")
        if not copy.is_available:
            raise serializers.ValidationError(
                f"This copy is currently {copy.get_status_display().lower()}."
            )
        return value


class RenewSerializer(serializers.Serializer):
    """Serializer for renewing a borrowing."""

    borrowing_id = serializers.UUIDField()

    def validate_borrowing_id(self, value):
        try:
            borrowing = Borrowing.objects.get(id=value)
        except Borrowing.DoesNotExist:
            raise serializers.ValidationError("Borrowing record not found.")
        if not borrowing.can_renew:
            raise serializers.ValidationError("This loan cannot be renewed.")
        return value


class ReturnRecordSerializer(serializers.ModelSerializer):
    borrowing_detail = BorrowingSerializer(source="borrowing", read_only=True)
    condition_display = serializers.CharField(source="get_condition_on_return_display", read_only=True)

    class Meta:
        model = ReturnRecord
        fields = [
            "id", "borrowing", "borrowing_detail", "returned_date",
            "condition_on_return", "condition_display", "processed_by",
            "damage_notes", "fine_assessed", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ReturnBookSerializer(serializers.Serializer):
    """Serializer for processing a book return."""

    borrowing_id = serializers.UUIDField()
    condition_on_return = serializers.ChoiceField(
        choices=ReturnRecord.Condition.choices, default="good",
    )
    damage_notes = serializers.CharField(required=False, allow_blank=True, default="")


class ReservationSerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source="book", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Reservation
        fields = [
            "id", "user", "user_name", "book", "book_detail",
            "book_copy", "status", "status_display",
            "reservation_date", "expiry_date", "pickup_by_date",
            "queue_position", "notification_sent", "notes",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "queue_position", "notification_sent",
            "book_copy", "expiry_date", "pickup_by_date",
            "created_at", "updated_at",
        ]


class BorrowingHistorySerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source="book", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = BorrowingHistory
        fields = [
            "id", "user", "user_name", "book", "book_detail",
            "checkout_date", "return_date", "was_overdue",
            "fine_amount", "rating", "review", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class FineSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    balance = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    reason_display = serializers.CharField(source="get_reason_display", read_only=True)

    class Meta:
        model = Fine
        fields = [
            "id", "user", "user_name", "borrowing", "amount",
            "amount_paid", "balance", "reason", "reason_display",
            "status", "status_display", "description",
            "issued_date", "paid_date", "waived_by", "waived_reason",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "amount_paid", "issued_date", "paid_date",
            "waived_by", "created_at", "updated_at",
        ]


class PayFineSerializer(serializers.Serializer):
    """Serializer for paying a fine."""

    amount = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0.01)
    payment_method = serializers.ChoiceField(
        choices=[("cash", "Cash"), ("card", "Card"), ("online", "Online")],
        default="cash",
    )

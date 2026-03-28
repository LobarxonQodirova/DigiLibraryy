"""Views for the members app."""

from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsLibrarianOrAdmin, IsOwnerOrLibrarian

from .models import MembershipCard, ReadingList, ReadingListItem
from .serializers import (
    MembershipCardSerializer,
    ReadingListCreateSerializer,
    ReadingListItemSerializer,
    ReadingListSerializer,
)


class MembershipCardViewSet(viewsets.ModelViewSet):
    """Manage membership cards."""

    serializer_class = MembershipCardSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = MembershipCard.objects.select_related("user")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        return qs.filter(user=self.request.user)

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="report-lost")
    def report_lost(self, request, pk=None):
        """Report a membership card as lost and issue a replacement."""
        card = self.get_object()
        if card.status == MembershipCard.CardStatus.LOST:
            return Response(
                {"error": "This card is already reported as lost."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        card.status = MembershipCard.CardStatus.LOST
        card.save(update_fields=["status", "updated_at"])

        return Response(
            {"message": "Card reported as lost. Please contact the library for a replacement."}
        )


class ReadingListViewSet(viewsets.ModelViewSet):
    """Manage user reading lists."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return ReadingListCreateSerializer
        return ReadingListSerializer

    def get_queryset(self):
        qs = ReadingList.objects.select_related("user").prefetch_related("items__book")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        # Members see their own lists + public lists from others
        return qs.filter(
            models__isnull=True  # placeholder -- see below
        ) | qs.filter(user=self.request.user) | qs.filter(is_public=True)

    def get_queryset(self):
        qs = ReadingList.objects.select_related("user").prefetch_related("items__book")
        if self.request.user.role in ("admin", "librarian"):
            return qs.all()
        from django.db.models import Q
        return qs.filter(Q(user=self.request.user) | Q(is_public=True))

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="add-book")
    def add_book(self, request, pk=None):
        """Add a book to this reading list."""
        reading_list = self.get_object()
        if reading_list.user != request.user:
            return Response(
                {"error": "You can only add books to your own reading lists."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = ReadingListItemSerializer(data={
            "reading_list": reading_list.id,
            "book": request.data.get("book_id"),
            "status": request.data.get("status", "want"),
            "priority": request.data.get("priority", 0),
            "personal_notes": request.data.get("notes", ""),
        })
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["delete"], url_path="remove-book/(?P<book_id>[^/.]+)")
    def remove_book(self, request, pk=None, book_id=None):
        """Remove a book from this reading list."""
        reading_list = self.get_object()
        if reading_list.user != request.user:
            return Response(
                {"error": "You can only modify your own reading lists."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            item = ReadingListItem.objects.get(reading_list=reading_list, book_id=book_id)
            item.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ReadingListItem.DoesNotExist:
            return Response(
                {"error": "Book not found in this reading list."},
                status=status.HTTP_404_NOT_FOUND,
            )

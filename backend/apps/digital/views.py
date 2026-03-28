"""Views for the digital app."""

from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsLibrarianOrAdmin

from .models import DigitalResource, Download, EBook, ReadingProgress
from .serializers import (
    DigitalResourceSerializer,
    DownloadSerializer,
    EBookBorrowSerializer,
    EBookSerializer,
    ReadingProgressSerializer,
    UpdateProgressSerializer,
)
from .services import DigitalLendingService


class DigitalResourceViewSet(viewsets.ModelViewSet):
    """Manage digital resources (PDFs, audio, video, articles)."""

    queryset = DigitalResource.objects.all()
    serializer_class = DigitalResourceSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated:
            qs = qs.filter(is_public=True)
        return qs

    @action(detail=True, methods=["post"])
    def download(self, request, pk=None):
        """Record a download event for this resource."""
        resource = self.get_object()
        download = Download.objects.create(
            user=request.user,
            digital_resource=resource,
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:500],
        )
        resource.download_count += 1
        resource.save(update_fields=["download_count"])
        return Response(DownloadSerializer(download).data, status=status.HTTP_201_CREATED)


class EBookViewSet(viewsets.ModelViewSet):
    """Manage e-books and digital lending."""

    queryset = EBook.objects.select_related("book").prefetch_related("book__authors").all()
    serializer_class = EBookSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        if self.action in ("borrow", "return_ebook", "my_loans"):
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    @action(detail=False, methods=["post"])
    def borrow(self, request):
        """Borrow an e-book (creates a time-limited digital loan)."""
        serializer = EBookBorrowSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        ebook = EBook.objects.get(id=serializer.validated_data["ebook_id"])
        service = DigitalLendingService()

        try:
            download = service.borrow_ebook(request.user, ebook, request)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(DownloadSerializer(download).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="return")
    def return_ebook(self, request):
        """Return a borrowed e-book (release the license)."""
        download_id = request.data.get("download_id")
        if not download_id:
            return Response(
                {"error": "download_id is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        service = DigitalLendingService()
        try:
            service.return_ebook(request.user, download_id)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message": "E-book returned successfully."})

    @action(detail=False, methods=["get"], url_path="my-loans")
    def my_loans(self, request):
        """List the current user's active e-book loans."""
        downloads = Download.objects.filter(
            user=request.user, ebook__isnull=False, is_active=True,
        ).select_related("ebook__book")
        serializer = DownloadSerializer(downloads, many=True)
        return Response(serializer.data)


class ReadingProgressViewSet(viewsets.ModelViewSet):
    """Track and manage reading progress for e-books."""

    serializer_class = ReadingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ReadingProgress.objects.filter(
            user=self.request.user
        ).select_related("ebook__book")

    @action(detail=True, methods=["post"], url_path="update-progress")
    def update_progress(self, request, pk=None):
        """Update reading position for an e-book."""
        progress = self.get_object()
        serializer = UpdateProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        progress.update_progress(
            page=serializer.validated_data["current_page"],
            total_pages=serializer.validated_data.get("total_pages"),
        )
        extra_time = serializer.validated_data.get("time_spent_seconds", 0)
        if extra_time > 0:
            progress.time_spent_seconds += extra_time
            progress.save(update_fields=["time_spent_seconds"])

        return Response(ReadingProgressSerializer(progress).data)

    @action(detail=True, methods=["post"], url_path="add-bookmark")
    def add_bookmark(self, request, pk=None):
        """Add a bookmark to the current e-book."""
        progress = self.get_object()
        page = request.data.get("page")
        label = request.data.get("label", "")
        if page is None:
            return Response(
                {"error": "page is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        bookmark = {"page": page, "label": label, "created_at": timezone.now().isoformat()}
        progress.bookmarks.append(bookmark)
        progress.save(update_fields=["bookmarks", "updated_at"])
        return Response(ReadingProgressSerializer(progress).data)

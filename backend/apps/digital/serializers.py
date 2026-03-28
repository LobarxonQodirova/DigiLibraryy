"""Serializers for the digital app."""

from rest_framework import serializers

from .models import DigitalResource, Download, EBook, ReadingProgress


class DigitalResourceSerializer(serializers.ModelSerializer):
    resource_type_display = serializers.CharField(source="get_resource_type_display", read_only=True)

    class Meta:
        model = DigitalResource
        fields = [
            "id", "title", "description", "resource_type",
            "resource_type_display", "file", "file_size_bytes",
            "mime_type", "duration_seconds", "is_public",
            "requires_subscription", "download_count",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "download_count", "created_at", "updated_at"]


class EBookSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source="book.title", read_only=True)
    book_cover = serializers.ImageField(source="book.cover_image", read_only=True)
    authors = serializers.SerializerMethodField()
    available_licenses = serializers.IntegerField(read_only=True)
    is_available = serializers.BooleanField(read_only=True)
    format_display = serializers.CharField(source="get_format_display", read_only=True)

    class Meta:
        model = EBook
        fields = [
            "id", "book", "book_title", "book_cover", "authors",
            "file", "format", "format_display", "file_size_bytes",
            "total_licenses", "active_loans", "available_licenses",
            "is_available", "drm_protected", "preview_available",
            "preview_percentage", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "active_loans", "created_at", "updated_at"]

    def get_authors(self, obj):
        return [
            {"id": str(a.id), "name": a.full_name}
            for a in obj.book.authors.all()
        ]


class EBookBorrowSerializer(serializers.Serializer):
    """Serializer for borrowing an e-book."""
    ebook_id = serializers.UUIDField()

    def validate_ebook_id(self, value):
        try:
            ebook = EBook.objects.get(id=value)
        except EBook.DoesNotExist:
            raise serializers.ValidationError("E-book not found.")
        if not ebook.is_available:
            raise serializers.ValidationError("No licenses currently available for this e-book.")
        return value


class DownloadSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    resource_title = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = Download
        fields = [
            "id", "user", "user_name", "ebook", "digital_resource",
            "resource_title", "downloaded_at", "expires_at",
            "is_active", "is_expired", "created_at",
        ]
        read_only_fields = ["id", "downloaded_at"]

    def get_resource_title(self, obj):
        if obj.ebook:
            return obj.ebook.book.title
        if obj.digital_resource:
            return obj.digital_resource.title
        return None


class ReadingProgressSerializer(serializers.ModelSerializer):
    ebook_title = serializers.CharField(source="ebook.book.title", read_only=True)
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = ReadingProgress
        fields = [
            "id", "user", "user_name", "ebook", "ebook_title",
            "current_page", "total_pages", "percentage_complete",
            "last_read_at", "bookmarks", "annotations",
            "time_spent_seconds", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "percentage_complete", "created_at", "updated_at"]


class UpdateProgressSerializer(serializers.Serializer):
    """Serializer for updating reading progress."""

    current_page = serializers.IntegerField(min_value=0)
    total_pages = serializers.IntegerField(min_value=1, required=False)
    time_spent_seconds = serializers.IntegerField(min_value=0, required=False, default=0)

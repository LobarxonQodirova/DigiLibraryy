"""Models for the digital app -- EBook, DigitalResource, Download, ReadingProgress."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class DigitalResource(models.Model):
    """
    Generic digital resource available in the library (PDFs, audio, video, etc.).
    """

    class ResourceType(models.TextChoices):
        PDF = "pdf", "PDF Document"
        AUDIO = "audio", "Audiobook"
        VIDEO = "video", "Video"
        ARTICLE = "article", "Journal Article"
        DATASET = "dataset", "Dataset"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=20, choices=ResourceType.choices, default=ResourceType.PDF,
    )
    file = models.FileField(upload_to="digital_resources/")
    file_size_bytes = models.BigIntegerField(default=0)
    mime_type = models.CharField(max_length=100, blank=True)
    duration_seconds = models.PositiveIntegerField(
        null=True, blank=True, help_text="For audio/video resources",
    )
    is_public = models.BooleanField(default=False, help_text="Available without login")
    requires_subscription = models.BooleanField(default=False)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.resource_type.upper()}] {self.title}"


class EBook(models.Model):
    """
    E-Book with DRM-aware licensing.
    Linked to a Book record for catalog integration.
    """

    class Format(models.TextChoices):
        EPUB = "epub", "EPUB"
        PDF = "pdf", "PDF"
        MOBI = "mobi", "MOBI"
        AZW3 = "azw3", "AZW3"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.OneToOneField(
        "books.Book", on_delete=models.CASCADE, related_name="ebook",
    )
    file = models.FileField(upload_to="ebooks/")
    format = models.CharField(max_length=10, choices=Format.choices, default=Format.EPUB)
    file_size_bytes = models.BigIntegerField(default=0)
    total_licenses = models.PositiveIntegerField(
        default=1, help_text="Total simultaneous loans allowed",
    )
    active_loans = models.PositiveIntegerField(default=0)
    drm_protected = models.BooleanField(default=True)
    preview_available = models.BooleanField(default=True)
    preview_percentage = models.PositiveIntegerField(
        default=10, help_text="Percentage of book available as preview",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "E-Book"
        verbose_name_plural = "E-Books"

    def __str__(self):
        return f"E-Book: {self.book.title} ({self.format})"

    @property
    def available_licenses(self):
        return max(0, self.total_licenses - self.active_loans)

    @property
    def is_available(self):
        return self.available_licenses > 0


class Download(models.Model):
    """Tracks downloads of digital resources and e-books."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="downloads",
    )
    ebook = models.ForeignKey(
        EBook, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="downloads",
    )
    digital_resource = models.ForeignKey(
        DigitalResource, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="downloads",
    )
    downloaded_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    is_active = models.BooleanField(default=True, help_text="Loan still active")

    class Meta:
        ordering = ["-downloaded_at"]

    def __str__(self):
        resource = self.ebook or self.digital_resource
        return f"{self.user} downloaded {resource} on {self.downloaded_at.date()}"

    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class ReadingProgress(models.Model):
    """Tracks a user's reading progress in a digital book."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reading_progress",
    )
    ebook = models.ForeignKey(
        EBook, on_delete=models.CASCADE, related_name="reading_progress",
    )
    current_page = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=0)
    percentage_complete = models.DecimalField(
        max_digits=5, decimal_places=2, default=0.00,
    )
    last_read_at = models.DateTimeField(default=timezone.now)
    bookmarks = models.JSONField(
        default=list, blank=True,
        help_text="List of bookmarked page numbers / positions",
    )
    annotations = models.JSONField(
        default=list, blank=True,
        help_text="List of user annotations / highlights",
    )
    time_spent_seconds = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_read_at"]
        unique_together = ("user", "ebook")
        verbose_name_plural = "Reading Progress"

    def __str__(self):
        return f"{self.user} - {self.ebook.book.title} ({self.percentage_complete}%)"

    def update_progress(self, page, total_pages=None):
        """Update reading position and recalculate percentage."""
        self.current_page = page
        if total_pages:
            self.total_pages = total_pages
        if self.total_pages > 0:
            self.percentage_complete = round((page / self.total_pages) * 100, 2)
        self.last_read_at = timezone.now()
        self.save()

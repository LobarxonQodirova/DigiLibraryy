"""Models for the catalog app -- Catalog, CatalogEntry, Classification."""

import uuid

from django.db import models


class Classification(models.Model):
    """
    Library classification scheme entry (e.g. Dewey Decimal, LC).
    Supports hierarchical classifications via `parent`.
    """

    class Scheme(models.TextChoices):
        DEWEY = "dewey", "Dewey Decimal"
        LOC = "loc", "Library of Congress"
        UDC = "udc", "Universal Decimal Classification"
        CUSTOM = "custom", "Custom"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scheme = models.CharField(max_length=20, choices=Scheme.choices, default=Scheme.DEWEY)
    code = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    level = models.PositiveIntegerField(default=0, help_text="Depth in the hierarchy (0 = top)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["scheme", "code"]
        unique_together = ("scheme", "code")
        verbose_name_plural = "Classifications"

    def __str__(self):
        return f"[{self.scheme.upper()}] {self.code} - {self.name}"


class Catalog(models.Model):
    """
    A named catalog that groups books into collections.
    Examples: 'Main Library', 'Children''s Section', 'Reference Only'.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=True, help_text="Visible to members")
    is_active = models.BooleanField(default=True)
    location = models.CharField(max_length=200, blank=True, help_text="Physical location or branch name")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def entry_count(self):
        return self.entries.count()


class CatalogEntry(models.Model):
    """
    Maps a Book to a Catalog with an optional Classification.
    A single book can appear in multiple catalogs.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    catalog = models.ForeignKey(
        Catalog, on_delete=models.CASCADE, related_name="entries",
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="catalog_entries",
    )
    classification = models.ForeignKey(
        Classification, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="catalog_entries",
    )
    call_number = models.CharField(
        max_length=50, blank=True,
        help_text="Library call number for physical shelving",
    )
    date_added = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["call_number"]
        unique_together = ("catalog", "book")
        verbose_name_plural = "Catalog Entries"

    def __str__(self):
        return f"{self.catalog.name}: {self.book.title} ({self.call_number})"

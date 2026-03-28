"""Models for the members app -- MemberProfile proxy, MembershipCard, ReadingList."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class MembershipCard(models.Model):
    """
    Physical or digital membership card issued to a library member.
    Linked to the MemberProfile in the accounts app.
    """

    class CardType(models.TextChoices):
        PHYSICAL = "physical", "Physical Card"
        DIGITAL = "digital", "Digital Card"

    class CardStatus(models.TextChoices):
        ACTIVE = "active", "Active"
        EXPIRED = "expired", "Expired"
        SUSPENDED = "suspended", "Suspended"
        LOST = "lost", "Lost"
        REPLACED = "replaced", "Replaced"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="membership_cards",
    )
    card_number = models.CharField(max_length=30, unique=True)
    card_type = models.CharField(
        max_length=20, choices=CardType.choices, default=CardType.PHYSICAL,
    )
    status = models.CharField(
        max_length=20, choices=CardStatus.choices, default=CardStatus.ACTIVE,
    )
    issued_date = models.DateField(default=timezone.now)
    expiry_date = models.DateField()
    barcode = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.ImageField(upload_to="membership_qr/", null=True, blank=True)
    replaced_by = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="replaces",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_date"]

    def __str__(self):
        return f"Card {self.card_number} - {self.user.get_full_name()}"

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = f"MC{self.card_number}"
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return (
            self.status == self.CardStatus.ACTIVE
            and self.expiry_date >= timezone.now().date()
        )


class ReadingList(models.Model):
    """User-curated reading list / wishlist."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reading_lists",
    )
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        unique_together = ("user", "name")

    def __str__(self):
        return f"{self.user.get_full_name()}: {self.name}"

    @property
    def book_count(self):
        return self.items.count()


class ReadingListItem(models.Model):
    """An individual book entry in a reading list."""

    class ReadStatus(models.TextChoices):
        WANT_TO_READ = "want", "Want to Read"
        READING = "reading", "Currently Reading"
        FINISHED = "finished", "Finished"
        ABANDONED = "abandoned", "Abandoned"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    reading_list = models.ForeignKey(
        ReadingList, on_delete=models.CASCADE, related_name="items",
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="reading_list_items",
    )
    status = models.CharField(
        max_length=20, choices=ReadStatus.choices, default=ReadStatus.WANT_TO_READ,
    )
    priority = models.PositiveIntegerField(default=0, help_text="Higher = more important")
    personal_notes = models.TextField(blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    date_started = models.DateTimeField(null=True, blank=True)
    date_finished = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-priority", "date_added"]
        unique_together = ("reading_list", "book")

    def __str__(self):
        return f"{self.book.title} ({self.get_status_display()})"

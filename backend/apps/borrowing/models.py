"""Models for the borrowing app -- Borrowing, Reservation, BorrowingHistory, Fine, ReturnRecord."""

import uuid
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class Borrowing(models.Model):
    """Active loan of a physical book copy to a member."""

    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        RETURNED = "returned", "Returned"
        OVERDUE = "overdue", "Overdue"
        LOST = "lost", "Lost"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="loans",
    )
    book_copy = models.ForeignKey(
        "books.BookCopy", on_delete=models.CASCADE,
        related_name="loans",
    )
    checkout_date = models.DateTimeField(default=timezone.now)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE,
    )
    renewals_count = models.PositiveIntegerField(default=0)
    checked_out_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="checkouts_processed",
        help_text="Librarian who processed the checkout",
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-checkout_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["due_date"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.book_copy.book.title} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.due_date:
            loan_days = getattr(settings, "LOAN_PERIOD_DAYS", 14)
            self.due_date = self.checkout_date + timedelta(days=loan_days)
        super().save(*args, **kwargs)

    @property
    def is_overdue(self):
        if self.status == self.Status.ACTIVE and timezone.now() > self.due_date:
            return True
        return False

    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now() - self.due_date).days
        return 0

    @property
    def can_renew(self):
        max_renewals = getattr(settings, "MAX_RENEWALS", 2)
        return (
            self.status == self.Status.ACTIVE
            and self.renewals_count < max_renewals
            and not Reservation.objects.filter(
                book_copy=self.book_copy, status=Reservation.Status.PENDING
            ).exists()
        )


class ReturnRecord(models.Model):
    """Record of a book return, including condition assessment."""

    class Condition(models.TextChoices):
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        DAMAGED = "damaged", "Damaged"
        LOST = "lost", "Lost"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrowing = models.OneToOneField(
        Borrowing, on_delete=models.CASCADE, related_name="return_record",
    )
    returned_date = models.DateTimeField(default=timezone.now)
    condition_on_return = models.CharField(
        max_length=20, choices=Condition.choices, default=Condition.GOOD,
    )
    processed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="returns_processed",
    )
    damage_notes = models.TextField(blank=True)
    fine_assessed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-returned_date"]

    def __str__(self):
        return f"Return: {self.borrowing.book_copy.book.title} on {self.returned_date.date()}"


class Reservation(models.Model):
    """Hold / reservation request for a book or specific copy."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        READY = "ready", "Ready for Pickup"
        FULFILLED = "fulfilled", "Fulfilled"
        CANCELLED = "cancelled", "Cancelled"
        EXPIRED = "expired", "Expired"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="reservations",
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="reservations",
    )
    book_copy = models.ForeignKey(
        "books.BookCopy", on_delete=models.SET_NULL,
        null=True, blank=True, related_name="reservations",
        help_text="Assigned when a copy becomes available",
    )
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING,
    )
    reservation_date = models.DateTimeField(default=timezone.now)
    expiry_date = models.DateTimeField(null=True, blank=True)
    pickup_by_date = models.DateTimeField(
        null=True, blank=True,
        help_text="Deadline for the member to pick up the reserved copy",
    )
    queue_position = models.PositiveIntegerField(default=0)
    notification_sent = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["queue_position", "reservation_date"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["book", "status"]),
        ]

    def __str__(self):
        return f"{self.user} reserved {self.book.title} (#{self.queue_position})"


class BorrowingHistory(models.Model):
    """Aggregate borrowing history for analytics and member records."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="borrowing_history",
    )
    book = models.ForeignKey(
        "books.Book", on_delete=models.CASCADE, related_name="borrowing_history",
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="history_entries",
    )
    checkout_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    was_overdue = models.BooleanField(default=False)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rating = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Member's rating of the book (1-5)",
    )
    review = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-checkout_date"]
        verbose_name_plural = "Borrowing Histories"

    def __str__(self):
        return f"{self.user} - {self.book.title} ({self.checkout_date.date()})"


class Fine(models.Model):
    """Monetary fine assessed to a member for overdue or damaged items."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        WAIVED = "waived", "Waived"
        PARTIALLY_PAID = "partial", "Partially Paid"

    class Reason(models.TextChoices):
        OVERDUE = "overdue", "Overdue Return"
        DAMAGE = "damage", "Damaged Item"
        LOST = "lost", "Lost Item"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="fines",
    )
    borrowing = models.ForeignKey(
        Borrowing, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="fines",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reason = models.CharField(max_length=20, choices=Reason.choices, default=Reason.OVERDUE)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    description = models.TextField(blank=True)
    issued_date = models.DateTimeField(default=timezone.now)
    paid_date = models.DateTimeField(null=True, blank=True)
    waived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="fines_waived",
    )
    waived_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issued_date"]
        indexes = [
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"Fine #{self.id!s:.8} - {self.user} - ${self.amount}"

    @property
    def balance(self):
        return self.amount - self.amount_paid

"""Models for the notifications app."""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Notification(models.Model):
    """In-app notification delivered to a user."""

    class NotificationType(models.TextChoices):
        DUE_REMINDER = "due_reminder", "Due Date Reminder"
        OVERDUE = "overdue", "Overdue Notice"
        RESERVATION_READY = "reservation_ready", "Reservation Ready"
        FINE_ISSUED = "fine_issued", "Fine Issued"
        FINE_PAID = "fine_paid", "Fine Paid"
        MEMBERSHIP_EXPIRY = "membership_expiry", "Membership Expiry"
        SYSTEM = "system", "System Notification"
        NEW_BOOK = "new_book", "New Book Available"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name="notifications",
    )
    notification_type = models.CharField(
        max_length=30, choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    action_url = models.CharField(
        max_length=500, blank=True,
        help_text="Frontend route to navigate to when notification is clicked",
    )
    metadata = models.JSONField(
        default=dict, blank=True,
        help_text="Extra data (e.g. book_id, fine_id)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_read"]),
        ]

    def __str__(self):
        return f"[{self.notification_type}] {self.title} -> {self.user}"

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

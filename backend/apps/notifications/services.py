"""Notification dispatch services."""

import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Creates in-app notifications and optionally sends
    corresponding emails.
    """

    @staticmethod
    def notify(user, notification_type, title, message, action_url="", metadata=None, send_email=True):
        """
        Create an in-app notification and optionally send an email.

        Args:
            user:              Target User instance
            notification_type: One of Notification.NotificationType values
            title:             Short summary
            message:           Full notification body
            action_url:        Frontend URL for the notification link
            metadata:          Extra JSON-serialisable data
            send_email:        Whether to also send an email
        """
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url,
            metadata=metadata or {},
        )

        if send_email and user.email:
            try:
                send_mail(
                    subject=f"DigiLibrary: {title}",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as exc:
                logger.error("Failed to send email to %s: %s", user.email, exc)

        return notification

    @staticmethod
    def notify_due_reminder(user, borrowing):
        """Send a due-date reminder."""
        return NotificationService.notify(
            user=user,
            notification_type=Notification.NotificationType.DUE_REMINDER,
            title=f"'{borrowing.book_copy.book.title}' is due soon",
            message=(
                f"Your loan of '{borrowing.book_copy.book.title}' is due on "
                f"{borrowing.due_date.strftime('%B %d, %Y')}. "
                f"Please return or renew it to avoid late fees."
            ),
            action_url=f"/my-books/loans/{borrowing.id}",
            metadata={"borrowing_id": str(borrowing.id)},
        )

    @staticmethod
    def notify_overdue(user, borrowing, fine_amount):
        """Notify about an overdue loan and fine."""
        return NotificationService.notify(
            user=user,
            notification_type=Notification.NotificationType.OVERDUE,
            title=f"Overdue: '{borrowing.book_copy.book.title}'",
            message=(
                f"Your loan of '{borrowing.book_copy.book.title}' is overdue. "
                f"A fine of ${fine_amount:.2f} has been applied. "
                f"Please return the book as soon as possible."
            ),
            action_url=f"/my-books/loans/{borrowing.id}",
            metadata={
                "borrowing_id": str(borrowing.id),
                "fine_amount": str(fine_amount),
            },
        )

    @staticmethod
    def notify_reservation_ready(user, reservation):
        """Notify that a reserved book is ready for pickup."""
        return NotificationService.notify(
            user=user,
            notification_type=Notification.NotificationType.RESERVATION_READY,
            title=f"'{reservation.book.title}' is ready for pickup",
            message=(
                f"Great news! Your reserved copy of '{reservation.book.title}' "
                f"is now available. Please pick it up by "
                f"{reservation.pickup_by_date.strftime('%B %d, %Y')}."
            ),
            action_url=f"/my-books/reservations/{reservation.id}",
            metadata={"reservation_id": str(reservation.id)},
        )

    @staticmethod
    def notify_membership_expiry(user, days_remaining):
        """Warn about upcoming membership expiry."""
        return NotificationService.notify(
            user=user,
            notification_type=Notification.NotificationType.MEMBERSHIP_EXPIRY,
            title="Membership expiring soon",
            message=(
                f"Your library membership will expire in {days_remaining} day(s). "
                f"Please renew to continue enjoying library services."
            ),
            action_url="/profile/membership",
            metadata={"days_remaining": days_remaining},
        )

    @staticmethod
    def get_unread_count(user):
        """Return the number of unread notifications for a user."""
        return Notification.objects.filter(user=user, is_read=False).count()

    @staticmethod
    def mark_all_read(user):
        """Mark all notifications as read for a user."""
        from django.utils import timezone
        Notification.objects.filter(user=user, is_read=False).update(
            is_read=True, read_at=timezone.now(),
        )

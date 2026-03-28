"""Celery tasks for the notifications app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="notifications.send_due_date_reminders")
def send_due_date_reminders():
    """
    Send in-app + email reminders for loans due within the next 2 days.
    Runs daily (see celery beat schedule in config/celery.py).
    """
    from apps.borrowing.models import Borrowing

    from .services import NotificationService

    window_start = timezone.now()
    window_end = window_start + timedelta(days=2)

    upcoming = Borrowing.objects.filter(
        status=Borrowing.Status.ACTIVE,
        due_date__gte=window_start,
        due_date__lte=window_end,
    ).select_related("user", "book_copy__book")

    count = 0
    for loan in upcoming:
        # Avoid duplicate reminders
        from .models import Notification

        already_sent = Notification.objects.filter(
            user=loan.user,
            notification_type=Notification.NotificationType.DUE_REMINDER,
            metadata__borrowing_id=str(loan.id),
            created_at__gte=window_start - timedelta(days=1),
        ).exists()

        if not already_sent:
            NotificationService.notify_due_reminder(loan.user, loan)
            count += 1

    logger.info("Sent %d due-date reminders", count)
    return {"reminders_sent": count}


@shared_task(name="notifications.send_overdue_notices")
def send_overdue_notices():
    """
    Notify members about newly overdue loans.
    """
    from apps.borrowing.models import Borrowing

    from .services import NotificationService

    overdue_loans = Borrowing.objects.filter(
        status__in=[Borrowing.Status.ACTIVE, Borrowing.Status.OVERDUE],
        due_date__lt=timezone.now(),
    ).select_related("user", "book_copy__book")

    count = 0
    for loan in overdue_loans:
        from django.conf import settings as django_settings

        days_late = (timezone.now() - loan.due_date).days
        daily_rate = getattr(django_settings, "DAILY_FINE_RATE", 0.50)
        max_fine = getattr(django_settings, "MAX_FINE_AMOUNT", 25.00)
        fine = min(days_late * daily_rate, max_fine)

        NotificationService.notify_overdue(loan.user, loan, fine)
        count += 1

    logger.info("Sent %d overdue notices", count)
    return {"overdue_notices": count}


@shared_task(name="notifications.check_membership_expiry")
def check_membership_expiry():
    """
    Warn members whose membership expires within the next 7 days.
    """
    from apps.accounts.models import MemberProfile

    from .services import NotificationService

    expiry_window = timezone.now().date() + timedelta(days=7)
    expiring = MemberProfile.objects.filter(
        is_active=True,
        membership_expiry_date__lte=expiry_window,
        membership_expiry_date__gte=timezone.now().date(),
    ).select_related("user")

    count = 0
    for profile in expiring:
        days_remaining = (profile.membership_expiry_date - timezone.now().date()).days
        NotificationService.notify_membership_expiry(profile.user, days_remaining)
        count += 1

    logger.info("Sent %d membership expiry warnings", count)
    return {"expiry_warnings": count}


@shared_task(name="notifications.cleanup_old_notifications")
def cleanup_old_notifications(days=90):
    """
    Delete read notifications older than N days to keep the table lean.
    """
    from .models import Notification

    cutoff = timezone.now() - timedelta(days=days)
    deleted, _ = Notification.objects.filter(
        is_read=True, created_at__lt=cutoff,
    ).delete()

    logger.info("Cleaned up %d old notifications", deleted)
    return {"deleted": deleted}

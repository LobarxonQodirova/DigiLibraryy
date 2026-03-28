"""Celery tasks for the borrowing app."""

import logging
from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(name="borrowing.check_overdue_loans")
def check_overdue_loans():
    """
    Mark active loans as overdue when past their due date and
    create fines for newly overdue items.
    """
    from .models import Borrowing, Fine

    now = timezone.now()
    newly_overdue = Borrowing.objects.filter(
        status=Borrowing.Status.ACTIVE,
        due_date__lt=now,
    )

    count = 0
    daily_rate = getattr(settings, "DAILY_FINE_RATE", 0.50)
    max_fine = getattr(settings, "MAX_FINE_AMOUNT", 25.00)

    for loan in newly_overdue:
        loan.status = Borrowing.Status.OVERDUE
        loan.save(update_fields=["status", "updated_at"])

        days_late = (now - loan.due_date).days
        fine_amount = min(days_late * daily_rate, max_fine)

        # Only create a new fine if one doesn't already exist for this loan
        if not Fine.objects.filter(borrowing=loan, reason=Fine.Reason.OVERDUE).exists():
            Fine.objects.create(
                user=loan.user,
                borrowing=loan,
                amount=fine_amount,
                reason=Fine.Reason.OVERDUE,
                description=f"Overdue: {days_late} day(s) past due date",
            )
        count += 1

    logger.info("Checked overdue loans: %d loans marked overdue", count)
    return {"overdue_count": count}


@shared_task(name="borrowing.send_due_date_reminders")
def send_due_date_reminders():
    """
    Send email reminders to members whose books are due within the next 2 days.
    """
    from django.core.mail import send_mail

    from .models import Borrowing

    reminder_window = timezone.now() + timedelta(days=2)
    upcoming = Borrowing.objects.filter(
        status=Borrowing.Status.ACTIVE,
        due_date__lte=reminder_window,
        due_date__gte=timezone.now(),
    ).select_related("user", "book_copy__book")

    count = 0
    for loan in upcoming:
        try:
            send_mail(
                subject=f"Library Reminder: '{loan.book_copy.book.title}' is due soon",
                message=(
                    f"Dear {loan.user.get_full_name()},\n\n"
                    f"This is a reminder that '{loan.book_copy.book.title}' "
                    f"is due on {loan.due_date.strftime('%B %d, %Y')}.\n\n"
                    f"You can renew online or return it to the library.\n\n"
                    f"Thank you,\nDigiLibrary"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[loan.user.email],
                fail_silently=True,
            )
            count += 1
        except Exception as exc:
            logger.error("Failed to send reminder for loan %s: %s", loan.id, exc)

    logger.info("Sent %d due-date reminders", count)
    return {"reminders_sent": count}


@shared_task(name="borrowing.process_reservation_queue")
def process_reservation_queue():
    """
    When a reserved book copy becomes available, notify the next
    member in the queue.
    """
    from django.core.mail import send_mail

    from apps.books.models import BookCopy

    from .models import Reservation

    pending = (
        Reservation.objects.filter(status=Reservation.Status.PENDING, notification_sent=False)
        .select_related("user", "book")
        .order_by("queue_position")
    )

    processed = 0
    for reservation in pending:
        available_copy = (
            BookCopy.objects.filter(
                book=reservation.book, status=BookCopy.Status.AVAILABLE
            ).first()
        )
        if available_copy:
            reservation.book_copy = available_copy
            reservation.status = Reservation.Status.READY
            reservation.pickup_by_date = timezone.now() + timedelta(days=3)
            reservation.notification_sent = True
            reservation.save()

            available_copy.status = BookCopy.Status.ON_HOLD
            available_copy.save(update_fields=["status", "updated_at"])

            send_mail(
                subject=f"Your reserved book '{reservation.book.title}' is ready!",
                message=(
                    f"Dear {reservation.user.get_full_name()},\n\n"
                    f"'{reservation.book.title}' is now available for pickup.\n"
                    f"Please collect it by {reservation.pickup_by_date.strftime('%B %d, %Y')}.\n\n"
                    f"Thank you,\nDigiLibrary"
                ),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reservation.user.email],
                fail_silently=True,
            )
            processed += 1

    logger.info("Processed reservation queue: %d reservations ready", processed)
    return {"reservations_ready": processed}


@shared_task(name="borrowing.expire_uncollected_reservations")
def expire_uncollected_reservations():
    """
    Expire reservations that were not picked up by the deadline.
    """
    from apps.books.models import BookCopy

    from .models import Reservation

    now = timezone.now()
    expired = Reservation.objects.filter(
        status=Reservation.Status.READY,
        pickup_by_date__lt=now,
    )

    count = 0
    for reservation in expired:
        reservation.status = Reservation.Status.EXPIRED
        reservation.save(update_fields=["status", "updated_at"])

        # Release the held copy
        if reservation.book_copy:
            reservation.book_copy.status = BookCopy.Status.AVAILABLE
            reservation.book_copy.save(update_fields=["status", "updated_at"])
        count += 1

    logger.info("Expired %d uncollected reservations", count)
    return {"expired_count": count}

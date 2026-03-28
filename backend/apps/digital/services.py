"""Business logic services for the digital app."""

import logging
from datetime import timedelta

from django.conf import settings
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)


class DigitalLendingService:
    """
    Encapsulates e-book lending business logic:
    - License availability checks
    - Loan creation with expiry
    - Returns and license release
    - Concurrent loan limits
    """

    def borrow_ebook(self, user, ebook, request=None):
        """
        Borrow an e-book for the authenticated user.

        Raises ValueError on business-rule violations.
        Returns a Download instance on success.
        """
        from .models import Download, ReadingProgress

        # 1. Check license availability
        if not ebook.is_available:
            raise ValueError("No licenses currently available for this e-book.")

        # 2. Check member digital loan limit
        max_digital = getattr(settings, "MAX_CONCURRENT_DIGITAL_LOANS", 5)
        active_digital_loans = Download.objects.filter(
            user=user, ebook__isnull=False, is_active=True,
        ).count()
        if active_digital_loans >= max_digital:
            raise ValueError(
                f"You have reached the maximum of {max_digital} concurrent digital loans."
            )

        # 3. Check if user already has this e-book on loan
        existing = Download.objects.filter(
            user=user, ebook=ebook, is_active=True,
        ).exists()
        if existing:
            raise ValueError("You already have an active loan for this e-book.")

        # 4. Create the loan
        loan_days = getattr(settings, "EBOOK_LOAN_DAYS", 21)
        with transaction.atomic():
            download = Download.objects.create(
                user=user,
                ebook=ebook,
                expires_at=timezone.now() + timedelta(days=loan_days),
                ip_address=request.META.get("REMOTE_ADDR") if request else None,
                user_agent=(request.META.get("HTTP_USER_AGENT", "")[:500]) if request else "",
                is_active=True,
            )
            ebook.active_loans += 1
            ebook.save(update_fields=["active_loans", "updated_at"])

            # Initialize reading progress
            ReadingProgress.objects.get_or_create(
                user=user,
                ebook=ebook,
                defaults={"total_pages": ebook.book.page_count or 0},
            )

        logger.info(
            "E-book borrowed: user=%s ebook=%s expires=%s",
            user.email, ebook.id, download.expires_at,
        )
        return download

    def return_ebook(self, user, download_id):
        """
        Return a borrowed e-book and release the license.

        Raises ValueError on business-rule violations.
        """
        from .models import Download

        try:
            download = Download.objects.get(
                id=download_id, user=user, is_active=True,
            )
        except Download.DoesNotExist:
            raise ValueError("Active loan not found.")

        with transaction.atomic():
            download.is_active = False
            download.save(update_fields=["is_active"])

            if download.ebook:
                ebook = download.ebook
                ebook.active_loans = max(0, ebook.active_loans - 1)
                ebook.save(update_fields=["active_loans", "updated_at"])

        logger.info(
            "E-book returned: user=%s ebook=%s",
            user.email, download.ebook_id,
        )

    def expire_loans(self):
        """
        Expire all digital loans past their expiry date.
        Called by a Celery periodic task.
        """
        from .models import Download

        now = timezone.now()
        expired = Download.objects.filter(
            is_active=True, expires_at__lt=now,
        ).select_related("ebook")

        count = 0
        for download in expired:
            with transaction.atomic():
                download.is_active = False
                download.save(update_fields=["is_active"])

                if download.ebook:
                    ebook = download.ebook
                    ebook.active_loans = max(0, ebook.active_loans - 1)
                    ebook.save(update_fields=["active_loans", "updated_at"])
                count += 1

        logger.info("Expired %d digital loans", count)
        return count

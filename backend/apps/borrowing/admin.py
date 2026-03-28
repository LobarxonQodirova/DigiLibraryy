"""Admin configuration for the borrowing app."""

from django.contrib import admin

from .models import Borrowing, BorrowingHistory, Fine, Reservation, ReturnRecord


@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = (
        "user", "get_book_title", "checkout_date", "due_date",
        "return_date", "status", "renewals_count",
    )
    list_filter = ("status", "checkout_date", "due_date")
    search_fields = ("user__email", "book_copy__book__title", "book_copy__barcode")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user", "book_copy", "checked_out_by")

    def get_book_title(self, obj):
        return obj.book_copy.book.title
    get_book_title.short_description = "Book"


@admin.register(ReturnRecord)
class ReturnRecordAdmin(admin.ModelAdmin):
    list_display = (
        "get_book", "returned_date", "condition_on_return",
        "fine_assessed", "processed_by",
    )
    list_filter = ("condition_on_return", "returned_date")
    readonly_fields = ("id", "created_at")

    def get_book(self, obj):
        return obj.borrowing.book_copy.book.title
    get_book.short_description = "Book"


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        "user", "book", "status", "queue_position",
        "reservation_date", "pickup_by_date", "notification_sent",
    )
    list_filter = ("status", "notification_sent")
    search_fields = ("user__email", "book__title")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(BorrowingHistory)
class BorrowingHistoryAdmin(admin.ModelAdmin):
    list_display = (
        "user", "book", "checkout_date", "return_date",
        "was_overdue", "fine_amount", "rating",
    )
    list_filter = ("was_overdue", "checkout_date")
    search_fields = ("user__email", "book__title")
    readonly_fields = ("id", "created_at")


@admin.register(Fine)
class FineAdmin(admin.ModelAdmin):
    list_display = (
        "user", "amount", "amount_paid", "reason",
        "status", "issued_date", "paid_date",
    )
    list_filter = ("status", "reason", "issued_date")
    search_fields = ("user__email",)
    readonly_fields = ("id", "created_at", "updated_at")

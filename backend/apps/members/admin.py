"""Admin configuration for the members app."""

from django.contrib import admin

from .models import MembershipCard, ReadingList, ReadingListItem


@admin.register(MembershipCard)
class MembershipCardAdmin(admin.ModelAdmin):
    list_display = (
        "card_number", "user", "card_type", "status",
        "issued_date", "expiry_date",
    )
    list_filter = ("card_type", "status")
    search_fields = ("card_number", "barcode", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")


class ReadingListItemInline(admin.TabularInline):
    model = ReadingListItem
    extra = 0
    readonly_fields = ("id", "date_added")
    raw_id_fields = ("book",)


@admin.register(ReadingList)
class ReadingListAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "is_public", "book_count", "created_at")
    list_filter = ("is_public",)
    search_fields = ("name", "user__email")
    readonly_fields = ("id", "created_at", "updated_at")
    inlines = [ReadingListItemInline]

    def book_count(self, obj):
        return obj.items.count()
    book_count.short_description = "Books"

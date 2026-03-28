"""Admin configuration for the accounts app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import LibrarianProfile, MemberProfile, MembershipType

User = get_user_model()


class MemberProfileInline(admin.StackedInline):
    model = MemberProfile
    can_delete = False
    verbose_name_plural = "Member Profile"
    readonly_fields = ("library_card_number", "created_at", "updated_at")
    extra = 0


class LibrarianProfileInline(admin.StackedInline):
    model = LibrarianProfile
    can_delete = False
    verbose_name_plural = "Librarian Profile"
    readonly_fields = ("created_at", "updated_at")
    extra = 0


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "email", "username", "first_name", "last_name",
        "role", "is_active", "date_joined",
    )
    list_filter = ("role", "is_active", "is_staff", "date_joined")
    search_fields = ("email", "username", "first_name", "last_name")
    ordering = ("-created_at",)
    inlines = [MemberProfileInline, LibrarianProfileInline]

    fieldsets = BaseUserAdmin.fieldsets + (
        ("Library Info", {
            "fields": ("role", "phone", "date_of_birth", "address", "city", "state", "zip_code", "profile_picture"),
        }),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Library Info", {
            "fields": ("email", "first_name", "last_name", "role", "phone"),
        }),
    )


@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = (
        "name", "max_loans", "max_reservations", "loan_period_days",
        "max_renewals", "annual_fee", "is_active",
    )
    list_filter = ("is_active",)
    search_fields = ("name",)


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "library_card_number", "membership_type",
        "membership_start_date", "membership_expiry_date",
        "is_active", "total_fines_owed",
    )
    list_filter = ("is_active", "membership_type")
    search_fields = ("user__email", "user__first_name", "library_card_number")
    readonly_fields = ("library_card_number", "created_at", "updated_at")


@admin.register(LibrarianProfile)
class LibrarianProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user", "employee_id", "department", "position", "hire_date",
    )
    list_filter = ("department",)
    search_fields = ("user__email", "employee_id")
    readonly_fields = ("created_at", "updated_at")

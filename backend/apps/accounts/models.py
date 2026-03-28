"""User and membership models for the DigiLibrary system."""

import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""

    class Role(models.TextChoices):
        ADMIN = "admin", "Administrator"
        LIBRARIAN = "librarian", "Librarian"
        MEMBER = "member", "Member"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField("Email Address", unique=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[RegexValidator(r"^\+?1?\d{9,15}$", "Enter a valid phone number.")],
    )
    date_of_birth = models.DateField(null=True, blank=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    profile_picture = models.ImageField(upload_to="profiles/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    @property
    def is_librarian(self):
        return self.role in (self.Role.LIBRARIAN, self.Role.ADMIN)

    @property
    def is_admin_user(self):
        return self.role == self.Role.ADMIN


class MembershipType(models.Model):
    """Defines different membership tiers with their privileges."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    max_loans = models.PositiveIntegerField(default=5, help_text="Maximum simultaneous loans")
    max_reservations = models.PositiveIntegerField(default=3, help_text="Maximum simultaneous reservations")
    loan_period_days = models.PositiveIntegerField(default=14, help_text="Default loan period in days")
    max_renewals = models.PositiveIntegerField(default=2, help_text="Maximum renewals per loan")
    max_digital_loans = models.PositiveIntegerField(default=3, help_text="Maximum simultaneous e-book loans")
    can_use_reading_rooms = models.BooleanField(default=True)
    can_request_ill = models.BooleanField(default=False, help_text="Can request inter-library loans")
    annual_fee = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["annual_fee"]
        verbose_name = "Membership Type"
        verbose_name_plural = "Membership Types"

    def __str__(self):
        return self.name


class MemberProfile(models.Model):
    """Extended profile for library members."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )
    membership_type = models.ForeignKey(
        MembershipType,
        on_delete=models.PROTECT,
        related_name="members",
    )
    library_card_number = models.CharField(max_length=20, unique=True, editable=False)
    membership_start_date = models.DateField(default=timezone.now)
    membership_expiry_date = models.DateField()
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True, help_text="Internal notes about the member")
    emergency_contact_name = models.CharField(max_length=200, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    total_fines_owed = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Member Profile"
        verbose_name_plural = "Member Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.library_card_number}"

    def save(self, *args, **kwargs):
        if not self.library_card_number:
            self.library_card_number = self._generate_card_number()
        super().save(*args, **kwargs)

    def _generate_card_number(self):
        """Generate a unique library card number."""
        prefix = "DL"
        last_profile = (
            MemberProfile.objects.filter(library_card_number__startswith=prefix)
            .order_by("-library_card_number")
            .first()
        )
        if last_profile:
            try:
                last_num = int(last_profile.library_card_number[len(prefix):])
                new_num = last_num + 1
            except ValueError:
                new_num = 1
        else:
            new_num = 1
        return f"{prefix}{new_num:08d}"

    @property
    def is_membership_active(self):
        return self.is_active and self.membership_expiry_date >= timezone.now().date()

    @property
    def active_loans_count(self):
        return self.user.loans.filter(status="active").count()

    @property
    def can_borrow(self):
        return (
            self.is_membership_active
            and self.active_loans_count < self.membership_type.max_loans
            and self.total_fines_owed <= 0
        )


class LibrarianProfile(models.Model):
    """Extended profile for library staff."""

    class Department(models.TextChoices):
        CIRCULATION = "circulation", "Circulation"
        REFERENCE = "reference", "Reference"
        CATALOGING = "cataloging", "Cataloging"
        DIGITAL = "digital", "Digital Services"
        ADMINISTRATION = "administration", "Administration"
        CHILDREN = "children", "Children's Services"
        ACQUISITIONS = "acquisitions", "Acquisitions"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="librarian_profile",
    )
    employee_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(
        max_length=30,
        choices=Department.choices,
        default=Department.CIRCULATION,
    )
    position = models.CharField(max_length=100)
    hire_date = models.DateField()
    can_manage_catalog = models.BooleanField(default=False)
    can_manage_members = models.BooleanField(default=True)
    can_manage_fines = models.BooleanField(default=True)
    can_manage_ill = models.BooleanField(default=False)
    can_view_analytics = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Librarian Profile"
        verbose_name_plural = "Librarian Profiles"

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.employee_id}"

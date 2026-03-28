"""Serializers for the accounts app."""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import LibrarianProfile, MemberProfile, MembershipType

User = get_user_model()


class MembershipTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipType
        fields = [
            "id", "name", "description", "max_loans", "max_reservations",
            "loan_period_days", "max_renewals", "max_digital_loans",
            "can_use_reading_rooms", "can_request_ill", "annual_fee", "is_active",
        ]
        read_only_fields = ["id"]


class MemberProfileSerializer(serializers.ModelSerializer):
    membership_type_name = serializers.CharField(
        source="membership_type.name", read_only=True
    )
    is_membership_active = serializers.BooleanField(read_only=True)
    can_borrow = serializers.BooleanField(read_only=True)
    active_loans_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = MemberProfile
        fields = [
            "id", "library_card_number", "membership_type", "membership_type_name",
            "membership_start_date", "membership_expiry_date", "is_active",
            "is_membership_active", "can_borrow", "active_loans_count",
            "total_fines_owed", "emergency_contact_name", "emergency_contact_phone",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "library_card_number", "total_fines_owed", "created_at", "updated_at",
        ]


class LibrarianProfileSerializer(serializers.ModelSerializer):
    department_display = serializers.CharField(
        source="get_department_display", read_only=True
    )

    class Meta:
        model = LibrarianProfile
        fields = [
            "id", "employee_id", "department", "department_display", "position",
            "hire_date", "can_manage_catalog", "can_manage_members",
            "can_manage_fines", "can_manage_ill", "can_view_analytics",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    member_profile = MemberProfileSerializer(read_only=True)
    librarian_profile = LibrarianProfileSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "username", "first_name", "last_name", "full_name",
            "role", "phone", "date_of_birth", "address", "city", "state",
            "zip_code", "profile_picture", "is_active", "date_joined",
            "member_profile", "librarian_profile",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {
            "email": {"required": True},
        }

    def get_full_name(self, obj):
        return obj.get_full_name()


class UserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    full_name = serializers.SerializerMethodField()
    library_card = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "email", "full_name", "role", "phone",
            "is_active", "date_joined", "library_card",
        ]

    def get_full_name(self, obj):
        return obj.get_full_name()

    def get_library_card(self, obj):
        if hasattr(obj, "member_profile"):
            return obj.member_profile.library_card_number
        return None


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for member registration."""

    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password_confirm = serializers.CharField(write_only=True, required=True)
    membership_type = serializers.PrimaryKeyRelatedField(
        queryset=MembershipType.objects.filter(is_active=True),
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "email", "username", "password", "password_confirm",
            "first_name", "last_name", "phone", "date_of_birth",
            "address", "city", "state", "zip_code", "membership_type",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": "Passwords do not match."}
            )
        return attrs

    def create(self, validated_data):
        membership_type = validated_data.pop("membership_type", None)
        password = validated_data.pop("password")

        user = User.objects.create_user(**validated_data, role=User.Role.MEMBER)
        user.set_password(password)
        user.save()

        if membership_type is None:
            membership_type = MembershipType.objects.filter(is_active=True).order_by("annual_fee").first()

        if membership_type:
            from django.utils import timezone
            from dateutil.relativedelta import relativedelta

            MemberProfile.objects.create(
                user=user,
                membership_type=membership_type,
                membership_start_date=timezone.now().date(),
                membership_expiry_date=timezone.now().date() + relativedelta(years=1),
            )

        return user


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone", "date_of_birth",
            "address", "city", "state", "zip_code", "profile_picture",
        ]

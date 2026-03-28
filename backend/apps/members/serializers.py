"""Serializers for the members app."""

from rest_framework import serializers

from apps.books.serializers import BookListSerializer

from .models import MembershipCard, ReadingList, ReadingListItem


class MembershipCardSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    card_type_display = serializers.CharField(source="get_card_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = MembershipCard
        fields = [
            "id", "user", "user_name", "card_number", "card_type",
            "card_type_display", "status", "status_display",
            "issued_date", "expiry_date", "barcode", "qr_code",
            "is_valid", "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "barcode", "created_at", "updated_at"]


class ReadingListItemSerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source="book", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ReadingListItem
        fields = [
            "id", "reading_list", "book", "book_detail",
            "status", "status_display", "priority",
            "personal_notes", "date_added", "date_started", "date_finished",
        ]
        read_only_fields = ["id", "date_added"]


class ReadingListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.get_full_name", read_only=True)
    book_count = serializers.IntegerField(read_only=True)
    items = ReadingListItemSerializer(many=True, read_only=True)

    class Meta:
        model = ReadingList
        fields = [
            "id", "user", "user_name", "name", "description",
            "is_public", "book_count", "items",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]


class ReadingListCreateSerializer(serializers.ModelSerializer):
    """Lightweight serializer for creating / updating reading lists."""

    class Meta:
        model = ReadingList
        fields = ["name", "description", "is_public"]

    def validate_name(self, value):
        user = self.context["request"].user
        qs = ReadingList.objects.filter(user=user, name=value)
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("You already have a reading list with this name.")
        return value

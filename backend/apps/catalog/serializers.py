"""Serializers for the catalog app."""

from rest_framework import serializers

from apps.books.serializers import BookListSerializer

from .models import Catalog, CatalogEntry, Classification


class ClassificationSerializer(serializers.ModelSerializer):
    scheme_display = serializers.CharField(source="get_scheme_display", read_only=True)
    children = serializers.SerializerMethodField()

    class Meta:
        model = Classification
        fields = [
            "id", "scheme", "scheme_display", "code", "name",
            "description", "parent", "level", "children", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_children(self, obj):
        children = obj.children.all()
        if children.exists():
            return ClassificationSerializer(children, many=True).data
        return []


class CatalogSerializer(serializers.ModelSerializer):
    entry_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Catalog
        fields = [
            "id", "name", "description", "is_public", "is_active",
            "location", "entry_count", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class CatalogEntrySerializer(serializers.ModelSerializer):
    book_detail = BookListSerializer(source="book", read_only=True)
    catalog_name = serializers.CharField(source="catalog.name", read_only=True)
    classification_display = serializers.SerializerMethodField()

    class Meta:
        model = CatalogEntry
        fields = [
            "id", "catalog", "catalog_name", "book", "book_detail",
            "classification", "classification_display",
            "call_number", "date_added", "notes",
        ]
        read_only_fields = ["id", "date_added"]

    def get_classification_display(self, obj):
        if obj.classification:
            return f"{obj.classification.code} - {obj.classification.name}"
        return None


class CatalogEntryCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating / updating catalog entries."""

    class Meta:
        model = CatalogEntry
        fields = ["catalog", "book", "classification", "call_number", "notes"]

    def validate(self, attrs):
        catalog = attrs.get("catalog")
        book = attrs.get("book")
        if CatalogEntry.objects.filter(catalog=catalog, book=book).exists():
            if not self.instance:
                raise serializers.ValidationError(
                    "This book is already in the selected catalog."
                )
        return attrs

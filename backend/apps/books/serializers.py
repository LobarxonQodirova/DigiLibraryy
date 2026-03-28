"""Serializers for the books app."""

from rest_framework import serializers

from .models import Author, Book, BookCopy, BookEdition, Genre, ISBN, Publisher


class GenreSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = ["id", "name", "slug", "description", "parent", "children"]
        read_only_fields = ["id"]

    def get_children(self, obj):
        children = obj.children.all()
        return GenreSerializer(children, many=True).data if children.exists() else []


class AuthorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            "id", "first_name", "last_name", "full_name", "biography",
            "date_of_birth", "date_of_death", "website", "photo",
            "books_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_books_count(self, obj):
        return obj.books.count()


class AuthorListSerializer(serializers.ModelSerializer):
    """Lightweight author serializer for nested use."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "full_name"]


class PublisherSerializer(serializers.ModelSerializer):
    books_count = serializers.SerializerMethodField()

    class Meta:
        model = Publisher
        fields = [
            "id", "name", "address", "city", "country",
            "website", "email", "books_count", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def get_books_count(self, obj):
        return obj.books.count()


class ISBNSerializer(serializers.ModelSerializer):
    class Meta:
        model = ISBN
        fields = ["id", "isbn_10", "isbn_13"]
        read_only_fields = ["id"]


class BookCopySerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    condition_display = serializers.CharField(source="get_condition_display", read_only=True)
    is_available = serializers.BooleanField(read_only=True)

    class Meta:
        model = BookCopy
        fields = [
            "id", "book", "barcode", "status", "status_display",
            "condition", "condition_display", "shelf_location",
            "acquisition_date", "acquisition_price", "is_available",
            "notes", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class BookEditionSerializer(serializers.ModelSerializer):
    isbn_detail = ISBNSerializer(source="isbn", read_only=True)

    class Meta:
        model = BookEdition
        fields = [
            "id", "book", "edition_number", "publication_date",
            "isbn", "isbn_detail", "format", "page_count", "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class BookSerializer(serializers.ModelSerializer):
    authors_detail = AuthorListSerializer(source="authors", many=True, read_only=True)
    publisher_name = serializers.CharField(source="publisher.name", read_only=True)
    genres_detail = GenreSerializer(source="genres", many=True, read_only=True)
    isbn_detail = ISBNSerializer(source="isbn", read_only=True)
    available_copies_count = serializers.IntegerField(read_only=True)
    total_copies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "subtitle", "authors", "authors_detail",
            "publisher", "publisher_name", "genres", "genres_detail",
            "isbn", "isbn_detail", "publication_date", "language",
            "page_count", "description", "cover_image",
            "table_of_contents", "average_rating", "total_ratings",
            "available_copies_count", "total_copies_count",
            "is_active", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "average_rating", "total_ratings", "created_at", "updated_at",
        ]


class BookListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/search endpoints."""

    authors_detail = AuthorListSerializer(source="authors", many=True, read_only=True)
    available_copies_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Book
        fields = [
            "id", "title", "authors_detail", "cover_image",
            "publication_date", "language", "average_rating",
            "available_copies_count", "is_active",
        ]

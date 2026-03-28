"""Admin configuration for the books app."""

from django.contrib import admin

from .models import Author, Book, BookCopy, BookEdition, Genre, ISBN, Publisher


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "parent")
    list_filter = ("parent",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "date_of_birth", "date_of_death")
    search_fields = ("first_name", "last_name")
    list_filter = ("date_of_birth",)


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "website")
    search_fields = ("name",)


@admin.register(ISBN)
class ISBNAdmin(admin.ModelAdmin):
    list_display = ("isbn_13", "isbn_10")
    search_fields = ("isbn_13", "isbn_10")


class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 0
    readonly_fields = ("id", "created_at")
    fields = ("barcode", "status", "condition", "shelf_location", "created_at")


class BookEditionInline(admin.TabularInline):
    model = BookEdition
    extra = 0
    readonly_fields = ("id", "created_at")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = (
        "title", "get_authors", "publisher", "publication_date",
        "language", "average_rating", "is_active",
    )
    list_filter = ("language", "is_active", "genres")
    search_fields = ("title", "subtitle", "authors__last_name", "isbn__isbn_13")
    filter_horizontal = ("authors", "genres")
    inlines = [BookCopyInline, BookEditionInline]
    readonly_fields = ("average_rating", "total_ratings", "created_at", "updated_at")

    def get_authors(self, obj):
        return ", ".join(str(a) for a in obj.authors.all()[:3])
    get_authors.short_description = "Authors"


@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ("barcode", "book", "status", "condition", "shelf_location")
    list_filter = ("status", "condition")
    search_fields = ("barcode", "book__title")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(BookEdition)
class BookEditionAdmin(admin.ModelAdmin):
    list_display = ("book", "edition_number", "format", "publication_date")
    list_filter = ("format",)
    search_fields = ("book__title",)

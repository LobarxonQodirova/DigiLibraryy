"""Models for the books app -- Book, Author, Publisher, Genre, ISBN, BookCopy, BookEdition."""

import uuid

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models
from django.utils import timezone


class Genre(models.Model):
    """Library genre / subject classification."""

    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="children",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Genres"

    def __str__(self):
        return self.name


class Author(models.Model):
    """Book author."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    biography = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    website = models.URLField(blank=True)
    photo = models.ImageField(upload_to="authors/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Publisher(models.Model):
    """Book publisher."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    website = models.URLField(blank=True)
    email = models.EmailField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ISBN(models.Model):
    """ISBN record -- supports both ISBN-10 and ISBN-13."""

    isbn_10 = models.CharField(
        max_length=10, unique=True, blank=True, null=True,
        validators=[RegexValidator(r"^\d{9}[\dXx]$", "Enter a valid ISBN-10.")],
    )
    isbn_13 = models.CharField(
        max_length=13, unique=True, blank=True, null=True,
        validators=[RegexValidator(r"^(978|979)\d{10}$", "Enter a valid ISBN-13.")],
    )

    class Meta:
        verbose_name = "ISBN"
        verbose_name_plural = "ISBNs"

    def __str__(self):
        return self.isbn_13 or self.isbn_10 or "No ISBN"


class Book(models.Model):
    """Core book record in the library catalog."""

    class Language(models.TextChoices):
        ENGLISH = "en", "English"
        SPANISH = "es", "Spanish"
        FRENCH = "fr", "French"
        GERMAN = "de", "German"
        CHINESE = "zh", "Chinese"
        ARABIC = "ar", "Arabic"
        OTHER = "other", "Other"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300, db_index=True)
    subtitle = models.CharField(max_length=300, blank=True)
    authors = models.ManyToManyField(Author, related_name="books")
    publisher = models.ForeignKey(
        Publisher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="books",
    )
    genres = models.ManyToManyField(Genre, related_name="books", blank=True)
    isbn = models.OneToOneField(
        ISBN, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="book",
    )
    publication_date = models.DateField(null=True, blank=True)
    language = models.CharField(
        max_length=10, choices=Language.choices, default=Language.ENGLISH,
    )
    page_count = models.PositiveIntegerField(null=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="covers/", null=True, blank=True)
    table_of_contents = models.TextField(blank=True)
    average_rating = models.DecimalField(
        max_digits=3, decimal_places=2, default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    total_ratings = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["title"]
        indexes = [
            models.Index(fields=["title"]),
            models.Index(fields=["publication_date"]),
        ]

    def __str__(self):
        return self.title

    @property
    def available_copies_count(self):
        return self.copies.filter(status=BookCopy.Status.AVAILABLE).count()

    @property
    def total_copies_count(self):
        return self.copies.count()


class BookEdition(models.Model):
    """Tracks different editions of the same work."""

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="editions")
    edition_number = models.PositiveIntegerField(default=1)
    publication_date = models.DateField(null=True, blank=True)
    isbn = models.OneToOneField(
        ISBN, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="edition",
    )
    format = models.CharField(
        max_length=20,
        choices=[
            ("hardcover", "Hardcover"),
            ("paperback", "Paperback"),
            ("ebook", "E-Book"),
            ("audiobook", "Audiobook"),
        ],
        default="paperback",
    )
    page_count = models.PositiveIntegerField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-edition_number"]
        unique_together = ("book", "edition_number")

    def __str__(self):
        return f"{self.book.title} (Edition {self.edition_number})"


class BookCopy(models.Model):
    """Physical copy of a book held in the library."""

    class Status(models.TextChoices):
        AVAILABLE = "available", "Available"
        CHECKED_OUT = "checked_out", "Checked Out"
        ON_HOLD = "on_hold", "On Hold"
        IN_REPAIR = "in_repair", "In Repair"
        LOST = "lost", "Lost"
        RETIRED = "retired", "Retired"

    class Condition(models.TextChoices):
        NEW = "new", "New"
        GOOD = "good", "Good"
        FAIR = "fair", "Fair"
        POOR = "poor", "Poor"
        DAMAGED = "damaged", "Damaged"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="copies")
    barcode = models.CharField(max_length=50, unique=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.AVAILABLE,
    )
    condition = models.CharField(
        max_length=20, choices=Condition.choices, default=Condition.NEW,
    )
    shelf_location = models.CharField(max_length=50, blank=True, help_text="e.g. A3-R2-S5")
    acquisition_date = models.DateField(default=timezone.now)
    acquisition_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["barcode"]
        verbose_name_plural = "Book Copies"

    def __str__(self):
        return f"{self.book.title} [{self.barcode}]"

    @property
    def is_available(self):
        return self.status == self.Status.AVAILABLE

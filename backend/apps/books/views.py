"""Views for the books app."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsLibrarianOrAdmin, ReadOnly

from .models import Author, Book, BookCopy, BookEdition, Genre, Publisher
from .serializers import (
    AuthorSerializer,
    BookCopySerializer,
    BookEditionSerializer,
    BookListSerializer,
    BookSerializer,
    GenreSerializer,
    PublisherSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    """CRUD for book genres / subject classifications."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = "slug"
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]


class AuthorViewSet(viewsets.ModelViewSet):
    """CRUD for authors."""

    queryset = Author.objects.prefetch_related("books").all()
    serializer_class = AuthorSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name"]
    ordering_fields = ["last_name", "created_at"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        """List all books by this author."""
        author = self.get_object()
        books = author.books.filter(is_active=True)
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)


class PublisherViewSet(viewsets.ModelViewSet):
    """CRUD for publishers."""

    queryset = Publisher.objects.all()
    serializer_class = PublisherSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]


class BookViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for books.
    - Public:   list, retrieve
    - Staff:    create, update, destroy
    """

    queryset = (
        Book.objects.select_related("publisher", "isbn")
        .prefetch_related("authors", "genres", "copies")
        .filter(is_active=True)
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["language", "genres__slug", "publisher"]
    search_fields = ["title", "subtitle", "authors__last_name", "isbn__isbn_13"]
    ordering_fields = ["title", "publication_date", "average_rating", "created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    @action(detail=True, methods=["get"])
    def copies(self, request, pk=None):
        """List all physical copies of this book."""
        book = self.get_object()
        copies = book.copies.all()
        serializer = BookCopySerializer(copies, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def editions(self, request, pk=None):
        """List all editions of this book."""
        book = self.get_object()
        editions = book.editions.all()
        serializer = BookEditionSerializer(editions, many=True)
        return Response(serializer.data)


class BookCopyViewSet(viewsets.ModelViewSet):
    """Manage physical copies (barcoded items)."""

    queryset = BookCopy.objects.select_related("book").all()
    serializer_class = BookCopySerializer
    permission_classes = [permissions.IsAuthenticated, IsLibrarianOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["status", "condition", "book"]
    search_fields = ["barcode", "book__title"]

    @action(detail=True, methods=["post"], url_path="update-status")
    def update_status(self, request, pk=None):
        """Quick status update for a copy (e.g. mark as lost, in repair)."""
        copy = self.get_object()
        new_status = request.data.get("status")
        if new_status not in dict(BookCopy.Status.choices):
            return Response(
                {"error": f"Invalid status. Choose from: {list(dict(BookCopy.Status.choices).keys())}"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        copy.status = new_status
        copy.save(update_fields=["status", "updated_at"])
        return Response(BookCopySerializer(copy).data)


class BookEditionViewSet(viewsets.ModelViewSet):
    """Manage book editions."""

    queryset = BookEdition.objects.select_related("book", "isbn").all()
    serializer_class = BookEditionSerializer
    permission_classes = [permissions.IsAuthenticated, IsLibrarianOrAdmin]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["book", "format"]

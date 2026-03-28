"""Views for the catalog app."""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.accounts.permissions import IsLibrarianOrAdmin

from .models import Catalog, CatalogEntry, Classification
from .serializers import (
    CatalogEntryCreateSerializer,
    CatalogEntrySerializer,
    CatalogSerializer,
    ClassificationSerializer,
)


class ClassificationViewSet(viewsets.ModelViewSet):
    """Manage classification scheme entries."""

    queryset = Classification.objects.select_related("parent").all()
    serializer_class = ClassificationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["scheme", "level", "parent"]
    search_fields = ["code", "name"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    @action(detail=False, methods=["get"], url_path="tree")
    def tree(self, request):
        """Return the full classification tree (top-level entries only)."""
        roots = self.queryset.filter(parent__isnull=True)
        serializer = self.get_serializer(roots, many=True)
        return Response(serializer.data)


class CatalogViewSet(viewsets.ModelViewSet):
    """Manage library catalogs."""

    queryset = Catalog.objects.all()
    serializer_class = CatalogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "location"]

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsLibrarianOrAdmin()]

    def get_queryset(self):
        qs = super().get_queryset()
        if not self.request.user.is_authenticated or self.request.user.role == "member":
            qs = qs.filter(is_public=True, is_active=True)
        return qs

    @action(detail=True, methods=["get"])
    def entries(self, request, pk=None):
        """List all entries in this catalog."""
        catalog = self.get_object()
        entries = catalog.entries.select_related("book", "classification").all()
        serializer = CatalogEntrySerializer(entries, many=True)
        return Response(serializer.data)


class CatalogEntryViewSet(viewsets.ModelViewSet):
    """Manage individual catalog entries (book-to-catalog mappings)."""

    queryset = CatalogEntry.objects.select_related(
        "catalog", "book", "classification"
    ).all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["catalog", "classification"]
    search_fields = ["book__title", "call_number"]
    permission_classes = [permissions.IsAuthenticated, IsLibrarianOrAdmin]

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return CatalogEntryCreateSerializer
        return CatalogEntrySerializer

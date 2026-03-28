"""URL configuration for the catalog app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "catalog"

router = DefaultRouter()
router.register(r"classifications", views.ClassificationViewSet, basename="classification")
router.register(r"catalogs", views.CatalogViewSet, basename="catalog")
router.register(r"entries", views.CatalogEntryViewSet, basename="catalogentry")

urlpatterns = [
    path("", include(router.urls)),
]

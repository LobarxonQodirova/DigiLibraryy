"""URL configuration for the digital app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "digital"

router = DefaultRouter()
router.register(r"resources", views.DigitalResourceViewSet, basename="digitalresource")
router.register(r"ebooks", views.EBookViewSet, basename="ebook")
router.register(r"progress", views.ReadingProgressViewSet, basename="readingprogress")

urlpatterns = [
    path("", include(router.urls)),
]

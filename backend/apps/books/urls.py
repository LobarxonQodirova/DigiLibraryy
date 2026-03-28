"""URL configuration for the books app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "books"

router = DefaultRouter()
router.register(r"genres", views.GenreViewSet, basename="genre")
router.register(r"authors", views.AuthorViewSet, basename="author")
router.register(r"publishers", views.PublisherViewSet, basename="publisher")
router.register(r"items", views.BookViewSet, basename="book")
router.register(r"copies", views.BookCopyViewSet, basename="bookcopy")
router.register(r"editions", views.BookEditionViewSet, basename="bookedition")

urlpatterns = [
    path("", include(router.urls)),
]

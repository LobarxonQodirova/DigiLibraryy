"""URL configuration for the members app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "members"

router = DefaultRouter()
router.register(r"cards", views.MembershipCardViewSet, basename="membershipcard")
router.register(r"reading-lists", views.ReadingListViewSet, basename="readinglist")

urlpatterns = [
    path("", include(router.urls)),
]

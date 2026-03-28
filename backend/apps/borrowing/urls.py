"""URL configuration for the borrowing app."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "borrowing"

router = DefaultRouter()
router.register(r"loans", views.BorrowingViewSet, basename="borrowing")
router.register(r"reservations", views.ReservationViewSet, basename="reservation")
router.register(r"history", views.BorrowingHistoryViewSet, basename="borrowinghistory")
router.register(r"fines", views.FineViewSet, basename="fine")

urlpatterns = [
    path("", include(router.urls)),
]

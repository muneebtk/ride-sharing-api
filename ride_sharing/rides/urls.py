from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import (
    RideLocationView,
    RideRequestView,
    RideStatusUpdateView,
    UserRegistrationView,
    signin_user,
    RideViewSet,
)


router = DefaultRouter()
router.register(r"rides", RideViewSet, basename="rides")

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("signin/", signin_user, name="user-signin"),
    path(
        "rides/<str:ride_id>/status/",
        RideStatusUpdateView.as_view(),
        name="ride-status-update",
    ),
    path(
        "rides/<str:ride_id>/location/",
        RideLocationView.as_view(),
        name="ride-location",
    ),
    path("rides/request/", RideRequestView.as_view(), name="ride-request"),
    path("", include(router.urls)),
]

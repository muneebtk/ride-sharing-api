from django.urls import re_path
from .consumer import RideTrackingConsumer

websocket_urlpatterns = [
    re_path(
        r"ws/ride-tracking/(?P<ride_id>[0-9a-f-]+)/$", RideTrackingConsumer.as_asgi()
    ),
]

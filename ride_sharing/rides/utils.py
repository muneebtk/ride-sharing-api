import random
from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance
from .models import User, Ride

# Default bounds for random latitude and longitude (adjust as needed)
DEFAULT_LATITUDE_BOUNDS = (-90, 90)
DEFAULT_LONGITUDE_BOUNDS = (-180, 180)

def get_nearby_drivers(rider_location, max_distance=5000):
    """
    Get a list of nearby drivers within a specified distance from the rider's location.
    :param rider_location: The location of the rider as a Point object.
    :param max_distance: The maximum distance in meters to search for drivers.
    :return: A queryset of nearby drivers.
    """
    print(f"Rider location: {rider_location}")
    drivers = User.objects.filter(is_driver=True, is_available=True)
    nearest_drivers = drivers.annotate(
        distance=Distance("current_location", rider_location)
    ).order_by("distance")[
        :5
    ]  # Top 5 closest drivers
    return nearest_drivers


def get_random_point():
    """Generates a random Point object with latitude and longitude."""
    latitude = random.uniform(*DEFAULT_LATITUDE_BOUNDS)
    longitude = random.uniform(*DEFAULT_LONGITUDE_BOUNDS)
    return Point(longitude, latitude)


def process_location_data(data):
    """Processes location data and assigns a random point if data is missing."""
    location_data = data.get("current_location", {})
    latitude = location_data.get("latitude")
    longitude = location_data.get("longitude")

    if latitude is not None and longitude is not None:
        return Point(float(longitude), float(latitude))
    else:
        return get_random_point()

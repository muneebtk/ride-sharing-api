import random
from celery import shared_task
from django.contrib.gis.geos import Point
from .models import Ride
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@shared_task(bind=True)
def simulate_ride_tracking(self, ride_id):
    """
    Simulate tracking a ride by periodically updating its location.
    """
    try:
        # Fetch the ride
        ride = Ride.objects.get(id=ride_id)

        # Exit if the ride status is no longer 'in_progress'
        if ride.status != "in_progress":
            print(
                f"Stopping tracking for ride {ride_id} as the status is '{ride.status}'."
            )
            return

        # Simulate new random coordinates within a range
        ride.current_location = generate_new_coordinates(ride.current_location)

        # Update the current location
        ride.save()

        # Notify clients about the location update
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"ride_{ride_id}",
            {
                "type": "send_location_update",
                "location": {
                    "lat": ride.current_location.y,
                    "lng": ride.current_location.x,
                },
            },
        )

        # Re-trigger this task for periodic updates
        self.apply_async(args=[ride_id], countdown=30)  # Schedule after 30 seconds

    except Ride.DoesNotExist:
        print(f"Ride with id {ride_id} does not exist. Stopping the task.")
    except Exception as e:
        print(f"An error occurred while tracking ride {ride_id}: {str(e)}")


def generate_new_coordinates(current_location):
    """
    Generate a new random Point within a small range.
    """
    lat = current_location.y if current_location else 0
    lng = current_location.x if current_location else 0
    lat += random.uniform(-0.001, 0.001)
    lng += random.uniform(-0.001, 0.001)
    return Point(lng, lat)

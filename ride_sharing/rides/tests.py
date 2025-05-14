from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rides.models import Ride, User
from rest_framework.authtoken.models import Token


class UserModelTestCase(TestCase):
    def test_user_creation(self):
        user = User.objects.create_user(email="testuser@example.com", password="securepassword")
        self.assertEqual(user.email, "testuser@example.com")
        self.assertTrue(user.check_password("securepassword"))
        self.assertFalse(user.is_driver)

    def test_driver_creation(self):
        driver = User.objects.create_user(
            email="driver@example.com",
            password="securepassword",
              is_driver=True,
                is_available=True
            )
        self.assertTrue(driver.is_driver)
        self.assertTrue(driver.is_available)

    def test_user_string_representation(self):
        user = User.objects.create_user(email="testuser@example.com", password="securepassword")
        self.assertEqual(str(user), "testuser@example.com")

class RideModelTestCase(TestCase):
    # Create a rider and driver
    def setUp(self):
        self.rider = User.objects.create_user(
            email="rider@example.com", password="riderpassword"
        )
        self.driver = User.objects.create_user(
            email="driver@example.com", password="driverpassword", is_driver=True
        )

    def test_ride_creation(self):
        ride = Ride.objects.create(
            rider=self.rider,
            driver=self.driver,
            pickup_location=Point(12.971598, 77.594566),
            dropoff_location=Point(13.035542, 77.5971),
            status="requested",
        )
        self.assertEqual(ride.rider, self.rider)
        self.assertEqual(ride.driver, self.driver)
        self.assertEqual(ride.status, "requested")

    def test_invalid_status(self):
        with self.assertRaises(ValueError):
            Ride.objects.create(
                rider=self.rider,
                pickup_location=Point(12.971598, 77.594566),
                dropoff_location=Point(13.035542, 77.5971),
                status="invalid_status",  # Assuming choices validation for status
            )
# ---------------model tests over------------------

from rest_framework_simplejwt.tokens import RefreshToken
from channels.testing import WebsocketCommunicator

class RideAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            email="testuser@gmail.com", password="testpassword"
        )
        self.client.login(email="testuser@gmail.com", password="testpassword")
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

        # Set the Authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")
        # Endpoint for ride creation
        self.create_ride_url = "/api/rides/request/"
        # self.accept_ride_url = "/api/rides/accept/"
        self.crud_ride_url = "/api/rides/"

    def test_create_ride(self):
        data = {
            "pickup_location": {"latitude": 12.971598, "longitude": 77.594566},
            "dropoff_location": {"latitude": 13.035542, "longitude": 77.5971},
        }
        response = self.client.post(self.create_ride_url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ride.objects.count(), 1)
        self.assertEqual(Ride.objects.first().status, "requested")

    def test_get_ride_detail(self):
        # Create a ride
        ride = Ride.objects.create(
            rider=self.user,
            pickup_location=Point(12.971598, 77.594566),
            dropoff_location=Point(13.035542, 77.5971),
        )

        # Retrieve the ride
        url = f"/api/rides/{ride.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "requested")

from rides.consumer import RideTrackingConsumer
from ride_sharing.asgi import application  # Import your Django Channels application
from channels.layers import get_channel_layer

# real time tracking tests
class RideRequestAndLocationTestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
             email="testuser@example.com", password="testpassword"
        )

        # Create a driver user
        self.driver = User.objects.create_user(
             email="testdriver@example.com", password="driverpassword", is_driver=True, is_available=True
        )

        # Create a test ride
        self.ride = Ride.objects.create(
            rider=self.user,
            pickup_location=Point(12.971598, 77.594566),
            dropoff_location=Point(13.035542, 77.5971),
            status="requested",
        )

        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
        self.ride_id = self.ride.id  # Example UUID

    async def test_realtime_location_update(self):
        # Create a WebSocket communicator
        communicator = WebsocketCommunicator(
            application, f"/ws/ride-tracking/{self.ride_id}/"
        )
        connected, subprotocol = await communicator.connect()
        self.assertTrue(connected)

        # Get the channel layer
        channel_layer = get_channel_layer()
        group_name = f"ride_{self.ride_id}"

        # Send a location update to the group
        test_location = {"latitude": 12.971598, "longitude": 77.594566}
        await channel_layer.group_send(
            group_name,
            {
                "type": "send_location_update",
                "location": test_location,
            },
        )

        # Receive the location update from the WebSocket
        response = await communicator.receive_json_from()
        self.assertEqual(response, test_location)

        # Close the WebSocket
        await communicator.disconnect()

    def test_fetch_available_drivers_on_ride_request(self):
        # API test for ride request and driver assignment
        url = reverse("ride-request")
        data = {
            "pickup_location": {"latitude":12.971598, "longitude": 77.594566},
            "dropoff_location": {"latitude":13.035542, "longitude": 77.5971},
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("ride_id", response.data)
        self.assertIn("nearest_drivers", response.data)

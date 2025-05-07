from django.contrib.gis.geos import Point
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rides.models import Ride, User
from rest_framework.authtoken.models import Token


from uuid import uuid4


# class RideAPITestCase(APITestCase):
#     def setUp(self):
#         # Setup for driver and a valid ride
#         self.driver = User.objects.create_user(
#             email="driver@example.com",
#             password="driverpassword",
#             is_driver=True,
#             is_available=True,
#         )
#         self.rider = User.objects.create_user(
#             email="rider@example.com", password="riderpassword", is_rider=True
#         )
#         self.ride = Ride.objects.create(
#             rider=self.rider,
#             pickup_location=Point(24.8607, 67.0011),
#             dropoff_location=Point(24.8707, 67.0211),
#             current_location=Point(24.8607, 67.0011),
#             status="requested",
#         )
#         self.client.force_authenticate(user=self.driver)

#     def test_accept_nonexistent_ride(self):
#         """Test that accepting a nonexistent ride returns a 404."""
#         non_existent_uuid = str(uuid4())  # Generate a valid but non-existent UUID
#         response = self.client.post(reverse("rides", args=[non_existent_uuid]))
#         self.assertEqual(response.status_code, 404)
#         self.assertIn("error", response.data)
#         self.assertEqual(response.data["error"], "Ride not found.")


# # api endpoint tests
# class RideAPITestCase(RideAPITestCase):
#     def test_accept_ride(self):
#         """
#         Test if a driver can successfully accept a ride.
#         """
#         response = self.client.post(reverse("ride-detail", args=[self.ride.id]))
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.ride.refresh_from_db()
#         self.driver.refresh_from_db()
#         self.assertEqual(self.ride.status, "in_progress")
#         self.assertEqual(self.ride.driver, self.driver)
#         self.assertFalse(self.driver.is_available)

#     def test_accept_ride_by_non_driver(self):
#         """
#         Test that only available drivers can accept rides.
#         """
#         self.client.force_authenticate(user=self.rider)  # Authenticate as rider
#         response = self.client.post(reverse("ride-detail", args=[self.ride.id]))
#         self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

#     def test_accept_nonexistent_ride(self):
#         """
#         Test that accepting a nonexistent ride returns a 404.
#         """
#         response = self.client.post(reverse("ride-detail", args=[str(uuid4())]))
#         self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

#     def test_reject_non_requested_ride(self):
#         """
#         Test that rides not in 'requested' status cannot be accepted.
#         """
#         self.ride.status = "in_progress"
#         self.ride.save()
#         response = self.client.post(reverse("ride-detail", args=[self.ride.id]))
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_location_tracking(self):
#         """
#         Test if the location updates correctly.
#         """
#         from rides.tasks import simulate_ride_tracking

#         simulate_ride_tracking(self.ride.id)

#         self.ride.refresh_from_db()
#         self.assertIsInstance(self.ride.current_location, Point)

#     def test_invalid_ride_tracking(self):
#         """
#         Test that tracking for a nonexistent ride does not crash.
#         """
#         from rides.tasks import simulate_ride_tracking

#         try:
#             simulate_ride_tracking(str(uuid4()))
#         except Exception:
#             self.fail(
#                 "simulate_ride_tracking raised an exception for a nonexistent ride."
#             )


# # ride matching algorithm tests
# class RideMatchingTestCase(APITestCase):
#     def setUp(self):
#         # Create driver and rider users
#         self.driver = User.objects.create_user(
#             email="driver@example.com",
#             password="driverpassword",
#             is_driver=True,
#             is_available=True,
#         )
#         self.rider = User.objects.create_user(
#             email="rider@example.com", password="riderpassword", is_driver=False
#         )

#         # Create a ride request
#         self.ride = Ride.objects.create(
#             rider=self.rider,
#             pickup_location=Point(12.971598, 77.594566),  # Example coordinates
#             destination=Point(13.035542, 77.5971),
#             status="requested",
#         )

#     def test_match_rider_to_driver(self):
#         # Call the ride-matching algorithm
#         response = self.client.post("/api/match/", {"ride_id": self.ride.id})
#         self.assertEqual(response.status_code, 200)
#         self.ride.refresh_from_db()
#         self.assertEqual(self.ride.driver, self.driver)
#         self.assertEqual(self.ride.status, "matched")


# # ride status update tests
# class RideStatusUpdateTestCase(APITestCase):
#     def setUp(self):
#         self.driver = User.objects.create_user(
#             email="driver@example.com",
#             password="driverpassword",
#             is_driver=True,
#             is_available=True,
#         )
#         self.rider = User.objects.create_user(
#             email="rider@example.com", password="riderpassword", is_driver=False
#         )

#         self.ride = Ride.objects.create(
#             rider=self.rider,
#             driver=self.driver,
#             pickup_location=Point(12.971598, 77.594566),
#             destination=Point(13.035542, 77.5971),
#             status="requested",
#         )

#     def test_update_ride_status(self):
#         # Update ride status
#         response = self.client.patch(
#             f"/api/rides/{self.ride.id}/", {"status": "completed"}
#         )
#         self.assertEqual(response.status_code, 200)
#         self.ride.refresh_from_db()
#         self.assertEqual(self.ride.status, "completed")


# # driver api endpoint tests
# class DriverAPITestCase(APITestCase):
#     def setUp(self):
#         self.driver = User.objects.create_user(
#             email="driver@example.com",
#             password="driverpassword",
#             is_driver=True,
#             is_available=True,
#         )
#         self.client.force_authenticate(user=self.driver)

#     def test_update_driver_availability(self):
#         # Update driver availability
#         response = self.client.patch("/api/driver/profile/", {"is_available": False})
#         self.assertEqual(response.status_code, 200)
#         self.driver.refresh_from_db()
#         self.assertFalse(self.driver.is_available)

#     def test_get_driver_rides(self):
#         response = self.client.get("/api/driver/rides/")
#         self.assertEqual(response.status_code, 200)
#         self.assertIsInstance(response.data, list)


# # ride tracking tests
# class RideTrackingTestCase(APITestCase):
#     def setUp(self):
#         self.driver = User.objects.create_user(
#             email="driver@example.com",
#             password="driverpassword",
#             is_driver=True,
#             is_available=True,
#         )
#         self.rider = User.objects.create_user(
#             email="rider@example.com", password="riderpassword", is_driver=False
#         )

#         self.ride = Ride.objects.create(
#             rider=self.rider,
#             driver=self.driver,
#             pickup_location=Point(12.971598, 77.594566),
#             destination=Point(13.035542, 77.5971),
#             status="ongoing",
#             current_location=Point(12.971598, 77.594566),
#         )
#         self.client.force_authenticate(user=self.driver)

#     def test_simulate_ride_tracking(self):
#         # Simulate updating driver's location
#         response = self.client.patch(
#             f"/api/rides/{self.ride.id}/track/",
#             {"current_location": {"latitude": 12.975, "longitude": 77.595}},
#         )
#         self.assertEqual(response.status_code, 200)
#         self.ride.refresh_from_db()
#         self.assertEqual(self.ride.current_location.x, 77.595)
#         self.assertEqual(self.ride.current_location.y, 12.975)

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

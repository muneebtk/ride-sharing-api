from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Ride, User
from .serializers import (
    RideSerializer,
    UserRegistrationSerializer,
    UserDetailSerializer,
)
from rest_framework.decorators import api_view, action
from .tasks import simulate_ride_tracking
from .utils import get_nearby_drivers, get_random_point
from django.contrib.gis.geos import Point

# 
class UserRegistrationView(APIView):
    def post(self, request):
        """ user registration view, handles user registration and location assignment.
        It generates a random point if no location is provided.
        """
        serializer = UserRegistrationSerializer(data=request.data)

        if serializer.is_valid():
            # Generate a random point if no location is provided
            random_point = get_random_point()

            # Extract or default to random point
            current_location = request.data.get("current_location", {})
            longitude = current_location.get("longitude", random_point.x)
            latitude = current_location.get("latitude", random_point.y)

            # Ensure the current_location is properly handled in the serializer
            serializer.validated_data["current_location"] = Point(
                float(longitude), float(latitude), srid=4326
            )
            user = serializer.save()
            return Response(
                {
                    "user": UserDetailSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )
        # Handle validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def signin_user(request):
    """ user sign-in view, handles user authentication and token generation.
    It checks if the user exists and if the password is correct."""
    if request.method == "POST":
        email = request.data.get("email")
        password = request.data.get("password")
        try:
            user = User.objects.get(email=email)
            if user.check_password(password):
                refresh = RefreshToken.for_user(user)
                return Response(
                    {
                        "user": UserDetailSerializer(user).data,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                return Response(
                    {"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST
                )
        except User.DoesNotExist:
            return Response(
                {"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class RideViewSet(viewsets.ModelViewSet):
    """Ride viewset for handling get and get all rides."""
    queryset = Ride.objects.all()
    serializer_class = RideSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(rider=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            # Riders see their own rides; drivers see assigned rides
            if user.groups.filter(name="Driver").exists():
                return Ride.objects.filter(driver=user)
            return Ride.objects.filter(rider=user)
        return Ride.objects.none()


class RideLocationView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, ride_id):
        """Get the current location of a ride. Only accessible to the rider or driver."""
        try:
            ride = Ride.objects.get(id=ride_id)
            if request.user != ride.rider and request.user != ride.driver:
                return Response(
                    {"detail": "Not authorized to view this ride."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            return Response(
                {"current_location": str(ride.current_location)},
                status=status.HTTP_200_OK,
            )
        except Ride.DoesNotExist:
            return Response(
                {"detail": "Ride not found."}, status=status.HTTP_404_NOT_FOUND
            )


class RideRequestView(APIView):
    """Ride request view for riders to request a ride and get nearby drivers."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        pickup_data = request.data.get("pickup_location")
        dropoff_data = request.data.get("dropoff_location")
        if not pickup_data or not dropoff_data:
            return Response(
                {"error": "Pickup and dropoff locations are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert to Point objects
        pickup_location = Point(
            pickup_data["longitude"], pickup_data["latitude"], srid=4326
        )
        dropoff_location = Point(
            dropoff_data["longitude"], dropoff_data["latitude"], srid=4326
        )

        ride = Ride.objects.create(
            rider=request.user,
            pickup_location=pickup_location,
            dropoff_location=dropoff_location,
            status="requested",
        )

        nearest_drivers = get_nearby_drivers(pickup_location)

        # Format response
        formatted_drivers = []
        for driver in nearest_drivers:
            # Convert distance from meters to kilometers (rounded to 2 decimals)
            distance_km = (
                round(driver.distance.m / 1000, 2) if driver.distance else None
            )

            # Extract lat/lng from Point (driver.current_location)
            driver_lat = driver.current_location.y
            driver_lng = driver.current_location.x

            formatted_drivers.append(
                {
                    "id": driver.id,
                    "distance_km": distance_km,
                    "current_location": {
                        "latitude": driver_lat,
                        "longitude": driver_lng,
                    },
                }
            )

        return Response(
            {
                "ride_id": ride.id,
                "nearest_drivers": formatted_drivers,
            },
            status=status.HTTP_201_CREATED,
        )


class RideStatusUpdateView(APIView):
    """"Ride status update view for drivers to update the status of a ride."""
    permission_classes = [IsAuthenticated]

    def patch(self, request, ride_id):
        try:
            ride = Ride.objects.get(id=ride_id)
            new_status = request.data.get(
                "status"
            )  # Expected: "in_progress", "completed", "cancelled"

            # Validate status input
            if new_status not in [
                choice[0] for choice in Ride.STATUS_CHOICES if choice[0] != "requested"
            ]:
                return Response(
                    {
                        "error": f"Invalid status. Allowed: {[choice[0] for choice in Ride.STATUS_CHOICES if choice[0] != 'requested']}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # --- Status: in_progress (Driver accepts) ---
            if new_status == "in_progress":
                if not (request.user.is_driver and request.user.is_available):
                    return Response(
                        {"error": "Only available drivers can accept rides."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if ride.status != "requested":
                    return Response(
                        {"error": "Ride must be in 'requested' state to be accepted."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ride.driver = request.user
                ride.status = "in_progress"
                ride.save()
                request.user.is_available = False
                request.user.save()
                simulate_ride_tracking.delay(ride.id)  # Start tracking
                return Response(
                    {"message": "Ride accepted. Status updated to 'in_progress'."},
                    status=status.HTTP_200_OK,
                )

            # --- Status: cancelled ---
            elif new_status == "cancelled":
                # Allow cancellation by driver (if assigned) or rider (if ride is still requested)
                if ride.driver and ride.driver != request.user:
                    return Response(
                        {"error": "Only the assigned driver can cancel this ride."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if ride.status == "completed":
                    return Response(
                        {"error": "Completed rides cannot be cancelled."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                # Revert to 'requested' if driver cancels mid-ride
                if ride.driver:
                    ride.driver.is_available = True
                    ride.driver.save()
                    ride.driver = None
                ride.status = "requested"
                ride.save()
                return Response(
                    {"message": "Ride cancelled successfully."},
                    status=status.HTTP_200_OK,
                )

            # --- Status: completed ---
            elif new_status == "completed":
                if not ride.driver or ride.driver != request.user:
                    return Response(
                        {"error": "Only the assigned driver can complete the ride."},
                        status=status.HTTP_403_FORBIDDEN,
                    )
                if ride.status != "in_progress":
                    return Response(
                        {"error": "Only rides 'in_progress' can be completed."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

                ride.status = "completed"
                ride.save()
                request.user.is_available = True  # Mark driver as available
                request.user.save()
                return Response(
                    {"message": "Ride completed successfully."},
                    status=status.HTTP_200_OK,
                )

        except Ride.DoesNotExist:
            return Response(
                {"error": "Ride not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

import uuid
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db import models
from django.contrib.gis.db import models as gis_models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    current_location = gis_models.PointField(null=True, blank=True)
    is_driver = models.BooleanField(default=False)
    is_rider = models.BooleanField(default=False)
    is_driver = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)  # Only relevant for drivers

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_set",
        blank=True,
        help_text="Specific permissions for this user.",
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.email


class Ride(models.Model):
    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name="rider_rides")
    driver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="driver_rides", null=True, blank=True)
    pickup_location = gis_models.PointField()  # Latitude/Longitude for pickup
    dropoff_location = gis_models.PointField()  # Latitude/Longitude for dropoff
    current_location = gis_models.PointField(
        null=True, blank=True
    )  # Real-time tracking
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="requested"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ride {self.id} - {self.status}"

    def save(self, *args, **kwargs):
        if self.status not in dict(self.STATUS_CHOICES):
            raise ValueError(f"Invalid status: {self.status}")
        super().save(*args, **kwargs)

from rest_framework import serializers
from .models import Ride, User
from django.contrib.gis.geos import Point
from .utils import get_random_point

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('email', 'password', 'phone_number', 'is_driver', 'is_rider', 'confirm_password', "first_name", "last_name", "current_location")

    def create(self, validated_data):
        if validated_data.get('password') != validated_data.get('confirm_password'):
            raise serializers.ValidationError("Passwords do not match")
        if validated_data.get('is_driver') and validated_data.get('is_rider'):
            raise serializers.ValidationError("User cannot be both driver and rider")
        if not validated_data.get('is_driver') and not validated_data.get('is_rider'):
            raise serializers.ValidationError("User must be either a driver or a rider")
        if validated_data.get('phone_number') and not validated_data.get('phone_number').isdigit():
            raise serializers.ValidationError("Phone number must be numeric")
        if validated_data.get('phone_number') and len(validated_data.get('phone_number')) != 10:
            raise serializers.ValidationError("Phone number must be 10 digits long")
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        if validated_data.get('phone_number') and User.objects.filter(phone_number=validated_data['phone_number']).exists():
            raise serializers.ValidationError("Phone number already exists")

        user = User.objects.create_user(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number'),
            is_driver=validated_data.get('is_driver', False),
            is_rider=validated_data.get('is_rider', False),
            current_location=validated_data.get('current_location')
        )
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'phone_number', 'is_driver', 'is_rider')


class RideSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ride
        fields = '__all__'
        read_only_fields = ['rider', 'driver', 'current_location', 'created_at', 'updated_at']


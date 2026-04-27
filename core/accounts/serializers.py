from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .models import (
    User,
    Location,
    BloodInventory,
    Request,
    Donation,
    Notification,
    SystemLog,
    GlobalSettings
)


# -----------------------------
# USER
# -----------------------------
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'password',
            'first_name',
            'last_name',
            'blood_type',
            'role',
            'location',
            'phone',
            'is_active_donor',
            'last_donation_date'
        ]
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        password = validated_data.get('password', None)

        if password:
            validated_data['password'] = make_password(password)

        return super().update(instance, validated_data)


# -----------------------------
# LOCATION
# -----------------------------
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'


# -----------------------------
# BLOOD INVENTORY
# -----------------------------
class BloodInventorySerializer(serializers.ModelSerializer):
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = BloodInventory
        fields = '__all__'


# -----------------------------
# BLOOD REQUEST
# -----------------------------
class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'
        read_only_fields = ['requester', 'status', 'approved_at']


# -----------------------------
# DONATION
# -----------------------------
class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = '__all__'


# -----------------------------
# NOTIFICATION (SAFER)
# -----------------------------
class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'
        read_only_fields = ['recipient', 'created_at']


# -----------------------------
# SYSTEM LOG (READ ONLY SAFE)
# -----------------------------
class SystemLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemLog
        fields = '__all__'
        read_only_fields = fields  # fully read-only


# -----------------------------
# GLOBAL SETTINGS (ADMIN ONLY SAFE)
# -----------------------------
class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = GlobalSettings
        fields = '__all__'
        read_only_fields = ['updated_at']
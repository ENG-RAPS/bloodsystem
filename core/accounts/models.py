from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator


# -----------------------------
# LOCATION (Hospitals / Centers)
# -----------------------------
class Location(models.Model):
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    area = models.CharField(max_length=100)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.city}"


# -----------------------------
# USER (Donor / Recipient / Admin via role)
# -----------------------------
class User(AbstractUser):


    BLOOD_TYPE_CHOICES = [
    ('O+', 'O Positive'),
    ('O-', 'O Negative'),
    ('A+', 'A Positive'),
    ('A-', 'A Negative'),
    ('B+', 'B Positive'),
    ('B-', 'B Negative'),
    ('AB+', 'AB Positive'),
    ('AB-', 'AB Negative'),
                    ]
    
    ROLE_CHOICES = [
        ('donor', 'Donor'),
        ('recipient', 'Recipient'),
        ('both', 'Both'),
        ('admin', 'Admin'),
        ('super_admin', 'Super Admin'),
    ]

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recipient')

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    phone = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{9,15}$')]
    )

    is_active_donor = models.BooleanField(default=False)
    last_donation_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username




# -----------------------------
# BLOOD INVENTORY
# -----------------------------
class BloodInventory(models.Model):

    BLOOD_TYPE_CHOICES = [
        ('O+', 'O+'), ('O-', 'O-'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPE_CHOICES)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    units_available = models.PositiveIntegerField(default=0)
    expiry_date = models.DateField()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('blood_type', 'location')

    def __str__(self):
        return f"{self.blood_type} - {self.location.name}"


# -----------------------------
# BLOOD REQUEST
# -----------------------------
class Request(models.Model):

    REQUEST_TYPE_CHOICES = [
        ('normal', 'Normal'),
        ('emergency', 'Emergency'),
    ]

    REQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    ]

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests')
    blood_type = models.CharField(max_length=3)
    units_required = models.PositiveIntegerField()

    request_type = models.CharField(max_length=20, choices=REQUEST_TYPE_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=REQUEST_STATUS_CHOICES, default='pending')

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    reason = models.TextField()

    # FIX: no Admin model anymore → use User role system
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_requests'
    )

    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requester.username} - {self.blood_type} ({self.status})"


# -----------------------------
# DONATION
# -----------------------------
class Donation(models.Model):

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    donor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='donations')
    blood_type = models.CharField(max_length=3)
    units_donated = models.PositiveIntegerField()

    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')

    scheduled_date = models.DateTimeField()
    completed_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor.username} - {self.blood_type}"


# -----------------------------
# NOTIFICATION
# -----------------------------
class Notification(models.Model):

    NOTIFICATION_TYPE_CHOICES = [
        ('request_status', 'Request Status'),
        ('emergency_alert', 'Emergency Alert'),
        ('donation_reminder', 'Donation Reminder'),
        ('general', 'General'),
    ]

    CHANNEL_CHOICES = [
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('in_app', 'In-App'),
    ]

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')

    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES)
    channel = models.CharField(max_length=20, choices=CHANNEL_CHOICES)

    title = models.CharField(max_length=255)
    message = models.TextField()

    is_read = models.BooleanField(default=False)

    related_request = models.ForeignKey(Request, on_delete=models.SET_NULL, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


# -----------------------------
# SYSTEM LOG (Audit)
# -----------------------------
class SystemLog(models.Model):

    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
        ('access', 'Access'),
    ]

    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    resource_type = models.CharField(max_length=100)
    resource_id = models.PositiveIntegerField()

    details = models.JSONField(default=dict)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)


# -----------------------------
# GLOBAL SETTINGS
# -----------------------------
class GlobalSettings(models.Model):

    auto_approve_requests = models.BooleanField(default=False)
    emergency_priority = models.BooleanField(default=True)

    notification_channels = models.JSONField(default=list)
    system_message = models.TextField(blank=True)

    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Global System Settings"
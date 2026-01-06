from django.db import models
from django.conf import settings
from django.utils import timezone


class PriceRange(models.Model):
    label = models.CharField(max_length=50)
    min_price = models.PositiveIntegerField()
    max_price = models.PositiveIntegerField(null=True, blank=True)  # None = no upper limit

    class Meta:
        ordering = ["min_price"]

    def __str__(self):
        return self.label


class ServiceRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    DECLINE_REASON_CHOICES = [
        ('price', 'Price'),
        ('distance', 'Distance'),
        ('time', 'Time'),
        ('other', 'Other'),
    ]

    # Requester (user who creates the request)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="service_requests"
    )

    # Provider (service provider who accepts/declines)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_requests_as_provider"
    )

    # Request details
    description = models.TextField()
    provider_name = models.CharField(max_length=255)  # Name of provider being requested

    # OPTIONAL per UI spec
    date_time = models.DateTimeField(null=True, blank=True)

    # OPTIONAL per UI spec
    price_range = models.ForeignKey(
        PriceRange,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="requests",
    )

    urgent = models.BooleanField(default=False)

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    # Decline information
    decline_reason = models.CharField(
        max_length=20,
        choices=DECLINE_REASON_CHOICES,
        null=True,
        blank=True
    )
    decline_message = models.TextField(null=True, blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Request #{self.id} - {self.provider_name}"

    def accept(self, provider):
        """Mark the request as accepted"""
        self.status = 'accepted'
        self.provider = provider
        self.accepted_at = timezone.now()
        self.save()

    def decline(self, reason, message=''):
        """Mark the request as declined"""
        self.status = 'declined'
        self.decline_reason = reason
        self.decline_message = message
        self.declined_at = timezone.now()
        self.save()


class RequestPhoto(models.Model):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(upload_to="request_photos/")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for Request #{self.service_request_id}"


class RequestDecisionToken(models.Model):
    """
    Stores secure tokens for provider decision links.
    Allows providers to accept/decline requests via secure links.
    """
    service_request = models.OneToOneField(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="decision_token"
    )

    token = models.CharField(max_length=255, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Decision Token for Request #{self.service_request_id}"

    def is_expired(self):
        """Check if the token has expired"""
        return timezone.now() > self.expires_at

    def is_valid(self):
        """Check if the token is still valid for use"""
        return not self.used and not self.is_expired()

    def mark_as_used(self):
        """Mark the token as used"""
        self.used = True
        self.used_at = timezone.now()
        self.save()
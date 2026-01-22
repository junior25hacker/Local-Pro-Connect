from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from .file_validation import validate_request_photo, generate_secure_filename

# Note: JobCompletion, ServiceRating, and ServiceFeedback models are in completion_models.py


def secure_photo_upload_path(instance, filename):
    """Generate secure upload path for request photos."""
    secure_name = generate_secure_filename(filename, "request_photo")
    return f"request_photos/{secure_name}"


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
        ('completed', 'Completed'),
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
    
    # Price offered by the user
    offered_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Price offered by the user")

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
    
    # Distance calculation field
    distance_km = models.DecimalField(
        max_digits=6, 
        decimal_places=1, 
        null=True, 
        blank=True, 
        help_text="Distance from user to provider in kilometers (calculated using Haversine formula)"
    )

    # Location fields for geolocation support
    address_string = models.CharField(
        max_length=500, 
        blank=True, 
        help_text="Full address string provided by user"
    )
    latitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="GPS latitude coordinate"
    )
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        null=True, 
        blank=True, 
        help_text="GPS longitude coordinate"
    )

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True,
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
    # NOTE: Use default=timezone.now (not auto_now_add) so timestamps can be set explicitly
    # (e.g. for imports/tests) while still defaulting to creation time.
    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    declined_at = models.DateTimeField(null=True, blank=True)
    
    # Email tracking
    email_sent_to_provider = models.BooleanField(default=False, help_text="Whether provider notification email was sent")
    email_sent_to_provider_timestamp = models.DateTimeField(null=True, blank=True, help_text="When provider email was sent")
    email_sent_to_user = models.BooleanField(default=False, help_text="Whether user notification email was sent")
    email_sent_to_user_timestamp = models.DateTimeField(null=True, blank=True, help_text="When user email was sent")
    email_read_timestamp = models.DateTimeField(null=True, blank=True, help_text="When provider opened email (if tracked)")
    email_response_timestamp = models.DateTimeField(null=True, blank=True, help_text="When provider responded to request")

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

    def clean(self):
        """Validate GPS coordinates"""
        super().clean()
        
        # Validate latitude range
        if self.latitude is not None:
            if not (-90 <= self.latitude <= 90):
                raise ValidationError({
                    'latitude': 'Latitude must be between -90 and 90 degrees'
                })
        
        # Validate longitude range
        if self.longitude is not None:
            if not (-180 <= self.longitude <= 180):
                raise ValidationError({
                    'longitude': 'Longitude must be between -180 and 180 degrees'
                })
        
        # Both coordinates should be provided together
        if (self.latitude is not None) != (self.longitude is not None):
            raise ValidationError(
                'Both latitude and longitude must be provided together'
            )

    def has_location(self):
        """Check if this request has valid GPS coordinates"""
        return (self.latitude is not None and 
                self.longitude is not None and
                bool(self.address_string.strip()))

    def get_location_data(self):
        """Get location data as a dictionary for API responses"""
        return {
            'address_string': self.address_string,
            'latitude': float(self.latitude) if self.latitude else None,
            'longitude': float(self.longitude) if self.longitude else None,
            'has_location': self.has_location()
        }
    
    def calculate_distance_to_provider(self, provider_profile):
        """
        Calculate and store distance to a specific provider using Haversine formula.
        
        Args:
            provider_profile: ProviderProfile instance
            
        Returns:
            float or None: Distance in kilometers, or None if coordinates missing
        """
        from .distance_utils import calculate_request_distance
        
        distance = calculate_request_distance(self, provider_profile)
        if distance is not None:
            self.distance_km = distance
            # Don't auto-save here to allow bulk operations
        
        return distance
    
    def update_distance_and_save(self, provider_profile):
        """
        Calculate distance to provider and save the request.
        
        Args:
            provider_profile: ProviderProfile instance
        """
        self.calculate_distance_to_provider(provider_profile)
        self.save(update_fields=['distance_km'])
    
    def get_priority_score(self):
        """
        Get priority score for request ordering in provider queues.
        
        Returns:
            int: Priority score (higher = more urgent)
        """
        from .distance_utils import calculate_priority_score
        return calculate_priority_score(self)
    
    def get_distance_display(self):
        """
        Get formatted distance string for display.
        
        Returns:
            str: Formatted distance string
        """
        from .distance_utils import format_distance_display
        return format_distance_display(self.distance_km)
    
    @classmethod
    def get_requests_for_provider(cls, provider_profile, include_distance=True):
        """
        Get all pending requests ordered by priority (urgent first, then by distance/time).
        
        Args:
            provider_profile: ProviderProfile instance
            include_distance: Whether to calculate and include distance
            
        Returns:
            QuerySet: Ordered list of ServiceRequest objects
        """
        requests = cls.objects.filter(
            status='pending'
        ).select_related('user', 'user__user_profile')
        
        if include_distance:
            # Calculate distances for all requests
            for request in requests:
                if request.has_location():
                    request.calculate_distance_to_provider(provider_profile)
        
        # Convert to list to allow custom sorting
        request_list = list(requests)
        
        # Sort by priority score (highest first)
        request_list.sort(key=lambda r: r.get_priority_score(), reverse=True)
        
        return request_list
    
    def is_in_progress(self):
        """
        Check if request is currently in progress (accepted but not completed).
        
        Returns:
            bool: True if request is accepted and not yet completed
        """
        if self.status != 'accepted':
            return False
        
        # Check if job has been completed
        return not hasattr(self, 'completion')
    
    def can_be_completed(self):
        """
        Validate if request can be marked as complete.
        
        Returns:
            tuple: (bool, str) - (can_complete, error_message)
        """
        if self.status != 'accepted':
            return False, "Only accepted requests can be marked as completed."
        
        if hasattr(self, 'completion'):
            return False, "This request has already been marked as completed."
        
        if not self.provider:
            return False, "No provider assigned to this request."
        
        return True, ""
    
    def can_be_rated(self):
        """
        Check if request is ready for rating.
        
        Returns:
            tuple: (bool, str) - (can_rate, error_message)
        """
        if not hasattr(self, 'completion'):
            return False, "Request must be completed before rating."
        
        if hasattr(self.completion, 'rating'):
            return False, "This request has already been rated."
        
        return True, ""


class RequestPhoto(models.Model):
    service_request = models.ForeignKey(
        ServiceRequest,
        on_delete=models.CASCADE,
        related_name="photos",
    )

    image = models.ImageField(
        upload_to=secure_photo_upload_path,
        validators=[validate_request_photo],
        help_text="Upload request photo (JPG, PNG, GIF, WEBP). Max size: 5MB, Max dimensions: 4096x4096px"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # Additional metadata
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    original_filename = models.CharField(max_length=255, blank=True, help_text="Original uploaded filename")

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Request Photo'
        verbose_name_plural = 'Request Photos'

    def __str__(self):
        return f"Photo for Request #{self.service_request_id}"

    def save(self, *args, **kwargs):
        if self.image:
            self.file_size = self.image.size
            if hasattr(self.image, 'name'):
                self.original_filename = self.image.name
        super().save(*args, **kwargs)


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
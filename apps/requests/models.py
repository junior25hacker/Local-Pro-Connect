from django.db import models


class PriceRange(models.Model):
    label = models.CharField(max_length=50)
    min_price = models.PositiveIntegerField()
    max_price = models.PositiveIntegerField(null=True, blank=True)  # None = no upper limit

    class Meta:
        ordering = ["min_price"]

    def __str__(self):
        return self.label


class ServiceRequest(models.Model):
    description = models.TextField()

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

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request #{self.id}"


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
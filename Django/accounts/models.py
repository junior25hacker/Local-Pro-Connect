from django.db import models
from django.conf import settings


class UserProfile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_profile')
	phone = models.CharField(max_length=20, blank=True)
	address = models.CharField(max_length=255, blank=True)
	city = models.CharField(max_length=100, blank=True)
	state = models.CharField(max_length=50, blank=True)
	zip_code = models.CharField(max_length=10, blank=True)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'User Profile'
		verbose_name_plural = 'User Profiles'

	def __str__(self):
		return f"Profile: {self.user.username}"


class ProviderProfile(models.Model):
	SERVICE_CHOICES = [
		('plumbing', 'Plumbing'),
		('electrical', 'Electrical'),
		('carpentry', 'Carpentry'),
		('cleaning', 'Cleaning'),
		('tutoring', 'Tutoring'),
		('hvac', 'HVAC'),
		('roofing', 'Roofing'),
		('landscaping', 'Landscaping'),
		('painting', 'Painting'),
		('other', 'Other'),
	]

	user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='provider_profile')
	company_name = models.CharField(max_length=255, blank=True)
	service_type = models.CharField(max_length=50, choices=SERVICE_CHOICES, default='other')
	phone = models.CharField(max_length=20, blank=True)
	business_address = models.CharField(max_length=255, blank=True)
	city = models.CharField(max_length=100, blank=True)
	state = models.CharField(max_length=50, blank=True)
	zip_code = models.CharField(max_length=10, blank=True)
	service_description = models.TextField(blank=True)
	bio = models.TextField(blank=True)
	profile_picture = models.ImageField(upload_to='profiles/', null=True, blank=True)
	services_rendered = models.PositiveIntegerField(default=0)
	years_experience = models.PositiveIntegerField(default=0)
	rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
	total_reviews = models.IntegerField(default=0)
	is_verified = models.BooleanField(default=False)
	
	# Pricing and location fields
	min_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00, help_text="Minimum service price")
	latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Current latitude for live tracking")
	longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Current longitude for live tracking")
	
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		verbose_name = 'Provider Profile'
		verbose_name_plural = 'Provider Profiles'
		ordering = ['-created_at']

	def __str__(self):
		return f"Provider: {self.user.username} ({self.company_name})"


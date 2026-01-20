"""
Models for job completion tracking and rating system.

This module defines models to track:
- Job completion when user marks job as done
- Star ratings and feedback
- Service completion history
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class JobCompletion(models.Model):
    """
    Tracks when a user marks a job as completed.
    Links to the original ServiceRequest and stores completion details.
    """
    
    # Link to original service request
    service_request = models.OneToOneField(
        'ServiceRequest',
        on_delete=models.CASCADE,
        related_name='completion',
        help_text="The service request that was completed"
    )
    
    # Completion details
    completed_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the job was marked as completed"
    )
    
    # User who marked it complete (should be the original requester)
    completed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='completed_jobs',
        help_text="User who marked the job as complete"
    )
    
    # Optional completion notes from user
    completion_notes = models.TextField(
        blank=True,
        help_text="Optional notes about the job completion"
    )
    
    # Work quality assessment (before rating)
    work_quality = models.CharField(
        max_length=20,
        choices=[
            ('excellent', 'Excellent'),
            ('good', 'Good'),
            ('satisfactory', 'Satisfactory'),
            ('needs_improvement', 'Needs Improvement'),
        ],
        null=True,
        blank=True,
        help_text="User's assessment of work quality"
    )
    
    # Whether job was completed on time
    completed_on_time = models.BooleanField(
        default=True,
        help_text="Whether the job was completed on schedule"
    )
    
    # Provider showed up as expected
    provider_showed_up = models.BooleanField(
        default=True,
        help_text="Whether the provider showed up as scheduled"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-completed_at']
        verbose_name = 'Job Completion'
        verbose_name_plural = 'Job Completions'
    
    def __str__(self):
        return f"Completion for Request #{self.service_request.id} by {self.completed_by.username}"


class ServiceRating(models.Model):
    """
    Stores user ratings and feedback for completed services.
    One rating per completed job.
    """
    
    # Link to job completion
    job_completion = models.OneToOneField(
        JobCompletion,
        on_delete=models.CASCADE,
        related_name='rating',
        help_text="The job completion this rating is for"
    )
    
    # Star rating (1-5 stars)
    stars = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Star rating from 1 to 5"
    )
    
    # Written feedback
    feedback = models.TextField(
        help_text="User's written feedback about the service",
        max_length=1000
    )
    
    # Category-specific ratings
    quality_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Rating for quality of work (1-5)"
    )
    
    timeliness_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Rating for timeliness (1-5)"
    )
    
    communication_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Rating for communication (1-5)"
    )
    
    professionalism_rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True,
        blank=True,
        help_text="Rating for professionalism (1-5)"
    )
    
    # Would recommend to others
    would_recommend = models.BooleanField(
        default=True,
        help_text="Would the user recommend this provider to others"
    )
    
    # Would hire again
    would_hire_again = models.BooleanField(
        default=True,
        help_text="Would the user hire this provider again"
    )
    
    # Rating submission
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # User who submitted rating (for validation)
    rated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_ratings',
        help_text="User who submitted this rating"
    )
    
    # Provider being rated (denormalized for easier queries)
    provider = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_ratings',
        help_text="Provider who received this rating"
    )
    
    # Whether this rating is public
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this rating should be shown publicly"
    )
    
    # Whether provider has responded to this rating
    provider_response = models.TextField(
        blank=True,
        help_text="Provider's response to the rating",
        max_length=500
    )
    
    provider_response_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When provider responded to the rating"
    )
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Service Rating'
        verbose_name_plural = 'Service Ratings'
    
    def __str__(self):
        return f"{self.stars}-star rating for Request #{self.job_completion.service_request.id}"
    
    @property
    def service_request(self):
        """Quick access to the related service request"""
        return self.job_completion.service_request
    
    @property
    def average_category_rating(self):
        """Calculate average of category ratings if any are provided"""
        ratings = [
            self.quality_rating,
            self.timeliness_rating,
            self.communication_rating,
            self.professionalism_rating,
        ]
        valid_ratings = [r for r in ratings if r is not None]
        
        if valid_ratings:
            return sum(valid_ratings) / len(valid_ratings)
        return None


class ServiceFeedback(models.Model):
    """
    Additional feedback model for storing service-specific comments and suggestions.
    This can be submitted independently of ratings.
    """
    
    # Link to service request
    service_request = models.ForeignKey(
        'ServiceRequest',
        on_delete=models.CASCADE,
        related_name='feedback_entries',
        help_text="Service request this feedback is about"
    )
    
    # Feedback type
    feedback_type = models.CharField(
        max_length=20,
        choices=[
            ('general', 'General Feedback'),
            ('complaint', 'Complaint'),
            ('suggestion', 'Suggestion'),
            ('compliment', 'Compliment'),
            ('issue', 'Issue Report'),
        ],
        default='general',
        help_text="Type of feedback"
    )
    
    # Feedback content
    feedback_text = models.TextField(
        help_text="Feedback content",
        max_length=2000
    )
    
    # Feedback category (what aspect of service)
    category = models.CharField(
        max_length=20,
        choices=[
            ('quality', 'Work Quality'),
            ('timing', 'Timing/Schedule'),
            ('communication', 'Communication'),
            ('pricing', 'Pricing'),
            ('professionalism', 'Professionalism'),
            ('platform', 'Platform Experience'),
            ('other', 'Other'),
        ],
        default='other',
        help_text="Category of feedback"
    )
    
    # Priority/severity
    priority = models.CharField(
        max_length=10,
        choices=[
            ('low', 'Low'),
            ('medium', 'Medium'),
            ('high', 'High'),
            ('urgent', 'Urgent'),
        ],
        default='medium',
        help_text="Priority level of this feedback"
    )
    
    # Submitter
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_feedback',
        help_text="User who submitted the feedback"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('new', 'New'),
            ('reviewed', 'Reviewed'),
            ('addressed', 'Addressed'),
            ('closed', 'Closed'),
        ],
        default='new',
        help_text="Status of feedback processing"
    )
    
    # Admin response
    admin_response = models.TextField(
        blank=True,
        help_text="Administrative response to feedback"
    )
    
    admin_response_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='feedback_responses',
        help_text="Admin who responded"
    )
    
    admin_response_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When admin responded"
    )
    
    # Timestamps
    submitted_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Service Feedback'
        verbose_name_plural = 'Service Feedback'
    
    def __str__(self):
        return f"{self.feedback_type.title()} for Request #{self.service_request.id}"
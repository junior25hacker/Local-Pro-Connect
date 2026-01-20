"""
Signals for handling job completion and rating workflow events.
Automatically sends emails when jobs are completed or rated.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='requests.JobCompletion')
def handle_job_completion_created(sender, instance, created, **kwargs):
    """
    Signal handler: When a job is marked as completed, send notification to provider.
    """
    if created:
        logger.info(f"Job completion created: #{instance.id} for request #{instance.service_request.id}")
        
        # Import here to avoid circular imports
        from .email_service import send_job_completion_notification
        
        # Send provider notification
        result = send_job_completion_notification(instance, async_send=True)
        logger.info(f"Job completion notification result: {result}")


@receiver(post_save, sender='requests.ServiceRating')
def handle_rating_submitted(sender, instance, created, **kwargs):
    """
    Signal handler: When a rating is submitted, send notification to provider.
    """
    if created:
        logger.info(f"Rating submitted: #{instance.id} for request #{instance.job_completion.service_request.id}")
        
        # Import here to avoid circular imports  
        from .email_service import send_rating_received_notification
        
        # Send provider notification
        result = send_rating_received_notification(instance, async_send=True)
        logger.info(f"Rating notification result: {result}")


@receiver(post_save, sender='requests.ServiceFeedback')
def handle_feedback_submitted(sender, instance, created, **kwargs):
    """
    Signal handler: When feedback is submitted, log it for admin review.
    """
    if created:
        logger.info(
            f"Feedback submitted: #{instance.id} for request #{instance.service_request.id} "
            f"- Type: {instance.feedback_type}, Priority: {instance.priority}"
        )
        
        # If high priority or complaint, could send admin notification here
        if instance.priority in ['high', 'urgent'] or instance.feedback_type == 'complaint':
            logger.warning(
                f"High priority feedback received: {instance.feedback_type} "
                f"for request #{instance.service_request.id}"
            )
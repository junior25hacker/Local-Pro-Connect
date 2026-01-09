"""
Signals for handling ServiceRequest workflow events.
Automatically sends emails when requests are created, accepted, or declined.

Uses the centralized email_service module for all email operations.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ServiceRequest, RequestDecisionToken
from .email_service import (
    send_request_to_provider,
    send_user_confirmation_email,
    send_acceptance_email,
    send_decline_email,
)

import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=ServiceRequest)
def handle_service_request_created(sender, instance, created, **kwargs):
    """
    Signal handler: When a service request is created, send emails to:
    1. The provider (with accept/decline links)
    2. The user (confirmation email)
    """
    if created:
        logger.info(f"New service request created: #{instance.id}")
        
        # Send provider notification with decision links
        provider_result = send_request_to_provider(instance, async_send=True)
        logger.info(f"Provider notification result: {provider_result}")
        
        # Send user confirmation email
        user_result = send_user_confirmation_email(instance, async_send=True)
        logger.info(f"User confirmation result: {user_result}")


@receiver(post_save, sender=ServiceRequest)
def handle_service_request_accepted(sender, instance, created, **kwargs):
    """
    Signal handler: When a service request is accepted, send email to customer.
    """
    # Only on updates (not creation) and only if status changed to accepted
    if not created and instance.status == 'accepted' and instance.accepted_at:
        logger.info(f"Service request accepted: #{instance.id}")
        
        # Send acceptance notification to customer
        result = send_acceptance_email(instance, async_send=True)
        logger.info(f"Acceptance email result: {result}")


@receiver(post_save, sender=ServiceRequest)
def handle_service_request_declined(sender, instance, created, **kwargs):
    """
    Signal handler: When a service request is declined, send email to customer.
    """
    # Only on updates (not creation) and only if status changed to declined
    if not created and instance.status == 'declined' and instance.declined_at:
        logger.info(f"Service request declined: #{instance.id}")
        
        # Send decline notification to customer
        result = send_decline_email(
            instance,
            decline_reason=instance.decline_reason,
            decline_message=instance.decline_message,
            async_send=True
        )
        logger.info(f"Decline email result: {result}")

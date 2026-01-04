"""
Signals for handling ServiceRequest workflow events.
Automatically sends emails when requests are created, accepted, or declined.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mass_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets

from .models import ServiceRequest, RequestDecisionToken
from .utils import generate_secure_token, get_provider_decision_url, get_provider_email_by_name


@receiver(post_save, sender=ServiceRequest)
def send_provider_notification_email(sender, instance, created, **kwargs):
    """
    Signal handler: Send email to provider when a new service request is created.
    Generates secure decision tokens and sends acceptance/decline links.
    """
    if created and instance.status == 'pending':
        # Generate secure token for provider decisions
        token = generate_secure_token()
        expires_at = timezone.now() + timedelta(days=7)
        
        # Store token in database
        try:
            RequestDecisionToken.objects.create(
                service_request=instance,
                token=token,
                expires_at=expires_at
            )
        except Exception as e:
            print(f"Error creating decision token: {str(e)}")
            return
        
        # Build context for email templates
        context = {
            'request_id': instance.id,
            'provider_name': instance.provider_name,
            'customer_name': instance.user.get_full_name() or instance.user.username,
            'description': instance.description,
            'date_time': instance.date_time,
            'price_range': instance.price_range,
            'urgent': instance.urgent,
            'created_at': instance.created_at,
            'accept_link': get_provider_decision_url(instance.id, token, 'accept'),
            'decline_link': get_provider_decision_url(instance.id, token, 'decline'),
            'expires_at': expires_at,
        }
        
        # Render email templates
        html_message = render_to_string('emails/request_to_provider_email.html', context)
        text_message = render_to_string('emails/request_to_provider_email.txt', context)
        
        # Send email to provider
        subject = f"New Service Request - Request #{instance.id}"
        
        # Look up provider email by name
        recipient_email = get_provider_email_by_name(instance.provider_name)
        
        if not recipient_email:
            print(f"Warning: Could not find email for provider '{instance.provider_name}'")
            # Fall back to console output
            recipient_email = settings.DEFAULT_FROM_EMAIL
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email],
        )
        email.attach_alternative(html_message, "text/html")
        
        try:
            email.send()
            print(f"Provider notification email sent for request #{instance.id} to {recipient_email}")
        except Exception as e:
            print(f"Error sending provider email: {str(e)}")


@receiver(post_save, sender=ServiceRequest)
def send_acceptance_notification_email(sender, instance, created, **kwargs):
    """
    Signal handler: Send email to customer when provider accepts the request.
    """
    if not created and instance.status == 'accepted' and instance.accepted_at:
        # Build context for email template
        context = {
            'request_id': instance.id,
            'customer_name': instance.user.get_full_name() or instance.user.username,
            'provider_name': instance.provider_name,
            'description': instance.description,
            'date_time': instance.date_time,
            'price_range': instance.price_range,
            'accepted_at': instance.accepted_at,
            'provider_contact': instance.provider.phone if instance.provider else '',
            'provider_email': instance.provider.email if instance.provider else '',
            'dashboard_link': f"{settings.SITE_URL}/requests/view/{instance.id}/",
        }
        
        # Render email templates
        html_message = render_to_string('emails/request_accepted_email.html', context)
        text_message = render_to_string('emails/request_accepted_email.txt', context)
        
        # Send email to customer
        subject = f"Your Service Request Has Been Accepted - Request #{instance.id}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        try:
            email.send()
            print(f"Acceptance notification email sent for request #{instance.id}")
        except Exception as e:
            print(f"Error sending acceptance email: {str(e)}")


@receiver(post_save, sender=ServiceRequest)
def send_decline_notification_email(sender, instance, created, **kwargs):
    """
    Signal handler: Send email to customer when provider declines the request.
    """
    if not created and instance.status == 'declined' and instance.declined_at:
        # Get decline reason display
        decline_reason_display = dict(ServiceRequest.DECLINE_REASON_CHOICES).get(
            instance.decline_reason, 
            'Not specified'
        )
        
        # Build context for email template
        context = {
            'request_id': instance.id,
            'customer_name': instance.user.get_full_name() or instance.user.username,
            'provider_name': instance.provider_name,
            'description': instance.description,
            'date_time': instance.date_time,
            'price_range': instance.price_range,
            'declined_at': instance.declined_at,
            'decline_reason': instance.decline_reason,
            'decline_reason_display': decline_reason_display,
            'decline_message': instance.decline_message,
            'dashboard_link': f"{settings.SITE_URL}/requests/",
        }
        
        # Render email templates
        html_message = render_to_string('emails/request_declined_email.html', context)
        text_message = render_to_string('emails/request_declined_email.txt', context)
        
        # Send email to customer
        subject = f"Service Request Update - Request #{instance.id}"
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[instance.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        try:
            email.send()
            print(f"Decline notification email sent for request #{instance.id}")
        except Exception as e:
            print(f"Error sending decline email: {str(e)}")

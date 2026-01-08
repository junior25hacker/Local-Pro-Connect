"""
Signals for handling ServiceRequest workflow events.
Automatically sends emails when requests are created, accepted, or declined.

Uses async tasks to avoid blocking the request with email sending.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets
from threading import Thread

from .models import ServiceRequest, RequestDecisionToken
from .utils import generate_secure_token, get_provider_decision_url, get_provider_email_by_name, get_address_string


def send_email_async(email_obj):
    """
    Send email in a background thread to avoid blocking the request.
    
    Args:
        email_obj: EmailMultiAlternatives object ready to send
    """
    try:
        email_obj.send()
    except Exception as e:
        print(f"Error sending email in background: {str(e)}")


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
        # Calculate distance
        distance = None
        customer_address = None
        provider_address = None
        
        # Get customer profile
        customer_profile = None
        if hasattr(instance.user, 'user_profile'):
            customer_profile = instance.user.user_profile
            customer_address = get_address_string(customer_profile)
        
        # Get provider profile
        provider_profile = None
        if instance.provider and hasattr(instance.provider, 'provider_profile'):
            provider_profile = instance.provider.provider_profile
            provider_address = get_address_string(provider_profile)
        
        # Calculate distance
        if customer_profile and provider_profile:
            try:
                customer_zip = int(customer_profile.zip_code) if customer_profile.zip_code else 0
                provider_zip = int(provider_profile.zip_code) if provider_profile.zip_code else 0
                zip_diff = abs(customer_zip - provider_zip)
                distance = min(zip_diff * 0.5, 500)  # Cap at 500 miles
            except (ValueError, AttributeError):
                distance = None
        
        context = {
            'request_id': instance.id,
            'provider_name': instance.provider_name,
            'customer_name': instance.user.get_full_name() or instance.user.username,
            'customer_email': instance.user.email,
            'description': instance.description,
            'date_time': instance.date_time,
            'price_range': instance.price_range.label if instance.price_range else None,
            'urgent': instance.urgent,
            'status': instance.status,
            'created_at': instance.created_at,
            'distance': distance,
            'customer_address': customer_address,
            'provider_address': provider_address,
            'company_name': provider_profile.company_name if provider_profile else None,
            'service_type': provider_profile.get_service_type_display() if provider_profile else None,
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
        
        # Send email asynchronously in a background thread to avoid blocking
        # The request will complete immediately while email is sent in the background
        thread = Thread(
            target=send_email_async,
            args=(email,),
            daemon=True  # Don't wait for thread to complete
        )
        thread.start()
        print(f"Provider notification email scheduled for request #{instance.id} to {recipient_email}")


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
            'provider_contact': instance.provider.provider_profile.phone if (instance.provider and hasattr(instance.provider, 'provider_profile')) else '',
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
        
        # Send email asynchronously in a background thread to avoid blocking
        thread = Thread(
            target=send_email_async,
            args=(email,),
            daemon=True
        )
        thread.start()
        print(f"Acceptance notification email scheduled for request #{instance.id}")


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
        
        # Send email asynchronously in a background thread to avoid blocking
        thread = Thread(
            target=send_email_async,
            args=(email,),
            daemon=True
        )
        thread.start()
        print(f"Decline notification email scheduled for request #{instance.id}")

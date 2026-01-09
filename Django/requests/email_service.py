"""
Comprehensive Email Service for ServiceRequest Notifications

This module handles all email communications for the requests workflow:
- Request submission notifications to providers
- Request acceptance notifications to customers
- Request decline notifications to customers
- Customer confirmation of request receipt
- Retry logic for failed emails
- Async sending with background threads

Features:
- Template rendering for HTML and plain text emails
- Error handling and logging
- Email tracking in database
- Retry logic for transient failures
- Support for async/queue-based sending
"""

import logging
import os
from threading import Thread
from datetime import timedelta
from functools import wraps

from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from .models import ServiceRequest, RequestDecisionToken
from .utils import (
    generate_secure_token,
    get_provider_decision_url,
    get_provider_email_by_name,
    get_address_string,
    format_decline_reason,
)
from accounts.models import ProviderProfile, UserProfile

logger = logging.getLogger(__name__)


# ============================================================================
# Async Email Sending
# ============================================================================

def send_email_async(email_obj, max_retries=3, retry_delay=2):
    """
    Send email in a background thread to avoid blocking the request.
    
    Args:
        email_obj: EmailMultiAlternatives object to send
        max_retries: Maximum number of retry attempts
        retry_delay: Delay between retries in seconds
    """
    def _send_with_retry():
        attempt = 0
        while attempt < max_retries:
            try:
                email_obj.send(fail_silently=False)
                logger.info(f"Email sent successfully to {email_obj.to} (attempt {attempt + 1})")
                return
            except Exception as e:
                attempt += 1
                if attempt < max_retries:
                    logger.warning(
                        f"Email send failed (attempt {attempt}/{max_retries}): {str(e)}. "
                        f"Will retry in {retry_delay} seconds..."
                    )
                    import time
                    time.sleep(retry_delay)
                else:
                    logger.error(
                        f"Email send failed after {max_retries} attempts to {email_obj.to}: {str(e)}"
                    )
    
    thread = Thread(
        target=_send_with_retry,
        daemon=True
    )
    thread.start()


# ============================================================================
# Email Sending Functions
# ============================================================================

def send_request_to_provider(service_request, provider_profile=None, async_send=True):
    """
    Send notification email to provider when user submits a service request.
    
    This email includes:
    - Request ID and details
    - Customer information and contact details
    - Service description
    - Distance information
    - Accept/Decline action links with secure tokens
    
    Args:
        service_request: ServiceRequest instance
        provider_profile: ProviderProfile instance (if None, will be looked up by name)
        async_send: Whether to send asynchronously (recommended)
    
    Returns:
        dict: {'success': bool, 'message': str, 'email_sent': bool}
    """
    try:
        # Look up provider if not provided
        if not provider_profile:
            try:
                provider_profile = ProviderProfile.objects.get(
                    company_name=service_request.provider_name
                )
            except ProviderProfile.DoesNotExist:
                logger.warning(
                    f"Provider profile not found for '{service_request.provider_name}' "
                    f"(request #{service_request.id})"
                )
                provider_profile = None
        
        # Get provider email
        provider_email = None
        if provider_profile and provider_profile.user.email:
            provider_email = provider_profile.user.email
        else:
            # Try to look up email by provider name
            provider_email = get_provider_email_by_name(service_request.provider_name)
        
        if not provider_email:
            logger.error(
                f"Could not find provider email for request #{service_request.id} "
                f"(provider: {service_request.provider_name})"
            )
            return {
                'success': False,
                'message': f'Provider email not found for {service_request.provider_name}',
                'email_sent': False,
            }
        
        # Create or get decision token
        decision_token, created = RequestDecisionToken.objects.get_or_create(
            service_request=service_request,
            defaults={
                'token': generate_secure_token(),
                'expires_at': timezone.now() + timedelta(days=7),
            }
        )
        
        # Build decision URLs
        accept_link = get_provider_decision_url(service_request.id, decision_token.token, 'accept')
        decline_link = get_provider_decision_url(service_request.id, decision_token.token, 'decline')
        
        # Get customer profile for distance calculation
        customer_address = None
        distance = None
        try:
            customer_profile = UserProfile.objects.get(user=service_request.user)
            customer_address = get_address_string(customer_profile)
        except ObjectDoesNotExist:
            customer_profile = None
        
        # Get provider address
        provider_address = None
        if provider_profile:
            provider_address = get_address_string(provider_profile)
        
        # Calculate distance (mock for now, based on zip codes)
        if customer_profile and provider_profile:
            try:
                customer_zip = int(customer_profile.zip_code) if customer_profile.zip_code else 0
                provider_zip = int(provider_profile.zip_code) if provider_profile.zip_code else 0
                zip_diff = abs(customer_zip - provider_zip)
                distance = min(zip_diff * 0.5, 500)  # Cap at 500 miles
            except (ValueError, AttributeError, TypeError):
                distance = None
        
        # Get provider display name
        provider_display_name = (
            provider_profile.user.get_full_name() 
            if provider_profile and provider_profile.user.get_full_name()
            else service_request.provider_name
        )
        
        # Build email context
        context = {
            'request_id': service_request.id,
            'provider_name': provider_display_name,
            'customer_name': service_request.user.get_full_name() or service_request.user.username,
            'customer_email': service_request.user.email,
            'description': service_request.description,
            'date_time': service_request.date_time,
            'price_range': service_request.price_range.label if service_request.price_range else None,
            'offered_price': service_request.offered_price,
            'urgent': service_request.urgent,
            'status': service_request.status,
            'created_at': service_request.created_at,
            'distance': distance,
            'customer_address': customer_address,
            'provider_address': provider_address,
            'company_name': provider_profile.company_name if provider_profile else None,
            'service_type': (
                dict(ProviderProfile.SERVICE_CHOICES).get(provider_profile.service_type)
                if provider_profile else None
            ),
            'accept_link': accept_link,
            'decline_link': decline_link,
            'expires_at': decision_token.expires_at,
            'site_url': settings.SITE_URL,
        }
        
        # Render email templates
        subject = f"New Service Request - {service_request.provider_name}"
        text_message = render_to_string('emails/request_to_provider_email.txt', context)
        html_message = render_to_string('emails/request_to_provider_email.html', context)
        
        # Create email object
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[provider_email],
        )
        email.attach_alternative(html_message, "text/html")
        
        # Send email
        if async_send:
            send_email_async(email)
        else:
            email.send(fail_silently=False)
        
        # Update request to mark email as sent
        service_request.email_sent_to_provider = True
        service_request.email_sent_to_provider_timestamp = timezone.now()
        service_request.save(update_fields=['email_sent_to_provider', 'email_sent_to_provider_timestamp'])
        
        logger.info(
            f"Provider notification email sent for request #{service_request.id} "
            f"to {provider_email}"
        )
        
        return {
            'success': True,
            'message': f'Provider notification email sent to {provider_email}',
            'email_sent': True,
        }
        
    except Exception as e:
        logger.error(
            f"Failed to send provider notification for request #{service_request.id}: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'message': f'Failed to send provider notification: {str(e)}',
            'email_sent': False,
        }


def send_user_confirmation_email(service_request, async_send=True):
    """
    Send confirmation email to user after they submit a request.
    
    This email includes:
    - Request confirmation
    - Request ID
    - Provider name
    - Service description
    - Expected follow-up information
    
    Args:
        service_request: ServiceRequest instance
        async_send: Whether to send asynchronously
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        context = {
            'user_name': service_request.user.get_full_name() or service_request.user.username,
            'request_id': service_request.id,
            'provider_name': service_request.provider_name,
            'description': service_request.description,
            'created_at': service_request.created_at,
            'dashboard_link': f"{settings.SITE_URL}/requests/list/",
            'site_url': settings.SITE_URL,
        }
        
        subject = "Request Submitted Successfully"
        text_message = render_to_string('emails/request_confirmation_email.txt', context)
        html_message = render_to_string('emails/request_confirmation_email.html', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[service_request.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        if async_send:
            send_email_async(email)
        else:
            email.send(fail_silently=False)
        
        service_request.email_sent_to_user = True
        service_request.email_sent_to_user_timestamp = timezone.now()
        service_request.save(update_fields=['email_sent_to_user', 'email_sent_to_user_timestamp'])
        
        logger.info(f"User confirmation email sent for request #{service_request.id}")
        
        return {
            'success': True,
            'message': 'Confirmation email sent to user',
        }
        
    except Exception as e:
        logger.error(
            f"Failed to send user confirmation for request #{service_request.id}: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'message': f'Failed to send confirmation email: {str(e)}',
        }


def send_acceptance_email(service_request, async_send=True):
    """
    Send notification email to customer when provider accepts request.
    
    This email includes:
    - Acceptance confirmation
    - Provider details and contact information
    - Next steps
    - Request details
    
    Args:
        service_request: ServiceRequest instance (status='accepted')
        async_send: Whether to send asynchronously
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        if not service_request.provider:
            raise ValueError("Service request does not have an assigned provider")
        
        provider = service_request.provider
        provider_profile = None
        
        try:
            provider_profile = ProviderProfile.objects.get(user=provider)
        except ProviderProfile.DoesNotExist:
            pass
        
        context = {
            'customer_name': service_request.user.get_full_name() or service_request.user.username,
            'provider_name': provider.get_full_name() or provider.username,
            'provider_company': provider_profile.company_name if provider_profile else None,
            'provider_contact': provider_profile.phone if provider_profile else provider.email,
            'provider_email': provider.email,
            'request_id': service_request.id,
            'description': service_request.description,
            'date_time': service_request.date_time,
            'price_range': service_request.price_range.label if service_request.price_range else None,
            'accepted_at': service_request.accepted_at,
            'dashboard_link': f"{settings.SITE_URL}/requests/list/",
            'site_url': settings.SITE_URL,
        }
        
        subject = "Service Request Accepted"
        text_message = render_to_string('emails/request_accepted_email.txt', context)
        html_message = render_to_string('emails/request_accepted_email.html', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[service_request.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        if async_send:
            send_email_async(email)
        else:
            email.send(fail_silently=False)
        
        service_request.email_response_timestamp = timezone.now()
        service_request.save(update_fields=['email_response_timestamp'])
        
        logger.info(
            f"Acceptance notification email sent for request #{service_request.id} "
            f"to {service_request.user.email}"
        )
        
        return {
            'success': True,
            'message': 'Acceptance email sent to customer',
        }
        
    except Exception as e:
        logger.error(
            f"Failed to send acceptance email for request #{service_request.id}: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'message': f'Failed to send acceptance email: {str(e)}',
        }


def send_decline_email(service_request, decline_reason=None, decline_message=None, async_send=True):
    """
    Send notification email to customer when provider declines request.
    
    This email includes:
    - Decline confirmation
    - Reason for decline (if provided)
    - Custom message from provider (if provided)
    - Suggestion to contact other providers
    - Request details
    
    Args:
        service_request: ServiceRequest instance (status='declined')
        decline_reason: Reason code for decline
        decline_message: Custom message from provider
        async_send: Whether to send asynchronously
    
    Returns:
        dict: {'success': bool, 'message': str}
    """
    try:
        provider = service_request.provider
        if not provider:
            # Try to infer provider from provider_name
            provider_name = service_request.provider_name
        else:
            provider_name = provider.get_full_name() or provider.username
        
        formatted_reason = format_decline_reason(decline_reason or service_request.decline_reason)
        
        context = {
            'customer_name': service_request.user.get_full_name() or service_request.user.username,
            'provider_name': provider_name,
            'decline_reason': formatted_reason,
            'decline_message': decline_message or service_request.decline_message,
            'request_id': service_request.id,
            'description': service_request.description,
            'declined_at': service_request.declined_at,
            'dashboard_link': f"{settings.SITE_URL}/requests/list/",
            'browse_link': f"{settings.SITE_URL}/professionals/",
            'site_url': settings.SITE_URL,
        }
        
        subject = "Service Request Update"
        text_message = render_to_string('emails/request_declined_email.txt', context)
        html_message = render_to_string('emails/request_declined_email.html', context)
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=text_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[service_request.user.email],
        )
        email.attach_alternative(html_message, "text/html")
        
        if async_send:
            send_email_async(email)
        else:
            email.send(fail_silently=False)
        
        service_request.email_response_timestamp = timezone.now()
        service_request.save(update_fields=['email_response_timestamp'])
        
        logger.info(
            f"Decline notification email sent for request #{service_request.id} "
            f"to {service_request.user.email}"
        )
        
        return {
            'success': True,
            'message': 'Decline email sent to customer',
        }
        
    except Exception as e:
        logger.error(
            f"Failed to send decline email for request #{service_request.id}: {str(e)}",
            exc_info=True
        )
        return {
            'success': False,
            'message': f'Failed to send decline email: {str(e)}',
        }


# ============================================================================
# Email Configuration Testing
# ============================================================================

def test_email_configuration(recipient_email=None):
    """
    Test the email configuration by sending a test email.
    
    Args:
        recipient_email: Email address to send test to (defaults to DEFAULT_FROM_EMAIL)
    
    Returns:
        dict: {'success': bool, 'message': str, 'config': dict}
    """
    try:
        recipient = recipient_email or settings.DEFAULT_FROM_EMAIL
        
        subject = "LocaPro Email Configuration Test"
        message = """
This is a test email to verify your SMTP configuration is working correctly.

If you received this email, your email system is configured properly!

Configuration Details:
- Backend: {backend}
- Host: {host}:{port}
- From Email: {from_email}
- Use SSL: {use_ssl}
- Use TLS: {use_tls}

---
LocaPro Email System
        """.format(
            backend=settings.EMAIL_BACKEND.split('.')[-1],
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            from_email=settings.DEFAULT_FROM_EMAIL,
            use_ssl=settings.EMAIL_USE_SSL,
            use_tls=settings.EMAIL_USE_TLS,
        )
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient],
            fail_silently=False,
        )
        
        config_info = {
            'email_backend': settings.EMAIL_BACKEND,
            'email_host': settings.EMAIL_HOST,
            'email_port': settings.EMAIL_PORT,
            'email_use_tls': settings.EMAIL_USE_TLS,
            'email_use_ssl': settings.EMAIL_USE_SSL,
            'default_from_email': settings.DEFAULT_FROM_EMAIL,
            'recipient': recipient,
        }
        
        logger.info("Email configuration test successful")
        
        return {
            'success': True,
            'message': 'Test email sent successfully!',
            'config': config_info,
        }
        
    except Exception as e:
        logger.error(f"Email configuration test failed: {str(e)}", exc_info=True)
        
        config_info = {
            'email_backend': settings.EMAIL_BACKEND,
            'email_host': settings.EMAIL_HOST,
            'email_port': settings.EMAIL_PORT,
            'email_use_tls': settings.EMAIL_USE_TLS,
            'email_use_ssl': settings.EMAIL_USE_SSL,
            'default_from_email': settings.DEFAULT_FROM_EMAIL,
            'error': str(e),
        }
        
        return {
            'success': False,
            'message': f'Email configuration test failed: {str(e)}',
            'config': config_info,
        }


def get_email_configuration_info():
    """
    Get current email configuration information.
    
    Returns:
        dict: Current email configuration
    """
    return {
        'backend': settings.EMAIL_BACKEND,
        'host': settings.EMAIL_HOST,
        'port': settings.EMAIL_PORT,
        'use_tls': settings.EMAIL_USE_TLS,
        'use_ssl': settings.EMAIL_USE_SSL,
        'from_email': settings.DEFAULT_FROM_EMAIL,
        'host_user': settings.EMAIL_HOST_USER[:5] + '***' if settings.EMAIL_HOST_USER else 'Not set',
        'smtp_provider': os.environ.get('SMTP_PROVIDER', 'Not configured'),
    }

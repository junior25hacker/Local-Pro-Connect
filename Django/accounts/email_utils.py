"""
Email utilities for sending notifications to users and providers.
Handles both text and HTML emails with proper error handling.
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_profile_update_email(provider_profile):
    """
    Send notification email when provider updates their profile.
    
    Args:
        provider_profile: ProviderProfile instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'provider_name': provider_profile.user.first_name or provider_profile.user.username,
            'company_name': provider_profile.company_name,
            'service_type': provider_profile.get_service_type_display(),
            'service_type_display': dict(provider_profile.SERVICE_CHOICES).get(
                provider_profile.service_type, provider_profile.service_type
            ),
            'city': provider_profile.city,
            'state': provider_profile.state,
            'years_experience': provider_profile.years_experience,
            'is_verified': provider_profile.is_verified,
            'profile_url': f"{settings.SITE_URL}/professionals/{provider_profile.id}/",
        }
        
        # Render email templates
        subject = f"Profile Updated - {provider_profile.company_name}"
        text_message = render_to_string('emails/profile_update_email.txt', context)
        html_message = render_to_string('emails/profile_update_email.html', context)
        
        # Send email
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [provider_profile.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Profile update email sent to {provider_profile.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send profile update email: {str(e)}")
        return False


def send_request_submitted_email(service_request, provider_profile):
    """
    Send notification email when a new request is submitted to a provider.
    Uses existing request_to_provider_email template.
    
    Args:
        service_request: ServiceRequest instance
        provider_profile: ProviderProfile instance
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'provider_name': provider_profile.user.first_name or provider_profile.user.username,
            'user_name': service_request.user.first_name or service_request.user.username,
            'service_description': service_request.description,
            'request_id': service_request.id,
            'request_url': f"{settings.SITE_URL}/requests/{service_request.id}/",
        }
        
        subject = f"New Service Request Submitted - LocaProConnect"
        text_message = render_to_string('emails/request_to_provider_email.txt', context)
        html_message = render_to_string('emails/request_to_provider_email.html', context)
        
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [provider_profile.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Request submitted email sent to {provider_profile.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send request submitted email: {str(e)}")
        return False


def send_request_accepted_email(service_request):
    """
    Send notification email when provider accepts a service request.
    Uses existing request_accepted_email template.
    
    Args:
        service_request: ServiceRequest instance (with status='accepted')
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'user_name': service_request.user.first_name or service_request.user.username,
            'provider_name': service_request.provider.user.first_name or service_request.provider.user.username,
            'provider_company': service_request.provider.company_name,
            'request_id': service_request.id,
            'dashboard_url': f"{settings.SITE_URL}/requests/list/",
        }
        
        subject = f"Service Request Accepted - LocaProConnect"
        text_message = render_to_string('emails/request_accepted_email.txt', context)
        html_message = render_to_string('emails/request_accepted_email.html', context)
        
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [service_request.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Request accepted email sent to {service_request.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send request accepted email: {str(e)}")
        return False


def send_request_declined_email(service_request, decline_reason=None, decline_message=None):
    """
    Send notification email when provider declines a service request.
    Uses existing request_declined_email template.
    
    Args:
        service_request: ServiceRequest instance (with status='declined')
        decline_reason: Reason for declining
        decline_message: Custom message from provider
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        context = {
            'user_name': service_request.user.first_name or service_request.user.username,
            'provider_name': service_request.provider.user.first_name or service_request.provider.user.username,
            'provider_company': service_request.provider.company_name,
            'decline_reason': decline_reason or service_request.decline_reason,
            'decline_message': decline_message or service_request.decline_message,
            'request_id': service_request.id,
            'dashboard_url': f"{settings.SITE_URL}/requests/list/",
        }
        
        subject = f"Service Request Update - LocaProConnect"
        text_message = render_to_string('emails/request_declined_email.txt', context)
        html_message = render_to_string('emails/request_declined_email.html', context)
        
        email = EmailMultiAlternatives(
            subject,
            text_message,
            settings.DEFAULT_FROM_EMAIL,
            [service_request.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        
        logger.info(f"Request declined email sent to {service_request.user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send request declined email: {str(e)}")
        return False


def test_email_configuration():
    """
    Test the email configuration by sending a test email.
    
    Returns:
        dict: {'success': bool, 'message': str, 'config': dict}
    """
    try:
        # Prepare test email
        subject = "LocaProConnect - Email Configuration Test"
        message = "This is a test email to verify your SMTP configuration is working correctly."
        
        # Send test email to DEFAULT_FROM_EMAIL
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        config_info = {
            'email_backend': settings.EMAIL_BACKEND,
            'email_host': settings.EMAIL_HOST,
            'email_port': settings.EMAIL_PORT,
            'email_use_tls': settings.EMAIL_USE_TLS,
            'email_use_ssl': settings.EMAIL_USE_SSL,
            'default_from_email': settings.DEFAULT_FROM_EMAIL,
        }
        
        return {
            'success': True,
            'message': 'Test email sent successfully! Email configuration is working.',
            'config': config_info,
        }
        
    except Exception as e:
        config_info = {
            'email_backend': settings.EMAIL_BACKEND,
            'email_host': settings.EMAIL_HOST,
            'email_port': settings.EMAIL_PORT,
            'email_use_tls': settings.EMAIL_USE_TLS,
            'email_use_ssl': settings.EMAIL_USE_SSL,
            'default_from_email': settings.DEFAULT_FROM_EMAIL,
            'error': str(e),
        }
        
        logger.error(f"Email configuration test failed: {str(e)}")
        return {
            'success': False,
            'message': f'Failed to send test email: {str(e)}',
            'config': config_info,
        }

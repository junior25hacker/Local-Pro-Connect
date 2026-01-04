"""
Utility functions for the requests app.
Handles token generation, URL building, and other helper functions.
"""

import secrets
import hmac
import hashlib
from django.conf import settings
from django.urls import reverse
from django.utils.http import urlencode


def generate_secure_token(length=32):
    """
    Generate a secure random token for provider decision links.
    Uses Python's secrets module for cryptographic randomness.
    
    Args:
        length: Length of the token (default 32 characters)
        
    Returns:
        A secure random token string
    """
    return secrets.token_urlsafe(length)


def create_signed_token(data, secret=None):
    """
    Create a signed token using HMAC for secure data verification.
    
    Args:
        data: The data to sign (should be a string)
        secret: Secret key (defaults to Django's SECRET_KEY)
        
    Returns:
        A signed token that can be verified
    """
    if secret is None:
        secret = settings.SECRET_KEY
    
    signature = hmac.new(
        secret.encode(),
        data.encode(),
        hashlib.sha256
    ).hexdigest()
    
    return f"{data}.{signature}"


def verify_signed_token(token, secret=None):
    """
    Verify a signed token and return the original data if valid.
    
    Args:
        token: The signed token to verify
        secret: Secret key (defaults to Django's SECRET_KEY)
        
    Returns:
        The original data if valid, None if invalid
    """
    if secret is None:
        secret = settings.SECRET_KEY
    
    try:
        data, signature = token.rsplit('.', 1)
        expected_signature = hmac.new(
            secret.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(signature, expected_signature):
            return data
        return None
    except (ValueError, AttributeError):
        return None


def get_provider_decision_url(request_id, token, action):
    """
    Generate a secure decision URL for providers to accept or decline requests.
    
    Args:
        request_id: The ServiceRequest ID
        token: The secure token
        action: Either 'accept' or 'decline'
        
    Returns:
        The full decision URL
    """
    # Build the URL path
    url_path = reverse('requests:provider_decision', kwargs={
        'request_id': request_id,
        'action': action,
        'token': token,
    })
    
    # Get the full URL with domain
    site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
    return f"{site_url}{url_path}"


def get_provider_email_by_name(provider_name):
    """
    Look up a provider's email address by their name.
    This is a placeholder implementation.
    
    In production, you would:
    1. Search the ProviderProfile table for matching providers
    2. Return the associated user's email
    3. Handle cases where no provider is found
    
    Args:
        provider_name: The name of the provider
        
    Returns:
        The provider's email address or None
    """
    # Import here to avoid circular imports
    from accounts.models import ProviderProfile
    
    try:
        provider = ProviderProfile.objects.filter(
            company_name__icontains=provider_name
        ).first()
        
        if provider and provider.user.email:
            return provider.user.email
    except Exception as e:
        print(f"Error looking up provider email: {str(e)}")
    
    return None


def format_decline_reason(reason_code):
    """
    Format decline reason code into a human-readable message.
    
    Args:
        reason_code: The decline reason code
        
    Returns:
        A human-readable decline reason
    """
    reasons = {
        'price': 'Price too low',
        'distance': 'Too far away',
        'other': 'Other reason',
        'no_reason': 'No reason provided',
    }
    return reasons.get(reason_code, 'Unknown reason')

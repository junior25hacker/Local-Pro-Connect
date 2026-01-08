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
    Look up a provider's email address by their name using multiple strategies.
    
    Search strategy (in order):
    1. Exact match on company_name (case-insensitive)
    2. Partial match on company_name (case-insensitive contains)
    3. Match on user.first_name or user.last_name
    4. Return None if no match found
    
    Args:
        provider_name: The name of the provider (company name or person name)
        
    Returns:
        The provider's email address or None
    """
    # Import here to avoid circular imports
    from accounts.models import ProviderProfile
    from django.contrib.auth.models import User
    from django.db.models import Q
    
    if not provider_name or not provider_name.strip():
        return None
    
    provider_name_lower = provider_name.lower().strip()
    
    try:
        # Strategy 1: Try exact match on company_name (case-insensitive)
        provider = ProviderProfile.objects.filter(
            company_name__iexact=provider_name_lower
        ).select_related('user').first()
        
        if provider and provider.user and provider.user.email:
            print(f"Found provider '{provider_name}' by exact company name match: {provider.user.email}")
            return provider.user.email
        
        # Strategy 2: Try partial match on company_name
        provider = ProviderProfile.objects.filter(
            company_name__icontains=provider_name_lower
        ).select_related('user').first()
        
        if provider and provider.user and provider.user.email:
            print(f"Found provider '{provider_name}' by company name contains: {provider.user.email}")
            return provider.user.email
        
        # Strategy 3: Try matching on user first_name or last_name
        provider = ProviderProfile.objects.filter(
            Q(user__first_name__icontains=provider_name_lower) |
            Q(user__last_name__icontains=provider_name_lower)
        ).select_related('user').first()
        
        if provider and provider.user and provider.user.email:
            print(f"Found provider '{provider_name}' by user name match: {provider.user.email}")
            return provider.user.email
        
        print(f"Warning: Could not find provider email for '{provider_name}' using any lookup strategy")
        
    except Exception as e:
        print(f"Error looking up provider email for '{provider_name}': {str(e)}")
    
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


def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two geographic coordinates using the Haversine formula.
    
    Args:
        lat1: Latitude of first point
        lon1: Longitude of first point
        lat2: Latitude of second point
        lon2: Longitude of second point
        
    Returns:
        Distance in miles (float)
    """
    from math import radians, sin, cos, sqrt, atan2
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    
    # Earth's radius in miles
    radius_miles = 3959
    distance = radius_miles * c
    
    return round(distance, 1)


def get_address_string(profile):
    """
    Get a formatted address string from a user or provider profile.
    
    Args:
        profile: UserProfile or ProviderProfile instance
        
    Returns:
        Formatted address string
    """
    address_parts = []
    
    if hasattr(profile, 'business_address') and profile.business_address:
        address_parts.append(profile.business_address)
    elif hasattr(profile, 'address') and profile.address:
        address_parts.append(profile.address)
    
    if profile.city:
        address_parts.append(profile.city)
    
    if profile.state:
        address_parts.append(profile.state)
    
    if profile.zip_code:
        address_parts.append(profile.zip_code)
    
    return ', '.join(address_parts) if address_parts else 'Address not available'

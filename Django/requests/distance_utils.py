"""
Distance calculation utilities using the Haversine formula.
Calculates distance between two points on Earth using their latitude and longitude coordinates.
"""

import logging
import math
from decimal import Decimal
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    
    Formula: d = 2r × arcsin(√(sin²((φ₂-φ₁)/2) + cos(φ₁) × cos(φ₂) × sin²((λ₂-λ₁)/2)))
    
    Args:
        lat1 (float): Latitude of first point in degrees
        lon1 (float): Longitude of first point in degrees
        lat2 (float): Latitude of second point in degrees
        lon2 (float): Longitude of second point in degrees
    
    Returns:
        float: Distance in kilometers, rounded to 1 decimal place
    
    Raises:
        ValueError: If coordinates are invalid
    """
    # Validate coordinates
    if not (-90 <= lat1 <= 90) or not (-90 <= lat2 <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= lon1 <= 180) or not (-180 <= lon2 <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    
    # Earth's radius in kilometers
    R = 6371.0
    
    # Convert degrees to radians
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(Δφ / 2) ** 2 + 
         math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    # Calculate distance and round to 1 decimal place
    distance = R * c
    return round(distance, 1)


def calculate_request_distance(service_request, provider_profile) -> Optional[float]:
    """
    Calculate distance between a service request location and provider business location.
    
    Args:
        service_request: ServiceRequest instance with latitude/longitude
        provider_profile: ProviderProfile instance with latitude/longitude
    
    Returns:
        Optional[float]: Distance in kilometers rounded to 1 decimal, or None if coordinates missing
    """
    # Check if both request and provider have coordinates
    if not (service_request.latitude and service_request.longitude):
        return None
    
    if not (provider_profile.latitude and provider_profile.longitude):
        return None
    
    try:
        # Convert Decimal to float for calculation
        request_lat = float(service_request.latitude)
        request_lon = float(service_request.longitude)
        provider_lat = float(provider_profile.latitude)
        provider_lon = float(provider_profile.longitude)
        
        return haversine_distance(request_lat, request_lon, provider_lat, provider_lon)
    
    except (ValueError, TypeError):
        logger.exception("Error calculating distance")
        return None


def get_providers_within_radius(request_lat: float, request_lon: float, 
                               max_distance_km: float = 50.0) -> list:
    """
    Get providers within a specified radius of a request location.
    
    Args:
        request_lat (float): Request latitude
        request_lon (float): Request longitude
        max_distance_km (float): Maximum distance in kilometers (default: 50km)
    
    Returns:
        list: List of tuples (provider_profile, distance_km) sorted by distance
    """
    from accounts.models import ProviderProfile
    
    # Get all providers with coordinates
    providers_with_location = ProviderProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('user')
    
    providers_with_distance = []
    
    for provider in providers_with_location:
        try:
            distance = haversine_distance(
                request_lat, request_lon,
                float(provider.latitude), float(provider.longitude)
            )
            
            if distance <= max_distance_km:
                providers_with_distance.append((provider, distance))
        
        except ValueError:
            # Skip providers with invalid coordinates
            continue
    
    # Sort by distance (closest first)
    providers_with_distance.sort(key=lambda x: x[1])
    
    return providers_with_distance


def format_distance_display(distance_km: Optional[float]) -> str:
    """Format distance for display in notifications and UI.

    Notes:
        - Keep formatting stable for UI + tests.
        - Do not insert a space between value and unit (e.g. "3.3km away").
        - Avoid trailing ".0" when distance is a whole number.
    """
    if distance_km is None:
        return "Distance not available"

    if distance_km < 1.0:
        return f"{int(distance_km * 1000)}m away"

    # Always show one decimal place and include a space before unit (matches UI/tests)
    return f"{float(distance_km):.1f} km away"


def calculate_priority_score(service_request) -> int:
    """
    Calculate priority score for request ordering in provider queues.
    Higher score = higher priority.
    
    Factors:
    - Urgent requests: +100 points
    - Distance: closer = more points (max 50 points)
    - Time since creation: older = more points (max 30 points)
    
    Args:
        service_request: ServiceRequest instance
    
    Returns:
        int: Priority score (0-180)
    """
    from django.utils import timezone
    
    score = 0
    
    # Urgent requests get highest priority
    if service_request.urgent:
        score += 100
    
    # Distance bonus (if available)
    if hasattr(service_request, 'distance_km') and service_request.distance_km is not None:
        # Closer requests get more points (50 points at 0km, decreasing to 0 at 50km+)
        # Ensure Decimal is handled correctly
        distance_km = float(service_request.distance_km)
        distance_score = max(0.0, 50.0 - distance_km)
        score += int(distance_score)
    
    # Time bonus (older requests get slight priority)
    created_at = getattr(service_request, 'created_at', None) or getattr(service_request, 'created', None)
    if created_at:
        # Ensure timezone-aware datetime for consistent behavior
        if timezone.is_naive(created_at):
            created_at = timezone.make_aware(created_at, timezone.get_current_timezone())
        hours_old = max(0.0, (timezone.now() - created_at).total_seconds() / 3600)
        time_score = min(30.0, hours_old * 2.0)  # 2 points per hour, max 30
        score += int(time_score)
    
    return score
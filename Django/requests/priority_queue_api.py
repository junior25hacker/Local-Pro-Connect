"""
Priority Queue API for Provider Dashboard.

Provides endpoints for providers to view service requests ordered by:
1. Urgency (urgent flag)
2. Distance (closer = higher priority)
3. Age (older = higher priority)

Priority Score: 0-180
- Urgent bonus: +100
- Distance bonus: +50 (closer is better)
- Time bonus: +30 (older is prioritized)
"""

import logging
import json
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q

from .models import ServiceRequest
from .distance_utils import (
    calculate_request_distance,
    format_distance_display,
    calculate_priority_score,
    get_providers_within_radius
)
from accounts.models import ProviderProfile

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def api_provider_pending_requests(request):
    """
    Get all pending requests ordered by priority score.
    
    Endpoint: GET /api/requests/provider/pending/
    
    Query Parameters:
    - service_type: Filter by service type (optional)
    - max_distance_km: Maximum distance in km (default: 50)
    - include_urgent_only: Show only urgent requests (default: false)
    - limit: Number of results (default: 50, max: 200)
    
    Returns:
    {
        "success": true,
        "requests": [
            {
                "id": 1,
                "description": "Pipe repair needed",
                "urgent": true,
                "distance_km": 2.5,
                "distance_display": "2.5 km away",
                "offered_price": 50000,
                "priority_score": 154,
                "priority_tier": "HIGHEST",
                "created_at": "2025-02-07T10:30:00Z",
                "user": {
                    "id": 5,
                    "name": "John Doe",
                    "phone": "+237123456789"
                },
                "photos": [
                    {"url": "/media/request_photos/...", "id": 1}
                ]
            },
            ...
        ],
        "total": 12,
        "summary": {
            "urgent_count": 2,
            "regular_count": 10,
            "avg_distance": 15.3
        }
    }
    """
    try:
        user = request.user
        
        # Verify user is a provider
        if not hasattr(user, 'provider_profile'):
            return JsonResponse({
                'success': False,
                'error': 'Only service providers can access this endpoint.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        provider_profile = user.provider_profile
        
        # Verify provider has location set
        if not (provider_profile.latitude and provider_profile.longitude):
            return JsonResponse({
                'success': False,
                'error': 'Provider location not set. Please update your business location.',
                'error_code': 'MISSING_LOCATION'
            }, status=400)
        
        # Parse query parameters
        service_type = request.GET.get('service_type', None)
        max_distance_km = float(request.GET.get('max_distance_km', 50.0))
        include_urgent_only = request.GET.get('include_urgent_only', 'false').lower() == 'true'
        limit = min(int(request.GET.get('limit', 50)), 200)
        
        # Get pending requests
        queryset = ServiceRequest.objects.filter(
            status='pending'
        ).select_related(
            'user',
            'user__user_profile',
            'price_range'
        ).prefetch_related('photos')
        
        # Filter by service type if specified
        if service_type:
            queryset = queryset.filter(provider_name__iexact=service_type)
        
        # Filter by urgent flag if requested
        if include_urgent_only:
            queryset = queryset.filter(urgent=True)
        
        # Calculate priority for each request
        requests_with_priority = []
        
        for service_request in queryset:
            try:
                # Calculate distance
                distance_km = None
                if service_request.has_location():
                    distance_km = calculate_request_distance(
                        service_request,
                        provider_profile
                    )
                
                # Skip requests beyond max distance
                if distance_km and distance_km > max_distance_km:
                    continue
                
                # Attach distance to request object for priority calculation
                service_request.distance_km = distance_km
                
                # Calculate priority score
                priority_score = calculate_priority_score(service_request)
                
                # Determine priority tier for UI
                if priority_score >= 140:
                    priority_tier = 'HIGHEST'
                elif priority_score >= 100:
                    priority_tier = 'HIGH'
                elif priority_score >= 50:
                    priority_tier = 'MEDIUM'
                else:
                    priority_tier = 'LOW'
                
                requests_with_priority.append({
                    'request': service_request,
                    'priority_score': priority_score,
                    'priority_tier': priority_tier,
                    'distance_km': distance_km
                })
            
            except Exception as e:
                logger.error(f"Error calculating priority for request {service_request.id}: {e}")
                continue
        
        # Sort by priority score (descending = highest first)
        requests_with_priority.sort(
            key=lambda x: x['priority_score'],
            reverse=True
        )
        
        # Apply limit
        requests_with_priority = requests_with_priority[:limit]
        
        # Serialize response
        results = []
        urgent_count = 0
        regular_count = 0
        total_distance = 0
        
        for item in requests_with_priority:
            service_request = item['request']
            distance_km = item['distance_km']
            priority_score = item['priority_score']
            priority_tier = item['priority_tier']
            
            # Count urgent vs regular
            if service_request.urgent:
                urgent_count += 1
            else:
                regular_count += 1
            
            # Accumulate distance for average
            if distance_km:
                total_distance += distance_km
            
            # Get user info
            user_name = service_request.user.get_full_name() or service_request.user.username
            user_phone = ''
            if hasattr(service_request.user, 'user_profile'):
                user_phone = service_request.user.user_profile.phone or ''
            
            result_item = {
                'id': service_request.id,
                'description': service_request.description,
                'urgent': service_request.urgent,
                'distance_km': round(distance_km, 1) if distance_km else None,
                'distance_display': format_distance_display(distance_km),
                'offered_price': float(service_request.offered_price or 0),
                'priority_score': priority_score,
                'priority_tier': priority_tier,
                'created_at': service_request.created_at.isoformat(),
                'address': service_request.address_string,
                'user': {
                    'id': service_request.user.id,
                    'name': user_name,
                    'phone': user_phone,
                    'profile_picture': (
                        service_request.user.user_profile.profile_picture.url
                        if hasattr(service_request.user, 'user_profile') 
                        and service_request.user.user_profile.profile_picture
                        else None
                    )
                },
                'photos': [
                    {
                        'url': photo.image.url,
                        'id': photo.id,
                        'created_at': photo.created_at.isoformat()
                    }
                    for photo in service_request.photos.all()[:3]
                ]
            }
            
            results.append(result_item)
        
        # Calculate summary stats
        avg_distance = (
            round(total_distance / len(requests_with_priority), 1)
            if requests_with_priority else 0
        )
        
        logger.info(
            f"Provider {user.username} viewed {len(results)} pending requests. "
            f"Urgent: {urgent_count}, Regular: {regular_count}"
        )
        
        return JsonResponse({
            'success': True,
            'requests': results,
            'total': len(results),
            'summary': {
                'urgent_count': urgent_count,
                'regular_count': regular_count,
                'avg_distance_km': avg_distance,
                'provider_location': {
                    'latitude': float(provider_profile.latitude),
                    'longitude': float(provider_profile.longitude)
                }
            }
        })
    
    except ValueError as e:
        logger.error(f"Validation error in priority queue: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Invalid parameter: {str(e)}',
            'error_code': 'VALIDATION_ERROR'
        }, status=400)
    
    except Exception as e:
        logger.error(f"Error fetching priority queue: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching requests.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def api_request_priority_details(request, request_id):
    """
    Get detailed priority information for a specific request.
    
    Endpoint: GET /api/requests/{id}/priority-details/
    
    Returns:
    {
        "success": true,
        "request_id": 1,
        "priority_score": 154,
        "priority_tier": "HIGHEST",
        "score_breakdown": {
            "urgent_bonus": 100,
            "distance_bonus": 49,
            "time_bonus": 5,
            "total": 154
        },
        "factors": {
            "is_urgent": true,
            "distance_km": 2.5,
            "hours_old": 0.5,
            "created_at": "2025-02-07T10:30:00Z"
        }
    }
    """
    try:
        user = request.user
        
        # Verify user is a provider
        if not hasattr(user, 'provider_profile'):
            return JsonResponse({
                'success': False,
                'error': 'Only service providers can access this endpoint.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        provider_profile = user.provider_profile
        service_request = get_object_or_404(ServiceRequest, id=request_id, status='pending')
        
        # Calculate distance
        distance_km = None
        if service_request.has_location() and provider_profile.latitude and provider_profile.longitude:
            distance_km = calculate_request_distance(service_request, provider_profile)
        
        # Calculate score breakdown
        urgent_bonus = 100 if service_request.urgent else 0
        
        distance_bonus = 0
        if distance_km is not None:
            distance_bonus = max(0, int(50 - distance_km))
        
        hours_old = (timezone.now() - service_request.created_at).total_seconds() / 3600
        time_bonus = min(30, int(hours_old * 2))
        
        total_score = urgent_bonus + distance_bonus + time_bonus
        
        # Determine priority tier
        if total_score >= 140:
            priority_tier = 'HIGHEST'
        elif total_score >= 100:
            priority_tier = 'HIGH'
        elif total_score >= 50:
            priority_tier = 'MEDIUM'
        else:
            priority_tier = 'LOW'
        
        logger.info(f"Provider {user.username} viewed priority details for request {request_id}")
        
        return JsonResponse({
            'success': True,
            'request_id': request_id,
            'priority_score': total_score,
            'priority_tier': priority_tier,
            'score_breakdown': {
                'urgent_bonus': urgent_bonus,
                'distance_bonus': distance_bonus,
                'time_bonus': time_bonus,
                'total': total_score
            },
            'factors': {
                'is_urgent': service_request.urgent,
                'distance_km': round(distance_km, 1) if distance_km else None,
                'distance_display': format_distance_display(distance_km),
                'hours_old': round(hours_old, 2),
                'created_at': service_request.created_at.isoformat()
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching priority details for request {request_id}: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching priority details.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def api_providers_within_radius(request):
    """
    Get list of providers within a specified radius from a request location.
    
    Endpoint: GET /api/requests/providers-nearby/
    
    Query Parameters:
    - latitude: Request latitude (required)
    - longitude: Request longitude (required)
    - max_distance_km: Maximum distance (default: 50)
    - service_type: Filter by service type (optional)
    
    Returns:
    {
        "success": true,
        "providers": [
            {
                "provider_id": 3,
                "company_name": "John's Plumbing",
                "distance_km": 2.5,
                "distance_display": "2.5 km away",
                "rating": 4.8,
                "service_type": "plumbing",
                "phone": "+237123456789",
                "min_price": 25000
            },
            ...
        ],
        "total": 5,
        "center": {
            "latitude": 3.8667,
            "longitude": 11.5167
        }
    }
    """
    try:
        # Parse coordinates
        try:
            request_lat = float(request.GET.get('latitude'))
            request_lon = float(request.GET.get('longitude'))
        except (TypeError, ValueError):
            return JsonResponse({
                'success': False,
                'error': 'Invalid latitude or longitude.',
                'error_code': 'INVALID_COORDINATES'
            }, status=400)
        
        # Validate coordinates
        if not (-90 <= request_lat <= 90) or not (-180 <= request_lon <= 180):
            return JsonResponse({
                'success': False,
                'error': 'Coordinates out of valid range.',
                'error_code': 'COORDINATES_OUT_OF_RANGE'
            }, status=400)
        
        max_distance_km = float(request.GET.get('max_distance_km', 50.0))
        service_type = request.GET.get('service_type', None)
        
        # Get providers within radius
        from .distance_utils import haversine_distance
        from accounts.models import ProviderProfile
        
        providers_data = []
        
        # Build queryset
        queryset = ProviderProfile.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False,
            user__is_active=True,
            is_verified=True
        ).select_related('user')
        
        if service_type:
            queryset = queryset.filter(service_type=service_type)
        
        # Calculate distances
        for provider in queryset:
            try:
                distance = haversine_distance(
                    request_lat, request_lon,
                    float(provider.latitude), float(provider.longitude)
                )
                
                if distance <= max_distance_km:
                    providers_data.append({
                        'distance': distance,
                        'provider': provider
                    })
            except ValueError:
                continue
        
        # Sort by distance
        providers_data.sort(key=lambda x: x['distance'])
        
        # Serialize
        results = []
        for item in providers_data:
            provider = item['provider']
            distance = item['distance']
            
            results.append({
                'provider_id': provider.id,
                'user_id': provider.user.id,
                'company_name': provider.company_name or provider.user.get_full_name(),
                'distance_km': round(distance, 1),
                'distance_display': format_distance_display(distance),
                'rating': float(provider.rating),
                'total_reviews': provider.total_reviews,
                'service_type': provider.get_service_type_display(),
                'phone': provider.phone,
                'min_price': float(provider.min_price),
                'years_experience': provider.years_experience,
                'is_verified': provider.is_verified
            })
        
        logger.info(
            f"Found {len(results)} providers within {max_distance_km}km "
            f"of ({request_lat}, {request_lon})"
        )
        
        return JsonResponse({
            'success': True,
            'providers': results,
            'total': len(results),
            'center': {
                'latitude': request_lat,
                'longitude': request_lon
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching nearby providers: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching nearby providers.',
            'error_code': 'SERVER_ERROR'
        }, status=500)

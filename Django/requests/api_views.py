"""
API views for job completion and rating system.

Provides endpoints for:
- Fetching user's accepted requests (dashboard)
- Marking jobs as completed
- Submitting ratings and feedback
- Fetching job completion history
"""

import logging
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import json

from .models import ServiceRequest
from .completion_models import JobCompletion, ServiceRating, ServiceFeedback
from accounts.models import ProviderProfile

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
@login_required
def api_user_accepted_requests(request):
    """
    Fetch user's accepted service requests for dashboard.
    
    Returns requests where:
    - User is the requester (user field)
    - Status is 'accepted'
    - Optionally filter by completion status
    
    Query parameters:
    - include_completed: true/false (default: true)
    - limit: number of results (default: 50)
    """
    user = request.user
    
    # Providers cannot access this endpoint (they have their own dashboard)
    if hasattr(user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Providers cannot access user dashboard data.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    # Parse query parameters
    include_completed = request.GET.get('include_completed', 'true').lower() == 'true'
    limit = min(int(request.GET.get('limit', 50)), 100)  # Cap at 100
    
    # Build queryset
    queryset = ServiceRequest.objects.filter(
        user=user,
        status='accepted'
    ).select_related(
        'provider',
        'provider__provider_profile',
        'price_range'
    ).prefetch_related(
        'completion',
        'completion__rating',
        'photos'
    ).order_by('-accepted_at')
    
    # Filter by completion status if requested
    if not include_completed:
        queryset = queryset.filter(completion__isnull=True)
    
    # Apply limit
    requests_list = queryset[:limit]
    
    # Serialize data
    results = []
    for service_request in requests_list:
        # Check if job is completed
        is_completed = hasattr(service_request, 'completion')
        is_rated = is_completed and hasattr(service_request.completion, 'rating')
        
        # Provider info
        provider_info = None
        if service_request.provider:
            try:
                provider_profile = service_request.provider.provider_profile
                provider_info = {
                    'id': service_request.provider.id,
                    'name': provider_profile.company_name or service_request.provider.get_full_name(),
                    'phone': provider_profile.phone,
                    'service_type': provider_profile.get_service_type_display(),
                    'rating': float(provider_profile.rating),
                    'profile_picture': provider_profile.profile_picture.url if provider_profile.profile_picture else None,
                    'location': {
                        'address': provider_profile.business_address,
                        'city': provider_profile.city,
                        'state': provider_profile.state,
                        'latitude': float(provider_profile.latitude) if provider_profile.latitude else None,
                        'longitude': float(provider_profile.longitude) if provider_profile.longitude else None,
                    }
                }
            except ProviderProfile.DoesNotExist:
                provider_info = {
                    'id': service_request.provider.id,
                    'name': service_request.provider.get_full_name(),
                    'phone': None,
                    'service_type': None,
                    'rating': 0,
                    'profile_picture': None,
                }
        
        # Completion info
        completion_info = None
        if is_completed:
            completion = service_request.completion
            completion_info = {
                'completed_at': completion.completed_at.isoformat(),
                'completion_notes': completion.completion_notes,
                'work_quality': completion.work_quality,
                'completed_on_time': completion.completed_on_time,
                'provider_showed_up': completion.provider_showed_up,
            }
        
        # Rating info
        rating_info = None
        if is_rated:
            rating = service_request.completion.rating
            rating_info = {
                'stars': rating.stars,
                'feedback': rating.feedback,
                'quality_rating': rating.quality_rating,
                'timeliness_rating': rating.timeliness_rating,
                'communication_rating': rating.communication_rating,
                'professionalism_rating': rating.professionalism_rating,
                'would_recommend': rating.would_recommend,
                'would_hire_again': rating.would_hire_again,
                'submitted_at': rating.submitted_at.isoformat(),
            }
        
        # Photos
        photos = [
            {
                'id': photo.id,
                'url': photo.image.url,
                'created_at': photo.created_at.isoformat(),
            }
            for photo in service_request.photos.all()
        ]
        
        request_data = {
            'id': service_request.id,
            'description': service_request.description,
            'provider_name': service_request.provider_name,
            'offered_price': float(service_request.offered_price) if service_request.offered_price else None,
            'date_time': service_request.date_time.isoformat() if service_request.date_time else None,
            'urgent': service_request.urgent,
            'status': service_request.status,
            'created_at': service_request.created_at.isoformat(),
            'accepted_at': service_request.accepted_at.isoformat() if service_request.accepted_at else None,
            'is_completed': is_completed,
            'is_rated': is_rated,
            'provider': provider_info,
            'completion': completion_info,
            'rating': rating_info,
            'photos': photos,
            'location': service_request.get_location_data(),
            'price_range': {
                'id': service_request.price_range.id,
                'label': service_request.price_range.label,
                'min_price': service_request.price_range.min_price,
                'max_price': service_request.price_range.max_price,
            } if service_request.price_range else None,
        }
        
        results.append(request_data)
    
    return JsonResponse({
        'success': True,
        'results': results,
        'total': len(results),
        'has_more': len(results) == limit,
    })


@require_http_methods(["POST"])
@login_required
@csrf_exempt
def api_mark_job_completed(request, request_id):
    """
    Mark a job as completed by the user.
    
    POST /api/requests/{id}/complete/
    
    Expected JSON payload:
    {
        "completion_notes": "Optional notes about completion",
        "work_quality": "excellent|good|satisfactory|needs_improvement",
        "completed_on_time": true/false,
        "provider_showed_up": true/false
    }
    
    Returns:
    - 200 OK: Job marked as completed
    - 400 Bad Request: Invalid data or job already completed
    - 403 Forbidden: Not the request owner or request not accepted
    - 404 Not Found: Request doesn't exist
    """
    try:
        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Verify user is the requester
        if service_request.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to complete this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Verify request is accepted
        if service_request.status != 'accepted':
            return JsonResponse({
                'success': False,
                'error': 'Only accepted requests can be marked as completed.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Check if already completed
        if hasattr(service_request, 'completion'):
            return JsonResponse({
                'success': False,
                'error': 'This job has already been marked as completed.',
                'error_code': 'ALREADY_COMPLETED'
            }, status=400)
        
        # Validate work quality choice if provided
        work_quality = data.get('work_quality')
        valid_qualities = ['excellent', 'good', 'satisfactory', 'needs_improvement']
        if work_quality and work_quality not in valid_qualities:
            return JsonResponse({
                'success': False,
                'error': f'Invalid work_quality. Must be one of: {", ".join(valid_qualities)}',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Create job completion record
        with transaction.atomic():
            job_completion = JobCompletion.objects.create(
                service_request=service_request,
                completed_by=request.user,
                completion_notes=data.get('completion_notes', ''),
                work_quality=work_quality,
                completed_on_time=data.get('completed_on_time', True),
                provider_showed_up=data.get('provider_showed_up', True),
                completed_at=timezone.now(),
            )
        
        logger.info(f"Job completion created for request #{request_id} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Job marked as completed successfully.',
            'completion_id': job_completion.id,
            'completed_at': job_completion.completed_at.isoformat(),
        })
    
    except Exception as e:
        logger.error(f"Error marking job complete for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@csrf_exempt
def api_submit_rating(request, request_id):
    """
    Submit rating and feedback for a completed job.
    
    POST /api/requests/{id}/rating/
    
    Expected JSON payload:
    {
        "stars": 1-5,
        "feedback": "Written feedback",
        "quality_rating": 1-5 (optional),
        "timeliness_rating": 1-5 (optional),
        "communication_rating": 1-5 (optional),
        "professionalism_rating": 1-5 (optional),
        "would_recommend": true/false,
        "would_hire_again": true/false,
        "is_public": true/false (default true)
    }
    
    Returns:
    - 200 OK: Rating submitted successfully
    - 400 Bad Request: Invalid data or job not completed
    - 403 Forbidden: Not the request owner
    - 404 Not Found: Request doesn't exist
    - 409 Conflict: Rating already submitted
    """
    try:
        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Verify user is the requester
        if service_request.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to rate this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Verify job is completed
        try:
            job_completion = service_request.completion
        except JobCompletion.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'This job must be marked as completed before rating.',
                'error_code': 'NOT_COMPLETED'
            }, status=400)
        
        # Check if already rated
        if hasattr(job_completion, 'rating'):
            return JsonResponse({
                'success': False,
                'error': 'This job has already been rated.',
                'error_code': 'ALREADY_RATED'
            }, status=409)
        
        # Validate required fields
        if 'stars' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Star rating is required.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        if 'feedback' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Written feedback is required.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Validate star rating
        stars = data['stars']
        if not isinstance(stars, int) or stars < 1 or stars > 5:
            return JsonResponse({
                'success': False,
                'error': 'Star rating must be an integer between 1 and 5.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Validate category ratings if provided
        category_ratings = ['quality_rating', 'timeliness_rating', 'communication_rating', 'professionalism_rating']
        for rating_field in category_ratings:
            if rating_field in data:
                rating_value = data[rating_field]
                if rating_value is not None and (not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5):
                    return JsonResponse({
                        'success': False,
                        'error': f'{rating_field} must be an integer between 1 and 5.',
                        'error_code': 'BAD_REQUEST'
                    }, status=400)
        
        # Validate feedback length
        feedback = data['feedback']
        if len(feedback) > 1000:
            return JsonResponse({
                'success': False,
                'error': 'Feedback must be 1000 characters or less.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Create rating record
        with transaction.atomic():
            rating = ServiceRating.objects.create(
                job_completion=job_completion,
                stars=stars,
                feedback=feedback,
                quality_rating=data.get('quality_rating'),
                timeliness_rating=data.get('timeliness_rating'),
                communication_rating=data.get('communication_rating'),
                professionalism_rating=data.get('professionalism_rating'),
                would_recommend=data.get('would_recommend', True),
                would_hire_again=data.get('would_hire_again', True),
                is_public=data.get('is_public', True),
                rated_by=request.user,
                provider=service_request.provider,
            )
            
            # Update provider's overall rating
            if service_request.provider:
                try:
                    provider_profile = service_request.provider.provider_profile
                    # Recalculate provider's average rating
                    all_ratings = ServiceRating.objects.filter(
                        provider=service_request.provider,
                        is_public=True
                    )
                    
                    if all_ratings.exists():
                        avg_rating = sum(r.stars for r in all_ratings) / all_ratings.count()
                        provider_profile.rating = round(avg_rating, 1)
                        provider_profile.total_reviews = all_ratings.count()
                        provider_profile.save()
                        
                        logger.info(f"Updated provider {service_request.provider.username} rating to {provider_profile.rating}")
                
                except ProviderProfile.DoesNotExist:
                    logger.warning(f"Provider profile not found for user {service_request.provider.username}")
        
        logger.info(f"Rating submitted for request #{request_id} by user {request.user.username}: {stars} stars")
        
        return JsonResponse({
            'success': True,
            'message': 'Rating submitted successfully.',
            'rating_id': rating.id,
            'submitted_at': rating.submitted_at.isoformat(),
        })
    
    except Exception as e:
        logger.error(f"Error submitting rating for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@csrf_exempt
def api_submit_feedback(request, request_id):
    """
    Submit additional feedback for a service request.
    
    POST /api/requests/{id}/feedback/
    
    Expected JSON payload:
    {
        "feedback_type": "general|complaint|suggestion|compliment|issue",
        "feedback_text": "Feedback content",
        "category": "quality|timing|communication|pricing|professionalism|platform|other",
        "priority": "low|medium|high|urgent"
    }
    
    Returns:
    - 200 OK: Feedback submitted successfully
    - 400 Bad Request: Invalid data
    - 403 Forbidden: Not the request owner
    - 404 Not Found: Request doesn't exist
    """
    try:
        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON payload.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Verify user is the requester
        if service_request.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to submit feedback for this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Validate required fields
        if 'feedback_text' not in data:
            return JsonResponse({
                'success': False,
                'error': 'Feedback text is required.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        feedback_text = data['feedback_text']
        if len(feedback_text) > 2000:
            return JsonResponse({
                'success': False,
                'error': 'Feedback text must be 2000 characters or less.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Validate choice fields
        feedback_type = data.get('feedback_type', 'general')
        valid_types = ['general', 'complaint', 'suggestion', 'compliment', 'issue']
        if feedback_type not in valid_types:
            return JsonResponse({
                'success': False,
                'error': f'Invalid feedback_type. Must be one of: {", ".join(valid_types)}',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        category = data.get('category', 'other')
        valid_categories = ['quality', 'timing', 'communication', 'pricing', 'professionalism', 'platform', 'other']
        if category not in valid_categories:
            return JsonResponse({
                'success': False,
                'error': f'Invalid category. Must be one of: {", ".join(valid_categories)}',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        priority = data.get('priority', 'medium')
        valid_priorities = ['low', 'medium', 'high', 'urgent']
        if priority not in valid_priorities:
            return JsonResponse({
                'success': False,
                'error': f'Invalid priority. Must be one of: {", ".join(valid_priorities)}',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Create feedback record
        feedback = ServiceFeedback.objects.create(
            service_request=service_request,
            feedback_type=feedback_type,
            feedback_text=feedback_text,
            category=category,
            priority=priority,
            submitted_by=request.user,
        )
        
        logger.info(f"Feedback submitted for request #{request_id} by user {request.user.username}: {feedback_type}")
        
        return JsonResponse({
            'success': True,
            'message': 'Feedback submitted successfully.',
            'feedback_id': feedback.id,
            'submitted_at': feedback.submitted_at.isoformat(),
        })
    
    except Exception as e:
        logger.error(f"Error submitting feedback for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def api_job_completion_history(request):
    """
    Get user's job completion history.
    
    Query parameters:
    - limit: number of results (default: 20)
    - include_ratings: true/false (default: true)
    """
    user = request.user
    
    # Parse query parameters
    limit = min(int(request.GET.get('limit', 20)), 100)  # Cap at 100
    include_ratings = request.GET.get('include_ratings', 'true').lower() == 'true'
    
    # Get completed jobs
    queryset = JobCompletion.objects.filter(
        completed_by=user
    ).select_related(
        'service_request',
        'service_request__provider',
        'service_request__provider__provider_profile'
    ).order_by('-completed_at')
    
    if include_ratings:
        queryset = queryset.prefetch_related('rating')
    
    completions = queryset[:limit]
    
    # Serialize data
    results = []
    for completion in completions:
        service_request = completion.service_request
        
        # Provider info
        provider_info = None
        if service_request.provider:
            try:
                provider_profile = service_request.provider.provider_profile
                provider_info = {
                    'id': service_request.provider.id,
                    'name': provider_profile.company_name or service_request.provider.get_full_name(),
                    'service_type': provider_profile.get_service_type_display(),
                }
            except ProviderProfile.DoesNotExist:
                provider_info = {
                    'id': service_request.provider.id,
                    'name': service_request.provider.get_full_name(),
                    'service_type': None,
                }
        
        # Rating info
        rating_info = None
        if include_ratings and hasattr(completion, 'rating'):
            rating = completion.rating
            rating_info = {
                'stars': rating.stars,
                'feedback': rating.feedback,
                'would_recommend': rating.would_recommend,
                'submitted_at': rating.submitted_at.isoformat(),
            }
        
        completion_data = {
            'id': completion.id,
            'request_id': service_request.id,
            'description': service_request.description,
            'provider_name': service_request.provider_name,
            'completed_at': completion.completed_at.isoformat(),
            'completion_notes': completion.completion_notes,
            'work_quality': completion.work_quality,
            'completed_on_time': completion.completed_on_time,
            'provider_showed_up': completion.provider_showed_up,
            'has_rating': hasattr(completion, 'rating'),
            'provider': provider_info,
            'rating': rating_info,
        }
        
        results.append(completion_data)
    
    return JsonResponse({
        'success': True,
        'results': results,
        'total': len(results),
        'has_more': len(results) == limit,
    })
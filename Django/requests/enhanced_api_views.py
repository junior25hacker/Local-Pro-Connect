"""
Enhanced API views for service request management.

Provides endpoints for:
1. Secure photo upload with validation
2. Request status updates following state machine
3. Filtered request fetching by user ID and status
4. Accept completion action (changes status to Done)
"""

import logging
import json
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db.models import Q

from .models import ServiceRequest, RequestPhoto, PriceRange
from .completion_models import JobCompletion, ServiceRating
from accounts.models import ProviderProfile
from .file_validation import validate_request_photo

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
@login_required
def api_upload_request_photo(request, request_id):
    """
    Upload a photo for a service request with secure validation.
    
    POST /api/requests/{id}/upload-photo/
    
    Expected form data:
    - photo: Image file (required)
    
    Returns:
    - 201 Created: Photo uploaded successfully
    - 400 Bad Request: Invalid file or validation failed
    - 403 Forbidden: Not the request owner
    - 404 Not Found: Request doesn't exist
    """
    try:
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Verify user is the requester
        if service_request.user != request.user:
            return JsonResponse({
                'success': False,
                'error': 'You do not have permission to upload photos for this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Check if photo is provided
        if 'photo' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No photo file provided.',
                'error_code': 'MISSING_FILE'
            }, status=400)
        
        photo_file = request.FILES['photo']
        
        # Validate photo
        try:
            validate_request_photo(photo_file)
        except ValidationError as e:
            return JsonResponse({
                'success': False,
                'error': str(e),
                'error_code': 'VALIDATION_FAILED'
            }, status=400)
        
        # Create RequestPhoto instance
        with transaction.atomic():
            request_photo = RequestPhoto.objects.create(
                service_request=service_request,
                image=photo_file,
                original_filename=photo_file.name
            )
        
        logger.info(f"Photo uploaded for request #{request_id} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Photo uploaded successfully.',
            'photo': {
                'id': request_photo.id,
                'url': request_photo.image.url,
                'file_size': request_photo.file_size,
                'original_filename': request_photo.original_filename,
                'created_at': request_photo.created_at.isoformat(),
            }
        }, status=201)
        
    except Exception as e:
        logger.error(f"Error uploading photo for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while uploading the photo.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def api_update_request_status(request, request_id):
    """
    Update request status following the state machine.
    
    POST /api/requests/{id}/update-status/
    
    Expected JSON payload:
    {
        "status": "pending|accepted|declined|completed|done",
        "reason": "optional decline reason",
        "message": "optional message"
    }
    
    State transitions:
    - pending -> accepted/declined
    - accepted -> completed (by provider)
    - completed -> done (by user after rating)
    
    Returns:
    - 200 OK: Status updated successfully
    - 400 Bad Request: Invalid status transition or data
    - 403 Forbidden: Not authorized to update status
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
        
        new_status = data.get('status')
        if not new_status:
            return JsonResponse({
                'success': False,
                'error': 'Status is required.',
                'error_code': 'MISSING_STATUS'
            }, status=400)
        
        # Validate status choice
        valid_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                'error_code': 'INVALID_STATUS'
            }, status=400)
        
        current_status = service_request.status
        
        # Define allowed transitions and permissions
        transitions = {
            'pending': {
                'accepted': 'provider',  # Provider can accept
                'declined': 'provider',  # Provider can decline
            },
            'accepted': {
                'completed': 'provider',  # Provider marks as completed
            },
            'completed': {
                'done': 'user',  # User marks as done after rating
            }
        }
        
        # Check if transition is allowed
        if current_status not in transitions or new_status not in transitions[current_status]:
            return JsonResponse({
                'success': False,
                'error': f'Invalid status transition from "{current_status}" to "{new_status}".',
                'error_code': 'INVALID_TRANSITION'
            }, status=400)
        
        # Check user permissions for this transition
        required_role = transitions[current_status][new_status]
        
        if required_role == 'provider':
            # Must be the assigned provider
            if service_request.provider != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Only the assigned provider can perform this action.',
                    'error_code': 'FORBIDDEN'
                }, status=403)
        elif required_role == 'user':
            # Must be the original requester
            if service_request.user != request.user:
                return JsonResponse({
                    'success': False,
                    'error': 'Only the request owner can perform this action.',
                    'error_code': 'FORBIDDEN'
                }, status=403)
        
        # Update status with appropriate timestamp
        with transaction.atomic():
            service_request.status = new_status
            
            if new_status == 'accepted':
                service_request.accepted_at = timezone.now()
                service_request.provider = request.user
            elif new_status == 'declined':
                service_request.declined_at = timezone.now()
                service_request.decline_reason = data.get('reason', 'other')
                service_request.decline_message = data.get('message', '')
            
            service_request.save()
        
        logger.info(f"Request #{request_id} status updated from {current_status} to {new_status} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': f'Request status updated to {new_status}.',
            'status': new_status,
            'updated_at': timezone.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error updating status for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while updating the request status.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def api_filtered_requests(request):
    """
    Fetch service requests filtered by user ID and status.
    
    GET /api/requests/filtered/
    
    Query parameters:
    - user_id: Filter by user ID (optional, admin only for other users)
    - status: Filter by status (optional)
    - role: 'requester' or 'provider' - user's role in the requests
    - limit: Number of results (default: 50, max: 100)
    - offset: Offset for pagination (default: 0)
    
    Returns:
    - 200 OK: Filtered requests
    - 400 Bad Request: Invalid parameters
    - 403 Forbidden: Not authorized to view other user's requests
    """
    try:
        # Parse query parameters
        user_id = request.GET.get('user_id')
        status_filter = request.GET.get('status')
        role = request.GET.get('role', 'requester')  # 'requester' or 'provider'
        limit = min(int(request.GET.get('limit', 50)), 100)  # Cap at 100
        offset = int(request.GET.get('offset', 0))
        
        # Determine target user
        if user_id:
            if int(user_id) != request.user.id and not request.user.is_staff:
                return JsonResponse({
                    'success': False,
                    'error': 'You do not have permission to view other users\' requests.',
                    'error_code': 'FORBIDDEN'
                }, status=403)
            target_user = get_object_or_404(User, id=user_id)
        else:
            target_user = request.user
        
        # Build queryset based on role
        if role == 'requester':
            queryset = ServiceRequest.objects.filter(user=target_user)
        elif role == 'provider':
            queryset = ServiceRequest.objects.filter(provider=target_user)
        else:
            return JsonResponse({
                'success': False,
                'error': 'Role must be "requester" or "provider".',
                'error_code': 'INVALID_ROLE'
            }, status=400)
        
        # Apply status filter if provided
        if status_filter:
            valid_statuses = [choice[0] for choice in ServiceRequest.STATUS_CHOICES]
            if status_filter not in valid_statuses:
                return JsonResponse({
                    'success': False,
                    'error': f'Invalid status. Must be one of: {", ".join(valid_statuses)}',
                    'error_code': 'INVALID_STATUS'
                }, status=400)
            queryset = queryset.filter(status=status_filter)
        
        # Get total count before pagination
        total_count = queryset.count()
        
        # Apply ordering and pagination
        queryset = queryset.select_related(
            'user',
            'provider',
            'provider__provider_profile',
            'price_range'
        ).prefetch_related(
            'photos',
            'completion',
            'completion__rating'
        ).order_by('-created_at')[offset:offset+limit]
        
        # Serialize results
        results = []
        for service_request in queryset:
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
                    }
                except ProviderProfile.DoesNotExist:
                    provider_info = {
                        'id': service_request.provider.id,
                        'name': service_request.provider.get_full_name(),
                    }
            
            # User info
            user_info = {
                'id': service_request.user.id,
                'name': service_request.user.get_full_name() or service_request.user.username,
            }
            
            # Completion and rating info
            is_completed = hasattr(service_request, 'completion')
            is_rated = is_completed and hasattr(service_request.completion, 'rating')
            
            # Photos
            photos = [
                {
                    'id': photo.id,
                    'url': photo.image.url,
                    'file_size': photo.file_size,
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
                'declined_at': service_request.declined_at.isoformat() if service_request.declined_at else None,
                'decline_reason': service_request.decline_reason,
                'decline_message': service_request.decline_message,
                'is_completed': is_completed,
                'is_rated': is_rated,
                'user': user_info,
                'provider': provider_info,
                'photos': photos,
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
            'total': total_count,
            'count': len(results),
            'offset': offset,
            'limit': limit,
            'has_more': offset + len(results) < total_count,
        })
        
    except Exception as e:
        logger.error(f"Error fetching filtered requests: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while fetching requests.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def api_accept_completion(request, request_id):
    """
    Accept job completion - changes status to 'done' and optionally saves rating.
    
    POST /api/requests/{id}/accept-completion/
    
    Expected JSON payload:
    {
        "rating": {
            "stars": 1-5,
            "feedback": "Written feedback",
            "quality_rating": 1-5 (optional),
            "timeliness_rating": 1-5 (optional),
            "communication_rating": 1-5 (optional),
            "professionalism_rating": 1-5 (optional),
            "would_recommend": true/false,
            "would_hire_again": true/false
        }
    }
    
    Returns:
    - 200 OK: Completion accepted and status changed to done
    - 400 Bad Request: Invalid data or request not in completed status
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
                'error': 'You do not have permission to accept completion for this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Verify request is in completed status
        if service_request.status != 'completed':
            return JsonResponse({
                'success': False,
                'error': 'Only completed requests can be accepted. Current status: ' + service_request.status,
                'error_code': 'INVALID_STATUS'
            }, status=400)
        
        # Verify job completion exists
        if not hasattr(service_request, 'completion'):
            return JsonResponse({
                'success': False,
                'error': 'No completion record found for this request.',
                'error_code': 'NO_COMPLETION'
            }, status=400)
        
        job_completion = service_request.completion
        
        # Check if rating already exists
        if hasattr(job_completion, 'rating'):
            return JsonResponse({
                'success': False,
                'error': 'Rating has already been submitted for this request.',
                'error_code': 'ALREADY_RATED'
            }, status=400)
        
        rating_data = data.get('rating', {})
        
        # Validate required rating fields
        if not rating_data.get('stars'):
            return JsonResponse({
                'success': False,
                'error': 'Star rating is required.',
                'error_code': 'MISSING_RATING'
            }, status=400)
        
        stars = rating_data.get('stars')
        if not isinstance(stars, int) or stars < 1 or stars > 5:
            return JsonResponse({
                'success': False,
                'error': 'Star rating must be an integer between 1 and 5.',
                'error_code': 'INVALID_RATING'
            }, status=400)
        
        feedback = rating_data.get('feedback', '')
        if not feedback.strip():
            return JsonResponse({
                'success': False,
                'error': 'Feedback is required.',
                'error_code': 'MISSING_FEEDBACK'
            }, status=400)
        
        # Validate optional category ratings
        category_ratings = ['quality_rating', 'timeliness_rating', 'communication_rating', 'professionalism_rating']
        for rating_field in category_ratings:
            rating_value = rating_data.get(rating_field)
            if rating_value is not None:
                if not isinstance(rating_value, int) or rating_value < 1 or rating_value > 5:
                    return JsonResponse({
                        'success': False,
                        'error': f'{rating_field} must be an integer between 1 and 5.',
                        'error_code': 'INVALID_CATEGORY_RATING'
                    }, status=400)
        
        # Create rating and update status
        with transaction.atomic():
            # Create the rating
            service_rating = ServiceRating.objects.create(
                job_completion=job_completion,
                stars=stars,
                feedback=feedback.strip(),
                quality_rating=rating_data.get('quality_rating'),
                timeliness_rating=rating_data.get('timeliness_rating'),
                communication_rating=rating_data.get('communication_rating'),
                professionalism_rating=rating_data.get('professionalism_rating'),
                would_recommend=rating_data.get('would_recommend', True),
                would_hire_again=rating_data.get('would_hire_again', True),
                rated_by=request.user,
                provider=service_request.provider,
            )
            
            # Update request status to 'done'
            service_request.status = 'done'
            service_request.save()
            
            # Update provider's overall rating
            if service_request.provider:
                try:
                    provider_profile = service_request.provider.provider_profile
                    # Calculate new average rating
                    all_ratings = ServiceRating.objects.filter(
                        provider=service_request.provider,
                        is_public=True
                    )
                    if all_ratings.exists():
                        avg_rating = sum(r.stars for r in all_ratings) / len(all_ratings)
                        provider_profile.rating = round(avg_rating, 1)
                        provider_profile.total_reviews = len(all_ratings)
                        provider_profile.save()
                except ProviderProfile.DoesNotExist:
                    pass
        
        logger.info(f"Completion accepted and rating submitted for request #{request_id} by user {request.user.username}")
        
        return JsonResponse({
            'success': True,
            'message': 'Job completion accepted and rating submitted successfully.',
            'status': 'done',
            'rating': {
                'id': service_rating.id,
                'stars': service_rating.stars,
                'feedback': service_rating.feedback,
                'submitted_at': service_rating.submitted_at.isoformat(),
            },
            'updated_at': timezone.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error accepting completion for request #{request_id}: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'An error occurred while accepting completion.',
            'error_code': 'SERVER_ERROR'
        }, status=500)
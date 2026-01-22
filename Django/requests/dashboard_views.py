"""
Dashboard views for user and provider request management.

This module provides:
- User dashboard for tracking service requests
- API endpoints for dashboard data
- Request lifecycle management
"""

import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Prefetch
from django.utils import timezone

from .models import ServiceRequest
from .completion_models import JobCompletion, ServiceRating
from accounts.models import ProviderProfile

logger = logging.getLogger(__name__)


@login_required
def user_dashboard(request):
    """
    User Dashboard - Display user's service requests organized by status.
    
    RBAC Rules:
    - Only authenticated regular users (non-providers) can access
    - Providers are redirected to their provider dashboard
    
    Shows:
    - Pending requests (awaiting provider response)
    - In-progress requests (accepted by provider)
    - Completed requests (ready for rating)
    - History (all past requests with ratings)
    """
    # Check if user is a provider - redirect to provider dashboard
    if hasattr(request.user, 'provider_profile'):
        logger.info(f'Provider {request.user.username} redirected from user dashboard to provider dashboard')
        return redirect('accounts:provider_dashboard')
    
    # Get all user's requests
    all_requests = ServiceRequest.objects.filter(
        user=request.user
    ).select_related(
        'provider',
        'provider__provider_profile',
        'price_range'
    ).prefetch_related(
        'photos',
        'completion',
        'completion__rating'
    ).order_by('-created_at')
    
    # Categorize requests by status
    pending_requests = all_requests.filter(status='pending')
    in_progress_requests = all_requests.filter(status='accepted')
    
    # Get completed requests (have JobCompletion but no rating yet)
    completed_job_ids = JobCompletion.objects.filter(
        service_request__user=request.user
    ).values_list('service_request_id', flat=True)
    
    completed_requests = all_requests.filter(
        id__in=completed_job_ids
    ).exclude(
        id__in=ServiceRating.objects.filter(
            job_completion__service_request__user=request.user
        ).values_list('job_completion__service_request_id', flat=True)
    )
    
    # Get rated requests (history)
    rated_request_ids = ServiceRating.objects.filter(
        rated_by=request.user
    ).values_list('job_completion__service_request_id', flat=True)
    
    history_requests = all_requests.filter(id__in=rated_request_ids)
    
    # Calculate statistics
    total_requests = all_requests.count()
    total_completed = len(completed_job_ids)
    
    logger.info(f'User dashboard accessed by {request.user.username}: {total_requests} total requests')
    
    context = {
        'all_requests': all_requests,
        'pending_requests': pending_requests,
        'in_progress_requests': in_progress_requests,
        'completed_requests': completed_requests,
        'history_requests': history_requests,
        'pending_count': pending_requests.count(),
        'in_progress_count': in_progress_requests.count(),
        'completed_count': completed_requests.count(),
        'history_count': history_requests.count(),
        'total_requests': total_requests,
        'total_completed': total_completed,
    }
    
    return render(request, 'requests/user_dashboard.html', context)


@require_http_methods(["GET"])
@login_required
def api_user_dashboard_data(request):
    """
    API endpoint to fetch user dashboard data as JSON.
    
    Returns:
    - Categorized requests (pending, in-progress, completed, history)
    - Statistics
    - Provider information for each request
    
    Query parameters:
    - status: Filter by specific status (optional)
    - limit: Number of results per category (default: 50)
    """
    # Check if user is a provider
    if hasattr(request.user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Providers cannot access user dashboard data.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    # Parse query parameters
    status_filter = request.GET.get('status', None)
    limit = min(int(request.GET.get('limit', 50)), 100)  # Cap at 100
    
    # Get all user's requests
    all_requests = ServiceRequest.objects.filter(
        user=request.user
    ).select_related(
        'provider',
        'provider__provider_profile',
        'price_range'
    ).prefetch_related(
        'photos',
        'completion',
        'completion__rating'
    ).order_by('-created_at')
    
    # Helper function to serialize request
    def serialize_request(service_request):
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
                }
            except ProviderProfile.DoesNotExist:
                provider_info = {
                    'id': service_request.provider.id,
                    'name': service_request.provider.get_full_name(),
                }
        
        # Completion info
        completion_info = None
        if hasattr(service_request, 'completion'):
            completion = service_request.completion
            completion_info = {
                'completed_at': completion.completed_at.isoformat(),
                'work_quality': completion.work_quality,
            }
        
        # Rating info
        rating_info = None
        if hasattr(service_request, 'completion') and hasattr(service_request.completion, 'rating'):
            rating = service_request.completion.rating
            rating_info = {
                'stars': rating.stars,
                'feedback': rating.feedback,
                'submitted_at': rating.submitted_at.isoformat(),
            }
        
        return {
            'id': service_request.id,
            'description': service_request.description,
            'provider_name': service_request.provider_name,
            'offered_price': float(service_request.offered_price) if service_request.offered_price else None,
            'urgent': service_request.urgent,
            'status': service_request.status,
            'created_at': service_request.created_at.isoformat(),
            'accepted_at': service_request.accepted_at.isoformat() if service_request.accepted_at else None,
            'provider': provider_info,
            'completion': completion_info,
            'rating': rating_info,
            'has_completion': hasattr(service_request, 'completion'),
            'has_rating': hasattr(service_request, 'completion') and hasattr(service_request.completion, 'rating'),
        }
    
    # Categorize and serialize
    response_data = {
        'success': True,
        'pending': [],
        'in_progress': [],
        'completed': [],
        'history': [],
        'statistics': {}
    }
    
    # Get completed job IDs
    completed_job_ids = JobCompletion.objects.filter(
        service_request__user=request.user
    ).values_list('service_request_id', flat=True)
    
    # Get rated request IDs
    rated_request_ids = ServiceRating.objects.filter(
        rated_by=request.user
    ).values_list('job_completion__service_request_id', flat=True)
    
    # Categorize requests
    for req in all_requests[:limit]:
        serialized = serialize_request(req)
        
        if req.id in rated_request_ids:
            response_data['history'].append(serialized)
        elif req.id in completed_job_ids:
            response_data['completed'].append(serialized)
        elif req.status == 'accepted':
            response_data['in_progress'].append(serialized)
        elif req.status == 'pending':
            response_data['pending'].append(serialized)
    
    # Add statistics
    response_data['statistics'] = {
        'total_requests': all_requests.count(),
        'pending_count': len(response_data['pending']),
        'in_progress_count': len(response_data['in_progress']),
        'completed_count': len(response_data['completed']),
        'history_count': len(response_data['history']),
        'total_completed': len(completed_job_ids),
    }
    
    return JsonResponse(response_data)


@require_http_methods(["GET"])
@login_required
def api_user_pending_requests(request):
    """
    Get all pending requests for the user.
    
    Returns requests where status is 'pending' (awaiting provider response).
    """
    if hasattr(request.user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Providers cannot access user dashboard data.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    pending_requests = ServiceRequest.objects.filter(
        user=request.user,
        status='pending'
    ).select_related('provider', 'provider__provider_profile').order_by('-created_at')
    
    results = []
    for req in pending_requests:
        results.append({
            'id': req.id,
            'description': req.description,
            'provider_name': req.provider_name,
            'created_at': req.created_at.isoformat(),
            'urgent': req.urgent,
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results),
    })


@require_http_methods(["GET"])
@login_required
def api_user_in_progress_requests(request):
    """
    Get all in-progress requests for the user.
    
    Returns requests where status is 'accepted' (provider is working on it).
    """
    if hasattr(request.user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Providers cannot access user dashboard data.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    in_progress_requests = ServiceRequest.objects.filter(
        user=request.user,
        status='accepted'
    ).select_related('provider', 'provider__provider_profile').order_by('-accepted_at')
    
    results = []
    for req in in_progress_requests:
        provider_info = None
        if req.provider:
            try:
                provider_profile = req.provider.provider_profile
                provider_info = {
                    'id': req.provider.id,
                    'name': provider_profile.company_name or req.provider.get_full_name(),
                    'phone': provider_profile.phone,
                }
            except ProviderProfile.DoesNotExist:
                provider_info = {
                    'id': req.provider.id,
                    'name': req.provider.get_full_name(),
                }
        
        results.append({
            'id': req.id,
            'description': req.description,
            'provider_name': req.provider_name,
            'accepted_at': req.accepted_at.isoformat() if req.accepted_at else None,
            'urgent': req.urgent,
            'provider': provider_info,
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results),
    })


@require_http_methods(["GET"])
@login_required
def api_user_completed_requests(request):
    """
    Get all completed requests awaiting rating.
    
    Returns requests that have been marked as complete but not yet rated.
    """
    if hasattr(request.user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Providers cannot access user dashboard data.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    # Get completed job IDs
    completed_job_ids = JobCompletion.objects.filter(
        service_request__user=request.user
    ).values_list('service_request_id', flat=True)
    
    # Get rated request IDs
    rated_request_ids = ServiceRating.objects.filter(
        rated_by=request.user
    ).values_list('job_completion__service_request_id', flat=True)
    
    # Get completed but not rated requests
    completed_requests = ServiceRequest.objects.filter(
        id__in=completed_job_ids
    ).exclude(
        id__in=rated_request_ids
    ).select_related('provider', 'provider__provider_profile', 'completion').order_by('-completion__completed_at')
    
    results = []
    for req in completed_requests:
        provider_info = None
        if req.provider:
            try:
                provider_profile = req.provider.provider_profile
                provider_info = {
                    'id': req.provider.id,
                    'name': provider_profile.company_name or req.provider.get_full_name(),
                }
            except ProviderProfile.DoesNotExist:
                provider_info = {
                    'id': req.provider.id,
                    'name': req.provider.get_full_name(),
                }
        
        results.append({
            'id': req.id,
            'description': req.description,
            'provider_name': req.provider_name,
            'completed_at': req.completion.completed_at.isoformat() if hasattr(req, 'completion') else None,
            'provider': provider_info,
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results),
    })


@require_http_methods(["GET"])
@login_required
def api_provider_completed_jobs(request):
    """
    Get all completed jobs for the provider.
    
    Returns jobs that have been marked as complete by users.
    """
    # Check if user is a provider
    if not hasattr(request.user, 'provider_profile'):
        return JsonResponse({
            'success': False,
            'error': 'Only providers can access this endpoint.',
            'error_code': 'FORBIDDEN'
        }, status=403)
    
    # Get completed job IDs for this provider
    completed_jobs = JobCompletion.objects.filter(
        service_request__provider=request.user
    ).select_related('service_request', 'service_request__user').order_by('-completed_at')
    
    results = []
    for completion in completed_jobs:
        req = completion.service_request
        results.append({
            'id': req.id,
            'description': req.description,
            'client_name': req.user.get_full_name() or req.user.username,
            'completed_at': completion.completed_at.isoformat(),
            'work_quality': completion.work_quality,
            'has_rating': hasattr(completion, 'rating'),
        })
    
    return JsonResponse({
        'success': True,
        'results': results,
        'count': len(results),
    })

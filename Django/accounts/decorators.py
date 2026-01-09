"""
RBAC Decorators for authentication and authorization.
Provides decorators for login requirements, provider-only access, and permission checks.
"""

from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required as django_login_required
from django.urls import reverse


def login_required(view_func):
    """
    Enhanced login_required decorator that also works with AJAX requests.
    For AJAX: returns 401 JSON response
    For regular: redirects to login page
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'error': 'Authentication required', 'redirect': reverse('login_page')},
                    status=401
                )
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login_page')
        return view_func(request, *args, **kwargs)
    return wrapper


def provider_required(view_func):
    """
    Decorator to ensure only users with a provider profile can access the view.
    Returns 403 Forbidden for non-providers.
    Works with both regular and AJAX requests.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # First check if user is authenticated
        if not request.user.is_authenticated:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'error': 'Authentication required', 'redirect': reverse('login_page')},
                    status=401
                )
            messages.error(request, 'You must be logged in to access this page.')
            return redirect('login_page')
        
        # Check if user has a provider profile
        if not hasattr(request.user, 'provider_profile'):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse(
                    {'error': 'Provider access required', 'message': 'Only service providers can access this page.'},
                    status=403
                )
            messages.error(request, 'Only service providers can access this page.')
            return HttpResponseForbidden('Provider access required')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def owner_required(model_field='provider_profile'):
    """
    Decorator to ensure users can only edit/delete their own resources.
    
    Args:
        model_field: The field name in the model that references the user/provider
                    (default: 'provider_profile')
    
    Usage:
        @owner_required(model_field='provider_profile')
        def edit_profile(request, provider_id):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            from accounts.models import ProviderProfile
            
            # Check authentication
            if not request.user.is_authenticated:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'error': 'Authentication required'},
                        status=401
                    )
                messages.error(request, 'You must be logged in.')
                return redirect('login_page')
            
            # Get provider_id from kwargs
            provider_id = kwargs.get('provider_id') or request.POST.get('provider_id')
            if not provider_id:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'error': 'Provider ID required'},
                        status=400
                    )
                return HttpResponseForbidden('Provider ID required')
            
            try:
                provider = ProviderProfile.objects.get(id=provider_id)
            except ProviderProfile.DoesNotExist:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'error': 'Provider not found'},
                        status=404
                    )
                return HttpResponseForbidden('Provider not found')
            
            # Check if current user owns this provider profile
            if provider.user != request.user:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse(
                        {'error': 'You do not have permission to modify this provider profile'},
                        status=403
                    )
                messages.error(request, 'You do not have permission to modify this provider profile.')
                return HttpResponseForbidden('Permission denied')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def read_only_profile(view_func):
    """
    Decorator to enforce read-only access for provider profiles.
    Used when a non-provider views another provider's profile.
    Adds 'read_only' flag to request for template context.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from accounts.models import ProviderProfile
        
        provider_id = kwargs.get('provider_id')
        if provider_id:
            try:
                provider = ProviderProfile.objects.get(id=provider_id)
                # If current user is not the provider owner, mark as read-only
                if not request.user.is_authenticated or provider.user != request.user:
                    request.read_only_profile = True
                else:
                    request.read_only_profile = False
            except ProviderProfile.DoesNotExist:
                request.read_only_profile = True
        
        return view_func(request, *args, **kwargs)
    return wrapper

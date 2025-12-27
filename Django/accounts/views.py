
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages, auth
from .forms import UserRegistrationForm, ProviderRegistrationForm, UserLoginForm, ProviderLoginForm
from .models import ProviderProfile, UserProfile
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
import json
import logging

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'pages/index.html')

def login_page(request):
    """Serve login page through Django"""
    return render(request, 'login.html')

def signup_user_page(request):
    """Serve user signup page through Django"""
    return render(request, 'register-user.html')

def signup_provider_page(request):
    """Serve provider signup page through Django"""
    return render(request, 'register-provider.html')

@csrf_exempt
@require_http_methods(['GET', 'POST'])
def auth_view(request):
    """
    Professional authentication view handling both signup and signin.
    Supports both users and providers.
    """
    if request.method == 'POST':
        action = request.POST.get('action', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if action == 'signup':
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Account already exists. Please sign in.'}, status=400)
            else:
                username = email.split('@')[0]
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                return JsonResponse({'success': 'Account has been created successfully. Please sign in.'})

        elif action == 'signin':
            # Professional authentication flow
            return handle_user_login(request, username, email, password)

    return render(request, 'auth_choice.html')


def handle_user_login(request, username, email, password):
    """
    Handle user login with comprehensive validation and security checks.
    Returns JSON response with success/error messages and redirect URLs.
    Supports regular users, providers, and superusers/admins.
    """
    # Validate input
    if not username:
        return JsonResponse({'error': 'Username is required.'}, status=400)
    if not password:
        return JsonResponse({'error': 'Password is required.'}, status=400)

    try:
        # Check if user exists
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        logger.warning(f'Login attempt with non-existent username: {username}')
        return JsonResponse({
            'error': 'No account found for this username. Please check your username or sign up.'
        }, status=404)

    # Validate email if provided
    if email and user.email and user.email != email:
        logger.warning(f'Login attempt with mismatched email for user: {username}')
        return JsonResponse({
            'error': 'Email does not match the username provided.'
        }, status=400)

    # Authenticate user with username and password
    authenticated_user = auth.authenticate(username=username, password=password)
    
    if authenticated_user is None:
        logger.warning(f'Login attempt with incorrect password for user: {username}')
        return JsonResponse({
            'error': 'Incorrect password for this username.'
        }, status=401)

    # Password is correct, login the user
    auth.login(request, authenticated_user)
    logger.info(f'User successfully logged in: {username}')

    # Check if user is a superuser/admin first (highest priority)
    if authenticated_user.is_superuser and authenticated_user.is_staff:
        redirect_url = '/admin/'
        user_type = 'superuser'
        success_msg = 'Welcome Administrator! You have successfully logged in. Redirecting to admin panel...'
        logger.info(f'Superuser/Admin logged in: {username}')
    # Then check if user is a provider
    elif ProviderProfile.objects.filter(user=authenticated_user).exists():
        redirect_url = '/accounts/profile/provider/'
        user_type = 'provider'
        success_msg = 'You have successfully logged in! Redirecting to your provider profile...'
    # Otherwise, treat as regular user
    else:
        redirect_url = '/accounts/profile/user/'
        user_type = 'user'
        success_msg = 'You have successfully logged in! Redirecting to your profile...'

    return JsonResponse({
        'success': success_msg,
        'user_type': user_type,
        'redirect': redirect_url,
        'username': authenticated_user.username,
        'first_name': authenticated_user.first_name
    }, status=200)


@require_http_methods(['GET', 'POST'])
def register_user(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data.get('email') or '',
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name') or '',
                last_name=form.cleaned_data.get('last_name') or '',
            )
            UserProfile.objects.create(user=user)
            auth.login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.username}!')
            return redirect('user_profile')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register_user.html', {'form': form})


@require_http_methods(['GET', 'POST'])
def register_provider(request):
    if request.method == 'POST':
        form = ProviderRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data.get('email') or '',
                password=form.cleaned_data['password1'],
                first_name=form.cleaned_data.get('first_name') or '',
                last_name=form.cleaned_data.get('last_name') or '',
            )
            ProviderProfile.objects.create(
                user=user,
                company_name=form.cleaned_data.get('company_name') or '',
                service_type=form.cleaned_data.get('service_type') or 'other',
                phone=form.cleaned_data.get('phone') or '',
                business_address=form.cleaned_data.get('business_address') or '',
                city=form.cleaned_data.get('city') or '',
                state=form.cleaned_data.get('state') or '',
                zip_code=form.cleaned_data.get('zip_code') or '',
                bio=form.cleaned_data.get('bio') or '',
                years_experience=form.cleaned_data.get('years_experience') or 0,
            )
            auth.login(request, user)
            messages.success(request, f'Welcome {user.first_name or user.username}!')
            return redirect('provider_profile')
    else:
        form = ProviderRegistrationForm()
    return render(request, 'accounts/register_provider.html', {'form': form})


def user_profile(request):
    """Serve user profile HTML page"""
    if not request.user.is_authenticated:
        return redirect('register_user')
    user_profile = UserProfile.objects.get(user=request.user) if UserProfile.objects.filter(user=request.user).exists() else None
    return render(request, 'accounts/user_profile.html', {'user_profile': user_profile})


def provider_profile(request):
    """Serve provider profile HTML page"""
    if not request.user.is_authenticated:
        return redirect('register_provider')
    provider_profile = ProviderProfile.objects.get(user=request.user) if ProviderProfile.objects.filter(user=request.user).exists() else None
    return render(request, 'accounts/provider_profile.html', {'provider_profile': provider_profile})


@login_required(login_url='auth')
def logout_view(request):
    """
    Handle user logout securely.
    Clears session and redirects to login page.
    """
    username = request.user.username
    auth.logout(request)
    logger.info(f'User logged out: {username}')
    messages.success(request, 'You have been successfully logged out.')
    return redirect('auth')


@require_http_methods(['POST'])
def api_logout(request):
    """
    API endpoint for logout (AJAX).
    Returns JSON response for client-side handling.
    """
    if request.user.is_authenticated:
        username = request.user.username
        auth.logout(request)
        logger.info(f'User logged out via API: {username}')
        return JsonResponse({
            'success': 'You have been successfully logged out.',
            'redirect': '/pages/login.html'
        }, status=200)
    return JsonResponse({'error': 'Not authenticated.'}, status=401)


# API Endpoints for fetching profile data

@require_http_methods(['GET', 'POST'])
def api_user_profile(request):
    """API endpoint to get/update user profile data as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    # Handle POST requests to update profile
    if request.method == 'POST':
        try:
            # Update user fields
            if 'first_name' in request.POST:
                request.user.first_name = request.POST.get('first_name', '')
            if 'last_name' in request.POST:
                request.user.last_name = request.POST.get('last_name', '')
            if 'email' in request.POST:
                request.user.email = request.POST.get('email', '')
            
            request.user.save()
            
            # Update user profile fields
            if 'phone' in request.POST:
                user_profile.phone = request.POST.get('phone', '')
            if 'address' in request.POST:
                user_profile.address = request.POST.get('address', '')
            if 'city' in request.POST:
                user_profile.city = request.POST.get('city', '')
            if 'state' in request.POST:
                user_profile.state = request.POST.get('state', '')
            if 'zip_code' in request.POST:
                user_profile.zip_code = request.POST.get('zip_code', '')
            
            user_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'redirect': request.path
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # Handle GET requests to retrieve profile
    data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'phone': user_profile.phone,
        'address': user_profile.address,
        'city': user_profile.city,
        'state': user_profile.state,
        'zip_code': user_profile.zip_code,
        'created_at': request.user.date_joined.isoformat(),
        'updated_at': user_profile.updated_at.isoformat(),
        'date_joined': request.user.date_joined.isoformat(),
    }
    return JsonResponse(data)


@require_http_methods(['GET', 'POST'])
def api_provider_profile(request):
    """API endpoint to get/update provider profile data as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        provider_profile = ProviderProfile.objects.get(user=request.user)
    except ProviderProfile.DoesNotExist:
        return JsonResponse({'error': 'Provider profile not found'}, status=404)
    
    # Handle POST requests to update profile
    if request.method == 'POST':
        try:
            # Handle photo upload
            if 'profile_picture' in request.FILES:
                profile_picture = request.FILES['profile_picture']
                provider_profile.profile_picture = profile_picture
            
            # Update provider profile fields
            if 'company_name' in request.POST:
                provider_profile.company_name = request.POST.get('company_name', '')
            if 'service_type' in request.POST:
                provider_profile.service_type = request.POST.get('service_type', 'other')
            if 'phone' in request.POST:
                provider_profile.phone = request.POST.get('phone', '')
            if 'business_address' in request.POST:
                provider_profile.business_address = request.POST.get('business_address', '')
            if 'city' in request.POST:
                provider_profile.city = request.POST.get('city', '')
            if 'state' in request.POST:
                provider_profile.state = request.POST.get('state', '')
            if 'zip_code' in request.POST:
                provider_profile.zip_code = request.POST.get('zip_code', '')
            if 'bio' in request.POST:
                provider_profile.bio = request.POST.get('bio', '')
            if 'service_description' in request.POST:
                provider_profile.service_description = request.POST.get('service_description', '')
            if 'years_experience' in request.POST:
                try:
                    provider_profile.years_experience = int(request.POST.get('years_experience', 0))
                except ValueError:
                    pass
            
            provider_profile.save()
            
            return JsonResponse({
                'success': True,
                'message': 'Profile updated successfully',
                'redirect': request.path
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    # Handle GET requests to retrieve profile
    # Get service type display name
    service_type_display = dict(provider_profile.SERVICE_CHOICES).get(
        provider_profile.service_type, 
        'Other'
    )
    
    data = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
        'company_name': provider_profile.company_name,
        'service_type': provider_profile.service_type,
        'service_type_display': service_type_display,
        'phone': provider_profile.phone,
        'business_address': provider_profile.business_address,
        'city': provider_profile.city,
        'state': provider_profile.state,
        'zip_code': provider_profile.zip_code,
        'bio': provider_profile.bio,
        'services_rendered': provider_profile.services_rendered,
        'years_experience': provider_profile.years_experience,
        'rating': float(provider_profile.rating),
        'total_reviews': provider_profile.total_reviews,
        'is_verified': provider_profile.is_verified,
        'created_at': provider_profile.created_at.isoformat(),
        'updated_at': provider_profile.updated_at.isoformat(),
        'date_joined': request.user.date_joined.isoformat(),
    }
    return JsonResponse(data)


@require_http_methods(['POST'])
def api_service_request(request):
    """API endpoint to handle service requests"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        # Get form data
        description = request.POST.get('description', '')
        preferred_date = request.POST.get('preferred_date', '')
        preferred_time = request.POST.get('preferred_time', '')
        contact_phone = request.POST.get('contact_phone', '')
        
        # Validate required fields
        if not description or not preferred_date or not contact_phone:
            return JsonResponse({
                'success': False,
                'error': 'Please fill in all required fields'
            }, status=400)
        
        # TODO: Save service request to database when model is created
        # For now, we'll just return success
        
        return JsonResponse({
            'success': True,
            'message': 'Service request sent successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages, auth
from .forms import UserRegistrationForm, ProviderRegistrationForm, UserLoginForm, ProviderLoginForm
from .models import ProviderProfile, UserProfile
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from urllib.parse import urlencode
from django.core.mail import send_mail
from django.conf import settings
import json
import logging
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'pages/index.html')

def login_page(request):
    """Serve login page through Django"""
    return render(request, 'login.html')

def signup_user_page(request):
    """Redirect to the Django form-based user registration page"""
    return redirect('register_user')

def signup_provider_page(request):
    """Redirect to the Django form-based provider registration page"""
    return redirect('register_provider')

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

    # Check for 'next' parameter for redirect after login
    next_url = request.POST.get('next') or request.GET.get('next')
    
    # If there's a next URL, use it
    if next_url:
        redirect_url = next_url
        user_type = 'redirect'
        success_msg = 'You have successfully logged in! Redirecting...'
    # Check if user is a superuser/admin first (highest priority)
    elif authenticated_user.is_superuser and authenticated_user.is_staff:
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


def provider_profile_detail(request, provider_id):
    """
    Display detailed profile of a specific provider.
    Accessible to all authenticated users to view provider information.
    """
    if not request.user.is_authenticated:
        return redirect('login_page')
    
    # Get the provider profile by ID
    provider_profile = get_object_or_404(
        ProviderProfile.objects.select_related('user'),
        id=provider_id
    )
    
    context = {
        'provider_profile': provider_profile,
        'user': provider_profile.user,
        'is_own_profile': request.user == provider_profile.user,
    }
    
    return render(request, 'accounts/provider_profile_detail.html', context)


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


@csrf_exempt
@require_http_methods(['POST'])
def api_contact(request):
    name = request.POST.get('name', '').strip()
    email = request.POST.get('email', '').strip()
    subject = request.POST.get('subject', '').strip()
    message = request.POST.get('message', '').strip()

    if not name or not email or not subject or not message:
        return JsonResponse({'success': False, 'error': 'All fields are required.'}, status=400)

    try:
        full_subject = f"Contact form: {subject}"
        full_message = f"From: {name} <{email}>\n\n{message}"
        send_mail(
            full_subject,
            full_message,
            getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com'),
            [getattr(settings, 'CONTACT_RECEIVER_EMAIL', 'admin@example.com')],
            fail_silently=False,
        )
        # Return simple HTML so normal form posts render nicely
        return JsonResponse({'success': True, 'message': 'Message sent successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@require_http_methods(['GET'])
def api_check_auth(request):
    """API endpoint to check if user is authenticated"""
    if request.user.is_authenticated:
        return JsonResponse({
            'authenticated': True,
            'username': request.user.username,
            'email': request.user.email,
            'user_id': request.user.id
        })
    else:
        return JsonResponse({
            'authenticated': False
        })


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


def search_page(request):
    """
    Search page for finding professionals.
    """
    # Get all providers for search results
    providers = ProviderProfile.objects.all()
    
    # Filter by service type if provided
    service_type = request.GET.get('service')
    if service_type:
        providers = providers.filter(service_type=service_type)
    
    # Filter by location if provided
    city = request.GET.get('city')
    if city:
        providers = providers.filter(city__icontains=city)
    
    context = {
        'providers': providers,
        'service_type': service_type,
        'city': city,
    }
    return render(request, 'pages/search.html', context)


def api_search_providers(request):
    """
    API endpoint to search providers.
    """
    # Get all providers
    providers = ProviderProfile.objects.select_related('user').all()
    
    # Filter by service type if provided
    service_type = request.GET.get('service')
    if service_type:
        providers = providers.filter(service_type=service_type)
    
    # Filter by location if provided
    city = request.GET.get('city')
    if city:
        providers = providers.filter(city__icontains=city)
    
    # Prepare response data
    results = []
    for provider in providers:
        results.append({
            'id': provider.id,
            'company_name': provider.company_name,
            'service_type': provider.service_type,
            'service_type_display': dict(provider.SERVICE_CHOICES).get(provider.service_type, 'Other'),
            'city': provider.city,
            'state': provider.state,
            'rating': float(provider.rating),
            'total_reviews': provider.total_reviews,
            'years_experience': provider.years_experience,
            'bio': provider.bio,
            'phone': provider.phone,
            'is_verified': provider.is_verified,
        })
    
    return JsonResponse({'providers': results})


def professionals_list(request):
    """
    Display list of professionals filtered by service type.
    Supports filtering and sorting via query parameters.
    """
    service = request.GET.get('service', 'all')
    
    # Validate service parameter
    valid_services = ['all'] + [choice[0] for choice in ProviderProfile.SERVICE_CHOICES]
    if service not in valid_services:
        service = 'all'
    
    # Base queryset - active providers only
    professionals = ProviderProfile.objects.filter(
        user__is_active=True
    ).select_related('user')
    
    # Filter by service type
    if service and service != 'all':
        professionals = professionals.filter(service_type=service)
    
    # Get service name for display
    if service == 'all':
        service_name = 'All Services'
    else:
        service_name = dict(ProviderProfile.SERVICE_CHOICES).get(service, service.title())
    
    context = {
        'service_name': service_name,
        'service_type': service,
        'professionals_count': professionals.count(),
    }
    
    return render(request, 'accounts/professionals_list.html', context)

@require_http_methods(['GET'])
def api_professionals_list(request):
    """
    API endpoint to fetch professionals data with filtering, sorting, and pagination.
    Returns JSON data for AJAX requests.
    
    Query Parameters:
    - service (required): Service type to filter ('plumbing', 'electrical', 'all', etc.)
    - min_price (optional): Minimum price filter
    - max_price (optional): Maximum price filter
    - min_rating (optional): Minimum rating (e.g., 4.0, 4.5)
    - verified (optional): Filter verified only ('true'/'false')
    - availability (optional): Availability filter (e.g., 'weekdays', 'weekends', '24/7')
    - location (optional): Location search text
    - sort (optional): Sort by ('rating', 'reviews', 'price', 'experience')
    - page (optional): Page number (default: 1)
    - limit (optional): Items per page (default: 12)
    """
    from django.db.models import Q
    
    # Get required parameter
    service = request.GET.get('service', '')
    if not service:
        return JsonResponse({
            'success': False,
            'error': 'service parameter is required'
        }, status=400)
    
    # Validate service parameter
    valid_services = ['all'] + [choice[0] for choice in ProviderProfile.SERVICE_CHOICES]
    if service not in valid_services:
        return JsonResponse({
            'success': False,
            'error': f'Invalid service type: {service}. Valid options are: {", ".join(valid_services)}'
        }, status=404)
    
    # Get optional parameters
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    min_rating = request.GET.get('min_rating', '')
    verified = request.GET.get('verified', 'false').lower() == 'true'
    availability = request.GET.get('availability', '')
    location = request.GET.get('location', '')
    sort_by = request.GET.get('sort', 'rating')
    
    # Pagination parameters
    try:
        page = max(1, int(request.GET.get('page', 1)))
        limit = max(1, min(100, int(request.GET.get('limit', 12))))  # Cap at 100
    except (ValueError, TypeError):
        page = 1
        limit = 12
    
    # Base queryset - active providers only, optimized with select_related
    professionals = ProviderProfile.objects.filter(
        user__is_active=True
    ).select_related('user').defer('service_description')  # Defer unused field for performance
    
    # Apply service filter
    if service != 'all':
        professionals = professionals.filter(service_type=service)
    
    # Apply filters
    if verified:
        professionals = professionals.filter(is_verified=True)
    
    # Rating filter
    if min_rating:
        try:
            min_rating_float = float(min_rating)
            professionals = professionals.filter(rating__gte=min_rating_float)
        except (ValueError, TypeError):
            pass  # Ignore invalid rating values
    
    # Location filtering (text search)
    if location:
        professionals = professionals.filter(
            Q(city__icontains=location) |
            Q(state__icontains=location) |
            Q(business_address__icontains=location)
        )
    
    # Availability filtering
    if availability:
        # Note: This is a placeholder - implement based on your availability field
        # For now, we'll just filter if the field exists in the model
        pass
    
    # Get total count before pagination
    total_count = professionals.count()
    
    # Apply sorting
    sort_mapping = {
        'rating': '-rating',
        'reviews': '-total_reviews',
        'price': 'years_experience',  # Placeholder - adjust based on your price field
        'experience': '-years_experience'
    }
    sort_field = sort_mapping.get(sort_by, '-rating')
    professionals = professionals.order_by(sort_field, '-created_at')
    
    # Apply pagination
    offset = (page - 1) * limit
    professionals_page = professionals[offset:offset + limit]
    
    # Build response data
    professionals_data = []
    for p in professionals_page:
        professional_data = {
            'id': p.id,
            'name': p.company_name or p.user.get_full_name() or p.user.username,
            'avatar': p.profile_picture.url if p.profile_picture else None,
            'service': p.get_service_type_display(),
            'rating': float(p.rating) if p.rating else 0.0,
            'reviews': p.total_reviews if p.total_reviews else 0,
            'verified': p.is_verified,
            'experience': p.years_experience if p.years_experience else 0,
            'price_range': '$$',  # Default - can be extended with actual price field
            'location': f"{p.city}, {p.state}" if p.city and p.state else 'Location not available',
            'bio': p.bio or '',
        }
        professionals_data.append(professional_data)
    
    # Calculate pagination info
    total_pages = (total_count + limit - 1) // limit  # Ceiling division
    
    return JsonResponse({
        'success': True,
        'service': service,
        'professionals': professionals_data,
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total_count,
            'pages': total_pages
        }
    })

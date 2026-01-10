
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages, auth
from .forms import UserRegistrationForm, ProviderRegistrationForm, UserLoginForm, ProviderLoginForm
from .models import ProviderProfile, UserProfile
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from .decorators import provider_required, owner_required, read_only_profile
from urllib.parse import urlencode
from django.core.mail import send_mail
from django.conf import settings
import json
import logging
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from requests.models import ServiceRequest

logger = logging.getLogger(__name__)

def home(request):
    return render(request, 'pages/index.html')

def login_page(request):
    """Serve login page through Django"""
    return render(request, 'login.html')

def signup_user_page(request):
    """Redirect to the Django form-based user registration page"""
    return redirect('accounts:register_user')

def signup_provider_page(request):
    """Redirect to the Django form-based provider registration page"""
    return redirect('accounts:register_provider')

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
            return redirect('accounts:user_profile')
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
            return redirect('accounts:provider_profile')
    else:
        form = ProviderRegistrationForm()
    return render(request, 'accounts/register_provider.html', {'form': form})


def user_profile(request):
    """Serve user profile HTML page"""
    if not request.user.is_authenticated:
        return redirect('accounts:register_user')
    user_profile = UserProfile.objects.get(user=request.user) if UserProfile.objects.filter(user=request.user).exists() else None
    return render(request, 'accounts/user_profile.html', {'user_profile': user_profile})


def provider_profile(request):
    """Serve provider profile HTML page"""
    if not request.user.is_authenticated:
        return redirect('accounts:register_provider')
    provider_profile = ProviderProfile.objects.get(user=request.user) if ProviderProfile.objects.filter(user=request.user).exists() else None
    return render(request, 'accounts/provider_profile.html', {'provider_profile': provider_profile})


@login_required
def emergency_request(request):
    """
    Handle emergency service requests with location sharing and provider selection
    """
    if request.method == 'POST':
        # Handle emergency request submission
        emergency_type = request.POST.get('emergency_type', '')
        description = request.POST.get('description', '')
        location_lat = request.POST.get('location_lat', '')
        location_lng = request.POST.get('location_lng', '')
        address = request.POST.get('address', '')
        selected_provider_id = request.POST.get('selected_provider', '')
        contact_phone = request.POST.get('contact_phone', '')

        # Validate required fields
        if not all([emergency_type, description, contact_phone, selected_provider_id]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Please fill in all required fields.'})
            messages.error(request, 'Please fill in all required fields.')
            return redirect('emergency_request')

        try:
            # Get the selected provider
            selected_provider = User.objects.get(id=selected_provider_id)
            provider_profile = ProviderProfile.objects.get(user=selected_provider)

            # Create emergency service request
            emergency_request = ServiceRequest.objects.create(
                user=request.user,
                provider=selected_provider,
                provider_name=provider_profile.company_name or selected_provider.get_full_name(),
                description=f"EMERGENCY {emergency_type.upper()}: {description}\n\nLocation: {address}\nCoordinates: {location_lat}, {location_lng}\nContact Phone: {contact_phone}",
                urgent=True,
                status='pending'
            )

            # Update user profile with phone if not set
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            if not user_profile.phone:
                user_profile.phone = contact_phone
                user_profile.save()

            # Send email notification to provider
            try:
                send_mail(
                    subject=f'EMERGENCY SERVICE REQUEST - {emergency_type.upper()}',
                    message=f"""EMERGENCY SERVICE REQUEST

Type: {emergency_type.upper()}
Description: {description}

Customer: {request.user.get_full_name()} ({request.user.email})
Phone: {contact_phone}
Location: {address}
Coordinates: {location_lat}, {location_lng}

This is an EMERGENCY request. Please respond immediately!

View request: {request.build_absolute_uri(f'/requests/detail/{emergency_request.id}/')}""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[selected_provider.email],
                    fail_silently=True
                )
            except Exception as e:
                logger.error(f"Failed to send emergency email: {e}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Emergency request sent successfully! Help is on the way.',
                    'request_id': emergency_request.id
                })

            messages.success(request, 'Emergency request sent successfully! Help is on the way.')
            return redirect('user_profile')

        except User.DoesNotExist:
            error_msg = 'Selected provider not found.'
        except ProviderProfile.DoesNotExist:
            error_msg = 'Provider profile not found.'
        except Exception as e:
            logger.error(f"Error creating emergency request: {e}")
            error_msg = 'An error occurred while processing your request.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})

        messages.error(request, error_msg)
        return redirect('emergency_request')

    # Get nearby providers for the emergency request
    # In a real implementation, you'd filter by location and service type
    nearby_providers = ProviderProfile.objects.all()[:10]  # Get first 10 providers

    context = {
        'nearby_providers': nearby_providers,
        'user_profile': UserProfile.objects.get(user=request.user) if UserProfile.objects.filter(user=request.user).exists() else None
    }

    return render(request, 'accounts/emergency_request.html', context)
@read_only_profile
def provider_profile_detail(request, provider_id):
    """
    Display detailed profile of a specific provider.
    
    RBAC Rules:
    - Regular Users: Read-only access to any provider profile
      * View provider details (service, location, price, reviews)
      * Cannot modify any provider information
      * Cannot delete provider profile
    
    - Provider Owner: Full access to their own profile
      * Can edit their own provider profile fields
      * Cannot edit other providers' profiles
      * read_only_profile flag is False for owner
    """
    if not request.user.is_authenticated:
        return redirect('accounts:login_page')
    
    # Get the provider profile by ID
    provider_profile = get_object_or_404(
        ProviderProfile.objects.select_related('user'),
        id=provider_id
    )
    
    # Determine if this is the provider's own profile
    is_own_profile = (request.user.is_authenticated and request.user == provider_profile.user)
    
    # Check if user has edit permissions (only provider owner)
    can_edit = is_own_profile and request.user.is_authenticated
    
    context = {
        'provider_profile': provider_profile,
        'user': provider_profile.user,
        'is_own_profile': is_own_profile,
        'can_edit': can_edit,  # Used in template to show/hide edit buttons
        'read_only': getattr(request, 'read_only_profile', True),  # Flag for template
    }
    
    return render(request, 'accounts/provider_profile_detail.html', context)


@login_required
@provider_required
def provider_dashboard(request):
    """
    Provider Dashboard - Access only for users with provider role.
    
    RBAC Rules:
    - Only authenticated users with a ProviderProfile can access
    - Returns 403 Forbidden for non-providers
    - Displays provider's service requests and statistics
    """
    try:
        provider_profile = request.user.provider_profile
    except ProviderProfile.DoesNotExist:
        messages.error(request, 'Provider profile not found.')
        return redirect('accounts:home')
    
    # Get provider's service requests from requests app
    from requests.models import ServiceRequest
    
    # Get all requests for this provider (filter by user, not provider_profile)
    all_requests = ServiceRequest.objects.filter(
        provider=request.user
    ).select_related('user').order_by('-created_at')
    
    # Categorize requests by status
    pending_requests = all_requests.filter(status='pending')
    accepted_requests = all_requests.filter(status='accepted')
    declined_requests = all_requests.filter(status='declined')
    
    context = {
        'provider_profile': provider_profile,
        'all_requests': all_requests,
        'pending_requests': pending_requests,
        'accepted_requests': accepted_requests,
        'declined_requests': declined_requests,
        'pending_count': pending_requests.count(),
        'accepted_count': accepted_requests.count(),
        'declined_count': declined_requests.count(),
    }
    
    return render(request, 'requests/provider_dashboard.html', context)


@login_required
@provider_required
def edit_provider_profile(request, provider_id=None):
    """
    Edit Provider Profile - Owner access only.
    
    RBAC Rules:
    - Only the provider owner can edit their profile
    - Returns 403 Forbidden for non-owners
    - Handles both GET (display form) and POST (save changes)
    """
    # Get the provider profile to edit
    if provider_id:
        provider_profile = get_object_or_404(ProviderProfile, id=provider_id)
    else:
        # Use current user's provider profile if not specified
        try:
            provider_profile = request.user.provider_profile
        except ProviderProfile.DoesNotExist:
            messages.error(request, 'Provider profile not found.')
            return redirect('accounts:home')
    
    # Check ownership - only provider owner can edit
    if provider_profile.user != request.user:
        messages.error(request, 'You do not have permission to edit this provider profile.')
        return HttpResponseForbidden('Permission denied')
    
    if request.method == 'POST':
        from .forms import ProviderProfileForm
        from .email_utils import send_profile_update_email
        
        form = ProviderProfileForm(request.POST, request.FILES, instance=provider_profile)
        if form.is_valid():
            form.save()
            
            # Send profile update notification email
            email_sent = send_profile_update_email(provider_profile)
            if email_sent:
                messages.success(request, 'Provider profile updated successfully. Notification email sent.')
            else:
                messages.success(request, 'Provider profile updated successfully. (Email notification failed)')
            
            return redirect('accounts:provider_profile_detail', provider_id=provider_profile.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field}: {error}')
    else:
        from .forms import ProviderProfileForm
        form = ProviderProfileForm(instance=provider_profile)
    
    context = {
        'form': form,
        'provider_profile': provider_profile,
        'is_editing': True,
    }
    
    return render(request, 'accounts/provider_profile_edit.html', context)


@require_http_methods(['GET'])
def logout_view(request):
    """
    Handle user logout securely.
    Clears session and redirects to login page.
    """
    username = request.user.username
    auth.logout(request)
    logger.info(f'User logged out: {username}')
    messages.success(request, 'You have been successfully logged out.')
    # UXA: after logout, redirect to static homepage
    return redirect('http://127.0.0.1:5500/index.html')


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
    
    # Ensure user profile exists (auto-create if missing)
    user_profile, _created = UserProfile.objects.get_or_create(user=request.user)
    
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

            # Handle optional user profile photo upload
            if 'profile_picture' in request.FILES:
                uploaded = request.FILES['profile_picture']
                content_type = getattr(uploaded, 'content_type', '') or ''
                if not content_type.startswith('image/'):
                    return JsonResponse({'success': False, 'error': 'Only image uploads are allowed.'}, status=400)
                if uploaded.size and uploaded.size > 5 * 1024 * 1024:
                    return JsonResponse({'success': False, 'error': 'Image too large (max 5MB).'}, status=400)
                user_profile.profile_picture = uploaded

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
        'profile_picture': (user_profile.profile_picture.url if user_profile.profile_picture else ''),
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
    - city (optional): Filter by city
    - state (optional): Filter by state
    - region (optional): Filter by region (Cameroon regions)
    - location (optional): General location search
    - min_rating (optional): Minimum rating (e.g., 3.5, 4.0, 4.5)
    - min_experience (optional): Minimum years of experience
    - min_price (optional): Minimum price
    - max_price (optional): Maximum price
    - price_range (optional): Preset price range ('budget', 'moderate', 'premium', 'luxury')
    - verified (optional): Filter verified only ('true'/'false')
    - min_reviews (optional): Minimum number of reviews
    - sort (optional): Sort by ('rating', 'reviews', 'price', 'experience', 'newest', 'name')
    - page (optional): Page number (default: 1)
    - limit (optional): Items per page (default: 20, max: 100)
    
    Returns:
    JSON with professionals list, pagination info, and region alternatives if applicable
    """
    from .filter_utils import ProfessionalFilter, serialize_professional, get_region_alternatives
    
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
        }, status=400)
    
    # Get optional parameters
    city = request.GET.get('city', '').strip()
    state = request.GET.get('state', '').strip()
    region = request.GET.get('region', '').strip()
    location = request.GET.get('location', '').strip()
    min_rating = request.GET.get('min_rating', '').strip()
    min_experience = request.GET.get('min_experience', '').strip()
    min_price = request.GET.get('min_price', '').strip()
    max_price = request.GET.get('max_price', '').strip()
    price_range = request.GET.get('price_range', '').strip()
    verified = request.GET.get('verified', 'false').lower() == 'true'
    min_reviews = request.GET.get('min_reviews', '').strip()
    sort_by = request.GET.get('sort', 'rating').strip()
    
    # Pagination parameters
    try:
        page = max(1, int(request.GET.get('page', 1)))
        limit = max(1, min(100, int(request.GET.get('limit', 20))))  # Cap at 100, default 20
    except (ValueError, TypeError):
        page = 1
        limit = 20
    
    try:
        # Initialize filter
        pfilter = ProfessionalFilter()
        
        # Apply filters in order
        pfilter.apply_service_filter(service)
        pfilter.apply_rating_filter(min_rating)
        pfilter.apply_experience_filter(min_experience)
        pfilter.apply_price_filter(price_range=price_range, min_price=min_price, max_price=max_price)
        pfilter.apply_verified_filter(verified)
        pfilter.apply_review_count_filter(min_reviews)
        
        # Apply location filter (returns region_message if region not found)
        pfilter, region_message = pfilter.apply_location_filter(
            location=location,
            city=city,
            state=state,
            region=region
        )
        
        # Apply sorting
        pfilter.sort_by(sort_by)
        
        # Apply pagination
        pagination_info = pfilter.paginate(page=page, limit=limit)
        
        # Get all professionals for region alternatives (from unfiltered queryset)
        base_filter = ProfessionalFilter()
        base_filter.apply_service_filter(service)
        available_regions = get_region_alternatives(base_filter.get_queryset())
        
        # Serialize professionals data
        professionals_data = [
            serialize_professional(p) for p in pagination_info['items']
        ]
        
        # Prepare response
        response_data = {
            'success': True,
            'service': service,
            'professionals': professionals_data,
            'pagination': {
                'page': pagination_info['page'],
                'limit': pagination_info['limit'],
                'total': pagination_info['total'],
                'pages': pagination_info['pages'],
                'has_next': pagination_info['has_next'],
                'has_prev': pagination_info['has_prev'],
            },
            'filters_applied': pfilter.get_filters_applied(),
        }
        
        # Add region-specific information if applicable
        if region_message:
            response_data['region_message'] = region_message
            response_data['available_regions'] = available_regions
        
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f'Error in api_professionals_list: {str(e)}', exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Error processing filter: {str(e)}'
        }, status=500)

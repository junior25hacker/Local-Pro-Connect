
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages, auth
from .forms import UserRegistrationForm, ProviderRegistrationForm
from .models import ProviderProfile, UserProfile
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import urlencode
import json

def home(request):
    return render(request, 'pages/index.html')

@require_http_methods(['GET', 'POST'])
def auth_view(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if action == 'signup':
            if User.objects.filter(email=email).exists():
                return JsonResponse({'error': 'Account already exists. Please sign in.'}, status=400)
            else:
                username = email.split('@')[0]
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()
                return JsonResponse({'success': 'Account has been created successfully. Please sign in.'})

        elif action == 'signin':
            # Try to find user by username only
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return JsonResponse({'error': 'No account found for this username. Please check your username or sign up.'}, status=404)

            # Check if email matches (if provided)
            if email and user.email and user.email != email:
                return JsonResponse({'error': 'Email does not match the username provided.'}, status=400)

            # Authenticate with username and password
            user_auth = auth.authenticate(username=username, password=password)
            if user_auth is not None:
                auth.login(request, user_auth)
                # Check if user is a provider
                is_provider = ProviderProfile.objects.filter(user=user_auth).exists()
                if is_provider:
                    return JsonResponse({
                        'success': 'Login successful! Redirecting to provider profile...',
                        'user_type': 'provider',
                        'redirect': '/pages/provider-profile.html'
                    })
                else:
                    return JsonResponse({
                        'success': 'Login successful! Redirecting to user profile...',
                        'user_type': 'user',
                        'redirect': '/pages/user-profile.html'
                    })
            else:
                return JsonResponse({'error': 'Incorrect password for this username.'}, status=401)

    return render(request, 'auth_choice.html')


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
    return render(request, 'user-profile.html')


def provider_profile(request):
    """Serve provider profile HTML page"""
    if not request.user.is_authenticated:
        return redirect('register_provider')
    return render(request, 'provider-profile.html')


# API Endpoints for fetching profile data

@require_http_methods(['GET'])
def api_user_profile(request):
    """API endpoint to get user profile data as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
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


@require_http_methods(['GET'])
def api_provider_profile(request):
    """API endpoint to get provider profile data as JSON"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        provider_profile = ProviderProfile.objects.get(user=request.user)
    except ProviderProfile.DoesNotExist:
        return JsonResponse({'error': 'Provider profile not found'}, status=404)
    
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


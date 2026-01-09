from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db.models import Q
from decimal import Decimal
import math
import logging

logger = logging.getLogger(__name__)

from .forms import ServiceRequestForm, RejectionForm, AcceptanceForm, RequestEditForm
from .models import ServiceRequest, RequestPhoto, PriceRange, RequestDecisionToken
from accounts.models import ProviderProfile, UserProfile
from accounts.decorators import provider_required
from .utils import calculate_distance, get_address_string
from .export_utils import (
    get_filtered_requests,
    generate_csv_export,
    generate_pdf_export_html,
    get_export_filename,
    format_request_for_export
)


# Geocodio Autocomplete proxy endpoint
import requests as ext_requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

GEOCODIO_API_KEY = '054587d60047e4d609f91e55ed7876849766576'

@require_GET
@csrf_exempt
def locations_autocomplete(request):
    """
    Proxies Geocodio Autocomplete API for city/address suggestions.
    Query param: ?q=search_text
    """
    query = request.GET.get('q', '')
    if not query:
        return JsonResponse({'results': []})

    url = 'https://api.geocod.io/v1.7/autocomplete'
    params = {
        'q': query,
        'api_key': GEOCODIO_API_KEY,
        'limit': 8,
    }
    try:
        resp = ext_requests.get(url, params=params, timeout=5)
        data = resp.json()
        suggestions = data.get('results', [])
        # Return formatted suggestions
        results = [
            {
                'description': s.get('address_components', {}).get('formatted_city', s.get('formatted_address', '')),
                'full_address': s.get('formatted_address', ''),
                'lat': s.get('location', {}).get('lat'),
                'lng': s.get('location', {}).get('lng'),
            }
            for s in suggestions
        ]
        return JsonResponse({'results': results})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@require_http_methods(["GET", "POST"])
@login_required
def create_request(request):
    """
    CREATE REQUEST - Regular users only
    
    Handles creation of a service request with:
    - description
    - optional date/time
    - optional price range
    - urgent toggle
    - optional multiple photos
    
    Supports pre-selection of provider via query parameter:
    - ?provider=<provider_id> - pre-selects the provider in the form
    
    RBAC Rules:
    - Only regular users (non-providers) can create requests
    - Providers should be blocked from creating requests
    """
    # Providers must not be able to access the New Request page (strict RBAC)
    if hasattr(request.user, 'provider_profile'):
        return HttpResponseForbidden('Service providers cannot create service requests.')

    if request.method == "POST":
        form = ServiceRequestForm(request.POST, request.FILES)

        if form.is_valid():
            # Save the main ServiceRequest with current user
            service_request = form.save(commit=False)
            service_request.user = request.user
            service_request.save()

            # Handle uploaded photos (optional, multiple)
            photos = request.FILES.getlist("photos")
            for photo in photos:
                RequestPhoto.objects.create(
                    service_request=service_request,
                    image=photo,
                )

            # Log budget information for reporting
            if service_request.offered_price:
                logger.info(
                    f"Service request #{service_request.id} created with budget ${service_request.offered_price:.2f} "
                    f"for provider {service_request.provider_name} by user {request.user.username}"
                )
            
            # Log validation info
            if service_request.provider:
                logger.info(
                    f"Budget ${service_request.offered_price:.2f} validated against provider minimum "
                    f"${service_request.provider.provider_profile.min_price:.2f}"
                )

            # Token generation and email notifications are handled by post_save signals
            # Keep the request handling snappy and rely on signals for side-effects.

            # Redirect to success page
            return redirect("requests:create_request_success")

    else:
        # Check for provider pre-selection from query parameter
        provider_id = request.GET.get('provider')
        initial_data = {}
        
        if provider_id:
            try:
                provider_profile = ProviderProfile.objects.get(id=provider_id)
                initial_data['provider_choice'] = provider_profile
            except ProviderProfile.DoesNotExist:
                pass
        
        form = ServiceRequestForm(initial=initial_data)

    # Pass price ranges to template
    price_ranges = PriceRange.objects.all().order_by("min_price")

    context = {
        "form": form,
        "price_ranges": price_ranges,
    }

    return render(request, "requests/create_request.html", context)


@login_required
def create_request_success(request):
    return render(request, "requests/create_request_sucess.html")


@never_cache
def provider_decision(request, request_id, action, token):
    """
    Handle provider decision to accept or decline a service request.
    
    Args:
        request_id: The ServiceRequest ID
        action: Either 'accept' or 'decline'
        token: The secure decision token
    """
    # Get the service request
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    # Get and validate the decision token
    try:
        decision_token = RequestDecisionToken.objects.get(
            service_request=service_request,
            token=token
        )
    except RequestDecisionToken.DoesNotExist:
        return render(request, 'requests/invalid_token.html', {
            'error': 'Invalid or expired token'
        }, status=400)
    
    # Check if token is still valid
    if not decision_token.is_valid():
        return render(request, 'requests/invalid_token.html', {
            'error': 'This decision link has expired or has already been used'
        }, status=400)
    
    # Handle GET request - show confirmation page
    if request.method == "GET":
        context = {
            'service_request': service_request,
            'action': action,
            'token': token,
        }
        
        if action == 'accept':
            return render(request, 'requests/confirm_accept.html', context)
        elif action == 'decline':
            return render(request, 'requests/confirm_decline.html', context)
        else:
            return render(request, 'requests/invalid_token.html', {
                'error': 'Invalid action'
            }, status=400)
    
    # Handle POST request - process the decision
    elif request.method == "POST":
        try:
            # Get or create the provider user based on provider_name
            # For now, we'll create a generic provider user if it doesn't exist
            provider = None
            
            if action == 'accept':
                # Accept the request
                service_request.accept(provider)
                decision_token.mark_as_used()
                
                # Notify the requester via email
                try:
                    from django.core.mail import EmailMultiAlternatives
                    from django.template.loader import render_to_string
                    from django.conf import settings as dj_settings
                    subject = "Your request was accepted"
                    context = {
                        'service_request': service_request,
                        'status': 'accepted',
                        'site_url': dj_settings.SITE_URL,
                    }
                    text_body = render_to_string('emails/request_accepted_email.txt', context)
                    html_body = render_to_string('emails/request_accepted_email.html', context)
                    to_email = [service_request.user.email] if service_request.user and service_request.user.email else []
                    if to_email:
                        email = EmailMultiAlternatives(subject, text_body, None, to_email)
                        email.attach_alternative(html_body, "text/html")
                        email.send(fail_silently=True)
                except Exception as e:
                    print(f"User notify accept email error: {e}")

                return render(request, 'requests/decision_success.html', {
                    'message': 'Request accepted successfully!',
                    'service_request': service_request,
                    'action': 'accepted'
                })
            
            elif action == 'decline':
                # Get rejection data from form (can come from modal or regular form)
                rejection_reason = request.POST.get('rejection_reason', '')
                rejection_description = request.POST.get('rejection_description', '')
                
                # Map rejection_reason to decline_reason if using modal naming
                # Also support legacy decline_reason field for backward compatibility
                decline_reason = request.POST.get('decline_reason', rejection_reason)
                decline_message = request.POST.get('decline_message', rejection_description)
                
                # Validate decline reason
                valid_reasons = [r[0] for r in ServiceRequest.DECLINE_REASON_CHOICES]
                if decline_reason not in valid_reasons:
                    decline_reason = 'other'
                
                # Decline the request
                service_request.decline(decline_reason, decline_message)
                decision_token.mark_as_used()

                # Notify the requester via email
                try:
                    from django.core.mail import EmailMultiAlternatives
                    from django.template.loader import render_to_string
                    from django.conf import settings as dj_settings
                    
                    # Get display text for the reason
                    reason_display = dict(ServiceRequest.DECLINE_REASON_CHOICES).get(decline_reason, 'Other')
                    
                    subject = "Your request was declined"
                    context = {
                        'service_request': service_request,
                        'customer_name': service_request.user.get_full_name() or service_request.user.username,
                        'provider_name': service_request.provider_name,
                        'request_id': service_request.id,
                        'description': service_request.description,
                        'date_time': service_request.date_time,
                        'price_range': service_request.price_range,
                        'decline_reason': decline_reason,
                        'decline_reason_display': reason_display,
                        'decline_message': decline_message,
                        'declined_at': service_request.declined_at,
                        'dashboard_link': f"{dj_settings.SITE_URL}/dashboard/",
                        'status': 'declined',
                        'site_url': dj_settings.SITE_URL,
                    }
                    text_body = render_to_string('emails/request_declined_email.txt', context)
                    html_body = render_to_string('emails/request_declined_email.html', context)
                    to_email = [service_request.user.email] if service_request.user and service_request.user.email else []
                    if to_email:
                        email = EmailMultiAlternatives(subject, text_body, None, to_email)
                        email.attach_alternative(html_body, "text/html")
                        email.send(fail_silently=True)
                except Exception as e:
                    print(f"User notify decline email error: {e}")
                
                return render(request, 'requests/decision_success.html', {
                    'message': 'Request declined. Thank you for letting us know.',
                    'service_request': service_request,
                    'action': 'declined'
                })
            
            else:
                return render(request, 'requests/invalid_token.html', {
                    'error': 'Invalid action'
                }, status=400)
        
        except Exception as e:
            print(f"Error processing provider decision: {str(e)}")
            return render(request, 'requests/decision_error.html', {
                'error': str(e)
            }, status=500)
    
    else:
        return HttpResponseForbidden('Method not allowed')


def rejection_modal_demo(request):
    """
    Demo view to display the rejection modal as a standalone page for testing.
    """
    return render(request, 'requests/rejection_modal.html')


@login_required
@provider_required
def request_list(request):
    """
    Display a list of service requests for the logged-in user.
    Shows different views based on whether the user is a provider or regular user.
    Calculates and displays distance between user and provider.
    
    RBAC Rules:
    - Regular Users: See requests they created
    - Providers: See requests directed to them
    - Unauthenticated users: Redirected to login
    """
    user = request.user
    
    # Provider-only view (enforced by @provider_required)
    is_provider = True
    
    # Show requests directed to this provider
    requests_list = ServiceRequest.objects.filter(
        provider=user
    ).select_related('user', 'provider', 'price_range').prefetch_related('photos')
    
    # Calculate distances for each request
    requests_with_distance = []
    for service_request in requests_list:
        request_data = {
            'request': service_request,
            'distance': None,
            'user_address': None,
            'provider_address': None,
            'user_lat': None,
            'user_lng': None,
            'provider_lat': None,
            'provider_lng': None,
        }
        
        # Get user profile
        user_profile = None
        if hasattr(service_request.user, 'user_profile'):
            user_profile = service_request.user.user_profile
            request_data['user_address'] = get_address_string(user_profile)
            # Mock coordinates based on zip code for demo
            # In production, use actual geocoding API
            if user_profile.zip_code:
                try:
                    zip_int = int(user_profile.zip_code)
                    # Generate pseudo-coordinates from zip code (for demo only)
                    request_data['user_lat'] = 40.7128 + (zip_int % 1000) * 0.001
                    request_data['user_lng'] = -74.0060 + (zip_int % 2000) * 0.001
                except (ValueError, AttributeError):
                    pass
        
        # Get provider profile
        provider_profile = None
        if service_request.provider and hasattr(service_request.provider, 'provider_profile'):
            provider_profile = service_request.provider.provider_profile
            request_data['provider_address'] = get_address_string(provider_profile)
            # Mock coordinates based on zip code for demo
            if provider_profile.zip_code:
                try:
                    zip_int = int(provider_profile.zip_code)
                    # Generate pseudo-coordinates from zip code (for demo only)
                    request_data['provider_lat'] = 40.7128 + (zip_int % 1000) * 0.001
                    request_data['provider_lng'] = -74.0060 + (zip_int % 2000) * 0.001
                except (ValueError, AttributeError):
                    pass
        
        # Calculate distance if both profiles have zip codes (simplified distance calculation)
        # Note: For production, you'd want to use actual geocoding or stored lat/lon
        if user_profile and provider_profile:
            # Placeholder: In production, you'd geocode the addresses
            # For demo purposes, we'll show a mock distance based on zip code difference
            try:
                user_zip = int(user_profile.zip_code) if user_profile.zip_code else 0
                provider_zip = int(provider_profile.zip_code) if provider_profile.zip_code else 0
                # Very rough approximation: ~0.01 miles per zip code unit difference
                zip_diff = abs(user_zip - provider_zip)
                request_data['distance'] = min(zip_diff * 0.5, 500)  # Cap at 500 miles
            except (ValueError, AttributeError):
                request_data['distance'] = None
        
        requests_with_distance.append(request_data)
    
    context = {
        'requests_with_distance': requests_with_distance,
        'is_provider': is_provider,
        'total_requests': len(requests_with_distance),
    }
    
    return render(request, 'requests/request_list.html', context)


@login_required
def request_detail(request, request_id):
    """
    Display detailed view of a single service request with distance calculation.
    """
    service_request = get_object_or_404(
        ServiceRequest.objects.select_related('user', 'provider', 'price_range').prefetch_related('photos'),
        id=request_id
    )
    
    # Check if user has permission to view this request
    user = request.user
    is_provider = hasattr(user, 'provider_profile')
    
    # Users can view their own requests, providers can view requests directed to them
    if service_request.user != user and service_request.provider != user:
        return HttpResponseForbidden('You do not have permission to view this request')
    
    # Calculate distance
    distance = None
    user_address = None
    provider_address = None
    user_lat = None
    user_lng = None
    provider_lat = None
    provider_lng = None
    
    # Get user profile
    user_profile = None
    if hasattr(service_request.user, 'user_profile'):
        user_profile = service_request.user.user_profile
        user_address = get_address_string(user_profile)
        # Mock coordinates for demo
        if user_profile.zip_code:
            try:
                zip_int = int(user_profile.zip_code)
                user_lat = 40.7128 + (zip_int % 1000) * 0.001
                user_lng = -74.0060 + (zip_int % 2000) * 0.001
            except (ValueError, AttributeError):
                pass
    
    # Get provider profile
    provider_profile = None
    if service_request.provider and hasattr(service_request.provider, 'provider_profile'):
        provider_profile = service_request.provider.provider_profile
        provider_address = get_address_string(provider_profile)
        # Mock coordinates for demo
        if provider_profile.zip_code:
            try:
                zip_int = int(provider_profile.zip_code)
                provider_lat = 40.7128 + (zip_int % 1000) * 0.001
                provider_lng = -74.0060 + (zip_int % 2000) * 0.001
            except (ValueError, AttributeError):
                pass
    
    # Calculate distance
    if user_profile and provider_profile:
        try:
            user_zip = int(user_profile.zip_code) if user_profile.zip_code else 0
            provider_zip = int(provider_profile.zip_code) if provider_profile.zip_code else 0
            zip_diff = abs(user_zip - provider_zip)
            distance = min(zip_diff * 0.5, 500)  # Cap at 500 miles
        except (ValueError, AttributeError):
            distance = None
    
    context = {
        'service_request': service_request,
        'distance': distance,
        'user_address': user_address,
        'provider_address': provider_address,
        'user_lat': user_lat,
        'user_lng': user_lng,
        'provider_lat': provider_lat,
        'provider_lng': provider_lng,
        'is_provider': is_provider,
    }
    
    return render(request, 'requests/request_detail.html', context)


@login_required
@require_http_methods(["GET"])
def export_requests_csv(request):
    """
    Export service requests to CSV format.
    
    Supports query parameters for filtering:
    - status: pending, accepted, or declined
    - service_type: filter by service type name
    - urgent: true/false
    - date_from: ISO format date (e.g., 2024-01-01)
    - date_to: ISO format date (e.g., 2024-12-31)
    
    Only allows users to export their own requests (or all if staff).
    """
    user = request.user
    is_provider = hasattr(user, 'provider_profile')
    
    # Only staff can export all requests, regular users export their own
    if not user.is_staff and not is_provider:
        # Regular users can only export their own requests
        pass
    
    # Parse filter parameters from query string
    filters = {
        'status': request.GET.get('status'),
        'service_type': request.GET.get('service_type'),
        'urgent': request.GET.get('urgent'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
    }
    
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        # Get filtered requests
        requests_list = get_filtered_requests(user, filters, is_provider)
        
        if not requests_list:
            return HttpResponse(
                "No requests found matching the selected filters.",
                status=204,
                content_type="text/plain"
            )
        
        # Generate CSV
        csv_output = generate_csv_export(requests_list)
        csv_content = csv_output.getvalue()
        
        # Create HTTP response with CSV content
        response = HttpResponse(
            csv_content,
            content_type='text/csv'
        )
        
        filename = get_export_filename('csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        return HttpResponse(
            f"Error exporting requests: {str(e)}",
            status=500,
            content_type="text/plain"
        )


@login_required
@require_http_methods(["GET"])
def export_requests_pdf(request):
    """
    Export service requests to PDF format.
    
    Supports query parameters for filtering:
    - status: pending, accepted, or declined
    - service_type: filter by service type name
    - urgent: true/false
    - date_from: ISO format date (e.g., 2024-01-01)
    - date_to: ISO format date (e.g., 2024-12-31)
    
    Only allows users to export their own requests (or all if staff).
    Uses WeasyPrint for professional PDF generation with styling.
    """
    user = request.user
    is_provider = hasattr(user, 'provider_profile')
    
    # Only staff can export all requests, regular users export their own
    if not user.is_staff and not is_provider:
        # Regular users can only export their own requests
        pass
    
    # Parse filter parameters from query string
    filters = {
        'status': request.GET.get('status'),
        'service_type': request.GET.get('service_type'),
        'urgent': request.GET.get('urgent'),
        'date_from': request.GET.get('date_from'),
        'date_to': request.GET.get('date_to'),
    }
    
    # Remove None values from filters
    filters = {k: v for k, v in filters.items() if v is not None}
    
    try:
        # Get filtered requests
        requests_list = get_filtered_requests(user, filters, is_provider)
        
        if not requests_list:
            return HttpResponse(
                "No requests found matching the selected filters.",
                status=204,
                content_type="text/plain"
            )
        
        # Generate HTML for PDF
        export_timestamp = timezone.now()
        html_content = generate_pdf_export_html(requests_list, export_timestamp)
        
        # Try to use WeasyPrint for PDF generation
        try:
            from weasyprint import HTML, CSS
            import io
            
            # Create in-memory PDF
            pdf_buffer = io.BytesIO()
            HTML(string=html_content).write_pdf(pdf_buffer)
            pdf_content = pdf_buffer.getvalue()
            
        except ImportError:
            # Fallback: use ReportLab if WeasyPrint is not available
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib import colors
                from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
                from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
                from reportlab.lib.units import inch
                import io
                
                pdf_buffer = io.BytesIO()
                doc = SimpleDocTemplate(pdf_buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
                
                styles = getSampleStyleSheet()
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=18,
                    textColor=colors.HexColor('#667eea'),
                    spaceAfter=12,
                    alignment=1,
                )
                
                elements = []
                
                # Title
                title = Paragraph("Service Requests Export", title_style)
                elements.append(title)
                
                # Timestamp
                timestamp_text = export_timestamp.strftime('%B %d, %Y at %H:%M:%S')
                timestamp = Paragraph(f"Generated on {timestamp_text}", styles['Normal'])
                elements.append(timestamp)
                elements.append(Spacer(1, 0.3*inch))
                
                # Prepare table data
                table_data = [[
                    'Request ID',
                    'Service Type',
                    'User',
                    'Provider',
                    'Status',
                    'Date',
                    'Price Range',
                    'Urgent'
                ]]
                
                for service_request in requests_list:
                    formatted = format_request_for_export(service_request)
                    
                    table_data.append([
                        str(formatted['request_id']),
                        formatted['service_type'][:20],
                        formatted['user_name'][:20],
                        formatted['provider_name'][:20],
                        formatted['status'],
                        formatted['date_created'],
                        formatted['price_range'],
                        formatted['urgent'],
                    ])
                
                # Create table with styling
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                ]))
                
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                pdf_content = pdf_buffer.getvalue()
                
            except ImportError:
                return HttpResponse(
                    "PDF generation libraries not installed. Please install reportlab or weasyprint.",
                    status=500,
                    content_type="text/plain"
                )
        
        # Create HTTP response with PDF content
        response = HttpResponse(
            pdf_content,
            content_type='application/pdf'
        )
        
        filename = get_export_filename('pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
    
    except Exception as e:
        import traceback
        error_msg = f"Error exporting to PDF: {str(e)}\n{traceback.format_exc()}"
        return HttpResponse(
            error_msg,
            status=500,
            content_type="text/plain"
        )


@login_required
@require_http_methods(["GET"])
def live_provider_tracking(request, request_id):
    """
    Returns the live location of the provider for an accepted service request.
    
    Only allows the request owner (user who created the request) to access the data.
    Returns JSON with provider's current coordinates, name, and estimated time of arrival.
    
    Args:
        request_id: The ServiceRequest ID
    
    Returns:
        JSON response with provider location data:
        {
            "success": true,
            "provider_id": 123,
            "provider_name": "John Doe",
            "latitude": 12.3456,
            "longitude": 78.9012,
            "eta_minutes": 15
        }
    
    Error responses:
        - 404: Request not found
        - 403: User is not the owner of the request
        - 400: Request not accepted or provider not assigned
        - 400: Provider location not available
    """
    # Get the service request
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    # Authorization: Only the request owner can access provider location
    if service_request.user != request.user:
        return JsonResponse({
            'success': False,
            'error': 'You do not have permission to track this provider.',
            'error_code': 'UNAUTHORIZED'
        }, status=403)
    
    # Verify request is accepted
    if service_request.status != 'accepted':
        return JsonResponse({
            'success': False,
            'error': 'This request has not been accepted yet. Provider location is only available for accepted requests.',
            'error_code': 'REQUEST_NOT_ACCEPTED'
        }, status=400)
    
    # Verify provider is assigned
    if not service_request.provider:
        return JsonResponse({
            'success': False,
            'error': 'No provider assigned to this request.',
            'error_code': 'NO_PROVIDER'
        }, status=400)
    
    # Get provider profile
    try:
        provider_profile = service_request.provider.provider_profile
    except ProviderProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Provider profile not found.',
            'error_code': 'PROVIDER_PROFILE_NOT_FOUND'
        }, status=400)
    
    # Check if provider has location data
    if provider_profile.latitude is None or provider_profile.longitude is None:
        return JsonResponse({
            'success': False,
            'error': 'Provider location is not available at this time. The provider may not have enabled location sharing.',
            'error_code': 'LOCATION_NOT_AVAILABLE'
        }, status=400)
    
    # Get user location for ETA calculation
    user_profile = None
    eta_minutes = None
    
    if hasattr(service_request.user, 'user_profile'):
        user_profile = service_request.user.user_profile
        
        # Calculate ETA if we have both locations
        if user_profile.zip_code and provider_profile.zip_code:
            try:
                # Simple distance calculation based on lat/long
                # In production, you'd use a routing API (Google Maps, Mapbox, etc.)
                distance_km = calculate_haversine_distance(
                    float(provider_profile.latitude),
                    float(provider_profile.longitude),
                    # Mock user coordinates from zip for demo
                    40.7128 + (int(user_profile.zip_code) % 1000) * 0.001 if user_profile.zip_code else 40.7128,
                    -74.0060 + (int(user_profile.zip_code) % 2000) * 0.001 if user_profile.zip_code else -74.0060
                )
                
                # Estimate ETA: assume average speed of 30 km/h in city
                eta_minutes = int((distance_km / 30) * 60)
                
                # Add some buffer time for stops, traffic, etc.
                eta_minutes = max(5, eta_minutes + 5)
                
            except (ValueError, AttributeError, ZeroDivisionError):
                # If calculation fails, don't provide ETA
                eta_minutes = None
    
    # Get provider name
    provider_name = (
        provider_profile.company_name 
        or service_request.provider.get_full_name() 
        or service_request.provider.username
    )
    
    # Return success response
    return JsonResponse({
        'success': True,
        'provider_id': service_request.provider.id,
        'provider_name': provider_name,
        'latitude': float(provider_profile.latitude),
        'longitude': float(provider_profile.longitude),
        'eta_minutes': eta_minutes,
        'last_updated': provider_profile.updated_at.isoformat() if provider_profile.updated_at else None,
        'provider_phone': provider_profile.phone if provider_profile.phone else None,
    })


def calculate_haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees).
    Returns distance in kilometers.
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    
    return c * r


# ===========================
# API ENDPOINTS
# ===========================

@require_GET
def api_demo_providers(request):
    """
    API endpoint to return demo professionals for a service type.
    Query param: ?serviceType=plumbing
    """
    service_type = request.GET.get('serviceType', '').strip()
    # Only filter demo professionals (usernames start with demo_pro_)
    professionals = ProviderProfile.objects.filter(
        user__username__startswith='demo_pro_',
        service_type=service_type
    )
    results = []
    for pro in professionals:
        results.append({
            'id': pro.user.id,
            'name': pro.company_name,
            'serviceType': dict(ProviderProfile.SERVICE_CHOICES).get(pro.service_type, pro.service_type),
            'description': pro.service_description,
            'address': pro.business_address,
            'phone': pro.phone,
            'rating': float(pro.rating),
            'reviewCount': pro.total_reviews,
            'yearsExperience': pro.years_experience,
        })
    return JsonResponse(results, safe=False)


@require_GET
@login_required
def api_provider_min_price(request, provider_id):
    """
    API endpoint to fetch comprehensive provider pricing information.
    Returns JSON with pricing details and service information.
    
    Response includes:
    - min_price: Minimum price the provider accepts
    - max_price: Maximum price (for display range)
    - avg_price: Average pricing (calculated from min/max or min_price)
    - service_rate: How provider charges (hourly/fixed/custom)
    - currency: Currency format (USD)
    - company_name: Provider's company name
    """
    try:
        provider_profile = ProviderProfile.objects.get(id=provider_id)
        
        # Calculate average price
        if provider_profile.max_price:
            avg_price = float((provider_profile.min_price + provider_profile.max_price) / 2)
        else:
            avg_price = float(provider_profile.min_price)
        
        return JsonResponse({
            'success': True,
            'provider_id': provider_id,
            'min_price': float(provider_profile.min_price),
            'max_price': float(provider_profile.max_price) if provider_profile.max_price else None,
            'avg_price': avg_price,
            'service_rate': provider_profile.service_rate,
            'currency': 'USD',
            'company_name': provider_profile.company_name or provider_profile.user.get_full_name()
        })
    except ProviderProfile.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Provider not found'
        }, status=404)
    except (ValueError, TypeError) as e:
        return JsonResponse({
            'success': False,
            'error': 'Invalid provider pricing information'
        }, status=400)


# ===========================
# MODAL API ENDPOINTS
# ===========================

@require_http_methods(["POST"])
@login_required
def api_request_decline(request, request_id):
    """
    API endpoint for provider to decline a service request.
    
    Endpoint: POST /api/requests/{id}/decline/
    
    Expected JSON payload:
    {
        "reason": "price|distance|time|other",
        "message": "Optional custom message (max 500 chars)"
    }
    
    RBAC Rules:
    - Only the assigned provider can decline
    - Request must be in 'pending' or 'open' status
    - Once declined, cannot be changed back
    
    Returns:
    - 200 OK: { "status": "success", "message": "...", "request_id": X }
    - 400 Bad Request: Invalid payload or state transition
    - 403 Forbidden: User is not the assigned provider
    - 404 Not Found: Request doesn't exist
    - 409 Conflict: Request already declined
    """
    try:
        import json
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check authorization - only assigned provider can decline
        if service_request.provider != request.user:
            logger.warning(
                f"Unauthorized decline attempt for request #{request_id} by user {request.user.username}"
            )
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to decline this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Check if request is in a valid state for declining
        if service_request.status == 'declined':
            logger.warning(f"Decline attempt on already declined request #{request_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'This request has already been declined.',
                'error_code': 'CONFLICT'
            }, status=409)
        
        if service_request.status == 'accepted':
            logger.warning(f"Decline attempt on already accepted request #{request_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot decline an accepted request.',
                'error_code': 'CONFLICT'
            }, status=409)
        
        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON payload.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Validate using RejectionForm
        form = RejectionForm(data)
        if not form.is_valid():
            errors = form.errors
            logger.warning(f"Decline validation failed for request #{request_id}: {errors}")
            return JsonResponse({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': errors,
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Get validated data
        reason = form.cleaned_data['reason']
        message = form.cleaned_data.get('message', '')
        
        # Update the service request
        service_request.decline(reason=reason, message=message)
        
        logger.info(
            f"Request #{request_id} declined by provider {request.user.username} "
            f"(reason: {reason})"
        )
        
        # Signal handler will send decline email automatically
        
        return JsonResponse({
            'status': 'success',
            'message': 'Request has been declined successfully.',
            'request_id': service_request.id,
            'new_status': service_request.status,
        }, status=200)
    
    except ServiceRequest.DoesNotExist:
        logger.warning(f"Decline attempt on non-existent request #{request_id}")
        return JsonResponse({
            'status': 'error',
            'message': 'Service request not found.',
            'error_code': 'NOT_FOUND'
        }, status=404)
    
    except Exception as e:
        logger.error(
            f"Error processing decline for request #{request_id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def api_request_accept(request, request_id):
    """
    API endpoint for provider to accept a service request.
    
    Endpoint: POST /api/requests/{id}/accept/
    
    Expected JSON payload:
    {
        "notes": "Optional acceptance notes (max 500 chars)"
    }
    
    RBAC Rules:
    - Only the assigned provider can accept
    - Request must be in 'pending' or 'open' status
    - Once accepted, cannot be changed back
    
    Returns:
    - 200 OK: { "status": "success", "message": "...", "request_id": X }
    - 400 Bad Request: Invalid payload
    - 403 Forbidden: User is not the assigned provider
    - 404 Not Found: Request doesn't exist
    - 409 Conflict: Request already accepted/declined
    """
    try:
        import json
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check authorization
        if service_request.provider != request.user:
            logger.warning(
                f"Unauthorized accept attempt for request #{request_id} by user {request.user.username}"
            )
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to accept this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Check if request is in a valid state
        if service_request.status == 'accepted':
            logger.warning(f"Accept attempt on already accepted request #{request_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'This request has already been accepted.',
                'error_code': 'CONFLICT'
            }, status=409)
        
        if service_request.status == 'declined':
            logger.warning(f"Accept attempt on already declined request #{request_id}")
            return JsonResponse({
                'status': 'error',
                'message': 'Cannot accept a declined request.',
                'error_code': 'CONFLICT'
            }, status=409)
        
        # Parse JSON payload (optional)
        try:
            data = json.loads(request.body) if request.body else {}
        except json.JSONDecodeError:
            data = {}
        
        # Validate using AcceptanceForm
        form = AcceptanceForm(data)
        if not form.is_valid():
            errors = form.errors
            logger.warning(f"Accept validation failed for request #{request_id}: {errors}")
            return JsonResponse({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': errors,
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Accept the request (which sets accepted_at timestamp)
        service_request.accept(request.user)
        
        logger.info(
            f"Request #{request_id} accepted by provider {request.user.username}"
        )
        
        # Signal handler will send acceptance email automatically
        
        return JsonResponse({
            'status': 'success',
            'message': 'Request has been accepted successfully.',
            'request_id': service_request.id,
            'new_status': service_request.status,
        }, status=200)
    
    except ServiceRequest.DoesNotExist:
        logger.warning(f"Accept attempt on non-existent request #{request_id}")
        return JsonResponse({
            'status': 'error',
            'message': 'Service request not found.',
            'error_code': 'NOT_FOUND'
        }, status=404)
    
    except Exception as e:
        logger.error(
            f"Error processing accept for request #{request_id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)


@require_http_methods(["POST"])
@login_required
def api_request_edit(request, request_id):
    """
    API endpoint for user to edit their service request.
    
    Endpoint: POST /api/requests/{id}/edit/
    
    Expected JSON payload:
    {
        "description": "Updated description",
        "date_time": "2024-01-20T10:30",
        "offered_price": 150.00
    }
    
    RBAC Rules:
    - Only the request creator can edit
    - Can only edit pending requests (not accepted/declined)
    - Cannot edit after provider has responded
    
    Returns:
    - 200 OK: { "status": "success", "message": "...", "request_id": X }
    - 400 Bad Request: Invalid payload or state
    - 403 Forbidden: User is not the request creator
    - 404 Not Found: Request doesn't exist
    - 409 Conflict: Request already accepted/declined
    """
    try:
        import json
        
        # Get the service request
        service_request = get_object_or_404(ServiceRequest, id=request_id)
        
        # Check authorization - only creator can edit
        if service_request.user != request.user:
            logger.warning(
                f"Unauthorized edit attempt for request #{request_id} by user {request.user.username}"
            )
            return JsonResponse({
                'status': 'error',
                'message': 'You do not have permission to edit this request.',
                'error_code': 'FORBIDDEN'
            }, status=403)
        
        # Check if request is in editable state
        if service_request.status in ['accepted', 'declined']:
            logger.warning(
                f"Edit attempt on {service_request.status} request #{request_id}"
            )
            return JsonResponse({
                'status': 'error',
                'message': f'Cannot edit a {service_request.status} request.',
                'error_code': 'CONFLICT'
            }, status=409)
        
        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON payload.',
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Validate using RequestEditForm
        form = RequestEditForm(data, instance=service_request, service_request=service_request)
        if not form.is_valid():
            errors = form.errors
            logger.warning(f"Edit validation failed for request #{request_id}: {errors}")
            return JsonResponse({
                'status': 'error',
                'message': 'Validation failed.',
                'errors': errors,
                'error_code': 'BAD_REQUEST'
            }, status=400)
        
        # Save the updated request
        updated_request = form.save()
        
        logger.info(
            f"Request #{request_id} edited by user {request.user.username}"
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Request has been updated successfully.',
            'request_id': updated_request.id,
        }, status=200)
    
    except ServiceRequest.DoesNotExist:
        logger.warning(f"Edit attempt on non-existent request #{request_id}")
        return JsonResponse({
            'status': 'error',
            'message': 'Service request not found.',
            'error_code': 'NOT_FOUND'
        }, status=404)
    
    except Exception as e:
        logger.error(
            f"Error processing edit for request #{request_id}: {str(e)}",
            exc_info=True
        )
        return JsonResponse({
            'status': 'error',
            'message': 'An error occurred while processing your request.',
            'error_code': 'SERVER_ERROR'
        }, status=500)
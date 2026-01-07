from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.views.decorators.cache import never_cache
from django.utils import timezone
from django.db.models import Q

from .forms import ServiceRequestForm
from .models import ServiceRequest, RequestPhoto, PriceRange, RequestDecisionToken
from accounts.models import ProviderProfile, UserProfile
from .utils import calculate_distance, get_address_string
from .export_utils import (
    get_filtered_requests,
    generate_csv_export,
    generate_pdf_export_html,
    get_export_filename,
    format_request_for_export
)


@require_http_methods(["GET", "POST"])
@login_required
def create_request(request):
    """
    Handles creation of a service request with:
    - description
    - optional date/time
    - optional price range
    - urgent toggle
    - optional multiple photos
    
    Supports pre-selection of provider via query parameter:
    - ?provider=<provider_id> - pre-selects the provider in the form
    """

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
def request_list(request):
    """
    Display a list of service requests for the logged-in user.
    Shows different views based on whether the user is a provider or regular user.
    Calculates and displays distance between user and provider.
    """
    user = request.user
    
    # Determine if user is a provider
    is_provider = hasattr(user, 'provider_profile')
    
    if is_provider:
        # Show requests directed to this provider
        requests_list = ServiceRequest.objects.filter(
            provider=user
        ).select_related('user', 'provider', 'price_range').prefetch_related('photos')
    else:
        # Show requests created by this user
        requests_list = ServiceRequest.objects.filter(
            user=user
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
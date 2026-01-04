from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.cache import never_cache
from django.utils import timezone

from .forms import ServiceRequestForm
from .models import ServiceRequest, RequestPhoto, PriceRange, RequestDecisionToken
from accounts.models import ProviderProfile


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
        form = ServiceRequestForm()

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
                decline_reason = request.POST.get('decline_reason', 'no_reason')
                decline_message = request.POST.get('decline_message', '')
                
                # Validate decline reason
                valid_reasons = [r[0] for r in ServiceRequest.DECLINE_REASON_CHOICES]
                if decline_reason not in valid_reasons:
                    decline_reason = 'no_reason'
                
                # Decline the request
                service_request.decline(decline_reason, decline_message)
                decision_token.mark_as_used()

                # Notify the requester via email
                try:
                    from django.core.mail import EmailMultiAlternatives
                    from django.template.loader import render_to_string
                    from django.conf import settings as dj_settings
                    subject = "Your request was declined"
                    context = {
                        'service_request': service_request,
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
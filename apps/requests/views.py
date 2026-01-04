from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

from .forms import ServiceRequestForm
from .models import RequestPhoto, PriceRange


@require_http_methods(["GET", "POST"])
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
            # Save the main ServiceRequest
            service_request = form.save()

            # Handle uploaded photos (optional, multiple)
            photos = request.FILES.getlist("photos")
            for photo in photos:
                RequestPhoto.objects.create(
                    service_request=service_request,
                    image=photo,
                )

            # After successful submission
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


def create_request_success(request):
    return render(request, "requests/create_request_sucess.html")
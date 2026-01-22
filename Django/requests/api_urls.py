from django.urls import path

from .priority_queue_api import api_provider_pending_requests, api_providers_within_radius

urlpatterns = [
    path('provider/pending/', api_provider_pending_requests, name='api_provider_pending_requests'),
    path('providers-nearby/', api_providers_within_radius, name='api_providers_nearby'),
]

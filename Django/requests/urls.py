from django.urls import path
from .views import (
    create_request,
    create_request_success,
    provider_decision, 
    rejection_modal_demo,
    request_list,
    request_detail,
    export_requests_csv,
    export_requests_pdf,
    live_provider_tracking,
    locations_autocomplete,
    api_demo_providers,
)

app_name = "requests"

urlpatterns = [
    path("create/", create_request, name="create_request"),
    path("success/", create_request_success, name="create_request_success"),
    path("decision/<int:request_id>/<str:action>/<str:token>/", provider_decision, name="provider_decision"),
    path("rejection-modal-demo/", rejection_modal_demo, name="rejection_modal_demo"),
    path("list/", request_list, name="request_list"),
    path("export/csv/", export_requests_csv, name="export_requests_csv"),
    path("export/pdf/", export_requests_pdf, name="export_requests_pdf"),
    path("<int:request_id>/tracking/", live_provider_tracking, name="live_provider_tracking"),
    path("<int:request_id>/", request_detail, name="request_detail"),
    path("api/locations-autocomplete/", locations_autocomplete, name="locations_autocomplete"),
    path("api/demo-providers/", api_demo_providers, name="api_demo_providers"),
]
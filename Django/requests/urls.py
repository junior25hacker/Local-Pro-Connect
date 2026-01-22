from django.urls import path
from django.views.generic import RedirectView
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
    api_provider_min_price,
    api_request_decline,
    api_request_accept,
    api_request_edit,
)
from .api_views import (
    api_user_accepted_requests,
    api_mark_job_completed,
    api_submit_rating,
    api_submit_feedback,
    api_job_completion_history,
)
from .enhanced_api_views import (
    api_upload_request_photo,
    api_update_request_status,
    api_filtered_requests,
    api_accept_completion,
)
from .priority_queue_api import (
    api_provider_pending_requests,
    api_request_priority_details,
    api_providers_within_radius,
)
from .dashboard_views import (
    user_dashboard,
    api_user_dashboard_data,
    api_user_pending_requests,
    api_user_in_progress_requests,
    api_user_completed_requests,
    api_provider_completed_jobs,
)

app_name = "requests"

urlpatterns = [
    path("", request_list, name="request_index"),
    path("create/", create_request, name="create_request"),
    path("success/", create_request_success, name="create_request_success"),
    path("decision/<int:request_id>/<str:action>/<str:token>/", provider_decision, name="provider_decision"),
    path("rejection-modal-demo/", rejection_modal_demo, name="rejection_modal_demo"),
    path("list/", request_list, name="request_list"),
    path("export/csv/", export_requests_csv, name="export_requests_csv"),
    path("export/pdf/", export_requests_pdf, name="export_requests_pdf"),
    path("<int:request_id>/tracking/", live_provider_tracking, name="live_provider_tracking"),
    path("<int:request_id>/", request_detail, name="request_detail"),
    
    # Dashboard URLs
    path("dashboard/user/", user_dashboard, name="user_dashboard"),
    # Redirect from old URL pattern to maintain backward compatibility
    path("user/dashboard/", RedirectView.as_view(pattern_name="requests:user_dashboard", permanent=True), name="user_dashboard_redirect"),
    
    # API Endpoints
    path("api/locations-autocomplete/", locations_autocomplete, name="locations_autocomplete"),
    path("api/demo-providers/", api_demo_providers, name="api_demo_providers"),
    path("api/provider/<int:provider_id>/min-price/", api_provider_min_price, name="api_provider_min_price"),
    
    # Modal API Endpoints
    path("api/<int:request_id>/decline/", api_request_decline, name="api_request_decline"),
    path("api/<int:request_id>/accept/", api_request_accept, name="api_request_accept"),
    path("api/<int:request_id>/edit/", api_request_edit, name="api_request_edit"),
    
    # Job Completion and Rating API Endpoints
    path("api/user/accepted-requests/", api_user_accepted_requests, name="api_user_accepted_requests"),
    path("api/<int:request_id>/complete/", api_mark_job_completed, name="api_mark_job_completed"),
    path("api/<int:request_id>/rating/", api_submit_rating, name="api_submit_rating"),
    path("api/<int:request_id>/feedback/", api_submit_feedback, name="api_submit_feedback"),
    path("api/user/completion-history/", api_job_completion_history, name="api_job_completion_history"),
    
    # Enhanced API Endpoints
    path("api/<int:request_id>/upload-photo/", api_upload_request_photo, name="api_upload_request_photo"),
    path("api/<int:request_id>/update-status/", api_update_request_status, name="api_update_request_status"),
    path("api/filtered/", api_filtered_requests, name="api_filtered_requests"),
    path("api/<int:request_id>/accept-completion/", api_accept_completion, name="api_accept_completion"),
    
    # Priority Queue API Endpoints
    path("api/provider/pending/", api_provider_pending_requests, name="api_provider_pending_requests"),
    path("api/<int:request_id>/priority-details/", api_request_priority_details, name="api_request_priority_details"),
    path("api/providers-nearby/", api_providers_within_radius, name="api_providers_within_radius"),
    
    # Dashboard API Endpoints
    path("api/dashboard/user/data/", api_user_dashboard_data, name="api_user_dashboard_data"),
    path("api/dashboard/user/pending/", api_user_pending_requests, name="api_user_pending_requests"),
    path("api/dashboard/user/in-progress/", api_user_in_progress_requests, name="api_user_in_progress_requests"),
    path("api/dashboard/user/completed/", api_user_completed_requests, name="api_user_completed_requests"),
    path("api/dashboard/provider/completed/", api_provider_completed_jobs, name="api_provider_completed_jobs"),
]
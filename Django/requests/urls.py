from django.urls import path
from .views import (
    create_request,
    create_request_success,
    provider_decision,
    request_list,
    request_detail,
    export_requests_csv,
    export_requests_pdf,
)

app_name = "requests"

urlpatterns = [
    path("create/", create_request, name="create_request"),
    path("success/", create_request_success, name="create_request_success"),
    path("decision/<int:request_id>/<str:action>/<str:token>/", provider_decision, name="provider_decision"),
    path("list/", request_list, name="request_list"),
    path("export/csv/", export_requests_csv, name="export_requests_csv"),
    path("export/pdf/", export_requests_pdf, name="export_requests_pdf"),
    path("<int:request_id>/", request_detail, name="request_detail"),
]
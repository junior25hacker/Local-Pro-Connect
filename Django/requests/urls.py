from django.urls import path
from .views import create_request, create_request_success, provider_decision, rejection_modal_demo

app_name = "requests"

urlpatterns = [
    path("create/", create_request, name="create_request"),
    path("success/", create_request_success, name="create_request_success"),
    path("decision/<int:request_id>/<str:action>/<str:token>/", provider_decision, name="provider_decision"),
    path("rejection-modal-demo/", rejection_modal_demo, name="rejection_modal_demo"),
]
from django.urls import path
from .views import create_request,create_request_success

app_name = "requests"

urlpatterns = [
    path("create/", create_request, name="create_request"),
    path("success/", create_request_success, name="create_request_success"),
]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('auth/', views.auth_view, name='auth'),
    path('signup/user/', views.signup_user_page, name='signup_user_page'),
    path('signup/provider/', views.signup_provider_page, name='signup_provider_page'),
    path('register/user/', views.register_user, name='register_user'),
    path('register/provider/', views.register_provider, name='register_provider'),
    path('profile/user/', views.user_profile, name='user_profile'),
    path('profile/provider/', views.provider_profile, name='provider_profile'),
    path('emergency/', views.emergency_request, name='emergency_request'),
    path('logout/', views.logout_view, name='logout'),
    # API Endpoints
    path('api/user/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/provider/profile/', views.api_provider_profile, name='api_provider_profile'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/service-request/', views.api_service_request, name='api_service_request'),
    path('api/contact/', views.api_contact, name='api_contact'),
]

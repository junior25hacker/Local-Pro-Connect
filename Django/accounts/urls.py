from django.urls import path
from . import views

app_name = 'accounts'

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
<<<<<<< HEAD
    path('emergency/', views.emergency_request, name='emergency_request'),
=======
    path('profile/provider/<int:provider_id>/edit/', views.edit_provider_profile, name='edit_provider_profile'),
    path('dashboard/provider/', views.provider_dashboard, name='provider_dashboard'),
>>>>>>> 52a5e9701da7e4a57974d7d77f93dbe0f8158811
    path('logout/', views.logout_view, name='logout'),
    # Search (protected - requires login)
    path('search/', views.search_page, name='search_page'),
    # Professionals List
    path('professionals/', views.professionals_list, name='professionals_list'),
    path('professionals/<int:provider_id>/', views.provider_profile_detail, name='provider_profile_detail'),
    # API Endpoints
    path('api/check-auth/', views.api_check_auth, name='api_check_auth'),
    path('api/user/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/provider/profile/', views.api_provider_profile, name='api_provider_profile'),
    path('api/logout/', views.api_logout, name='api_logout'),
    path('api/service-request/', views.api_service_request, name='api_service_request'),
    path('api/contact/', views.api_contact, name='api_contact'),
    path('api/professionals/', views.api_professionals_list, name='api_professionals_list'),
    path('api/filter/', views.api_professionals_list, name='api_filter_professionals'),  # Alias for filtering
]

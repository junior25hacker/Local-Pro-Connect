from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('auth/', views.auth_view, name='auth'),
    path('signup/user/', views.register_user, name='register_user'),
    path('signup/provider/', views.register_provider, name='register_provider'),
    path('profile/user/', views.user_profile, name='user_profile'),
    path('profile/provider/', views.provider_profile, name='provider_profile'),
    # API Endpoints
    path('api/user/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/provider/profile/', views.api_provider_profile, name='api_provider_profile'),
]

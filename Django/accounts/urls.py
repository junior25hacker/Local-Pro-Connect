from django.urls import path
<<<<<<< HEAD
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Provider
from .serializers import ProviderSerializer

class ProviderListAPIView(APIView):
    def get(self, request):
        service_type = request.GET.get('serviceType')
        if service_type:
            providers = Provider.objects.filter(service_type__iexact=service_type)
        else:
            providers = Provider.objects.all()
        serializer = ProviderSerializer(providers, many=True)
        return Response(serializer.data)

urlpatterns = [
    path('providers/', ProviderListAPIView.as_view(), name='provider-list'),
=======
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('auth/', views.auth_view, name='auth'),
<<<<<<< HEAD
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
=======
    path('signup/user/', views.register_user, name='register_user'),
    path('signup/provider/', views.register_provider, name='register_provider'),
    path('profile/user/', views.user_profile, name='user_profile'),
    path('profile/provider/', views.provider_profile, name='provider_profile'),
    # API Endpoints
    path('api/user/profile/', views.api_user_profile, name='api_user_profile'),
    path('api/provider/profile/', views.api_provider_profile, name='api_provider_profile'),
>>>>>>> main
]

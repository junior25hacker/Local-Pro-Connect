from django.urls import path
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
]

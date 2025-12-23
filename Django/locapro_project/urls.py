from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('api/', include('accounts.urls')),
=======
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
]

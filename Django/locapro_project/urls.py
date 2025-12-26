from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
<<<<<<< HEAD
    path('api/', include('accounts.urls')),
=======
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
]

# Serve pages directory
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^pages/(?P<path>.*)$', serve, {'document_root': settings.PAGES_ROOT}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

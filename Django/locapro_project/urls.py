from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('accounts.urls')),
]

# Serve pages directory and root index.html
if settings.DEBUG:
    ROOT_DIR = settings.BASE_DIR.parent
    urlpatterns += [
        re_path(r'^index\.html$', serve, {'document_root': ROOT_DIR, 'path': 'index.html'}),
        re_path(r'^pages/(?P<path>.*)$', serve, {'document_root': settings.PAGES_ROOT}),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

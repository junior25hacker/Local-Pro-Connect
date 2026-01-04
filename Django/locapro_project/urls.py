from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView, RedirectView
import os

urlpatterns = [
    path('admin/', admin.site.urls),
    # Aliases for convenience
    path('login/', RedirectView.as_view(url='/accounts/login/', permanent=False), name='alias_login'),
    path('signup/user/', RedirectView.as_view(url='/accounts/signup/user/', permanent=False), name='alias_signup_user'),
    path('signup/provider/', RedirectView.as_view(url='/accounts/signup/provider/', permanent=False), name='alias_signup_provider'),

    path('accounts/', include('accounts.urls')),
    path('requests/', include('requests.urls')),
    path('', include('accounts.urls')),
]

# Serve pages directory and root index.html
if settings.DEBUG:
    ROOT_DIR = settings.BASE_DIR.parent
    urlpatterns += [
        re_path(r'^index\.html$', serve, {'document_root': ROOT_DIR, 'path': 'index.html'}),
        re_path(r'^pages/(?P<path>.*)$', serve, {'document_root': settings.PAGES_ROOT}),
    ]
    # Serve static files (CSS, JS, images)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

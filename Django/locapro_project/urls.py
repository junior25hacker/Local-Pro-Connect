from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
from django.views.generic import TemplateView, RedirectView
from django.http import FileResponse
from accounts import views as accounts_views
import os


def serve_static_homepage(request):
    """Serve the static index.html as homepage"""
    static_index_path = os.path.join(settings.BASE_DIR.parent, 'index.html')
    try:
        return FileResponse(open(static_index_path, 'rb'), content_type='text/html')
    except FileNotFoundError:
        # Fallback to Django template if static file not found
        from django.shortcuts import render
        return render(request, 'index.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    # Custom login page (no redirect to /accounts/login/)
    path('login/', accounts_views.login_page, name='custom_login'),
    path('signup/user/', RedirectView.as_view(url='/accounts/signup/user/', permanent=False), name='alias_signup_user'),
    path('signup/provider/', RedirectView.as_view(url='/accounts/signup/provider/', permanent=False), name='alias_signup_provider'),

    path('accounts/', include('accounts.urls')),
    path('requests/', include('requests.urls')),
    path('api/requests/', include('requests.api_urls')),
    path('healthz/', accounts_views.healthz, name='healthz'),
    path('', serve_static_homepage, name='home'),
]

# Serve pages directory and root index.html
if settings.DEBUG:
    ROOT_DIR = settings.BASE_DIR.parent
    urlpatterns += [
        re_path(r'^index\.html$', serve, {'document_root': ROOT_DIR, 'path': 'index.html'}),
        # Redirect search.html to the protected Django view
        path('pages/search.html', RedirectView.as_view(url='/accounts/search/', permanent=False)),
        path('search.html', RedirectView.as_view(url='/accounts/search/', permanent=False)),
        re_path(r'^pages/(?P<path>.*)$', serve, {'document_root': settings.PAGES_ROOT}),
    ]
    # Serve static files (CSS, JS, images)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.BASE_DIR / 'static')
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

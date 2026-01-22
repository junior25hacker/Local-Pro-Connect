import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Load .env from project root (with override=True to ensure .env values are used)
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '..', '.env'), override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------------------------------------------
# Core security settings (environment-driven)
# -----------------------------------------------------------------------------
# IMPORTANT: Never hardcode SECRET_KEY in production.
# Set DJANGO_SECRET_KEY in the environment.
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')

# DEBUG must be False in production. Set DJANGO_DEBUG=false in production.
# Default to True for local/dev to avoid surprising breakage when env vars are missing.
DEBUG = os.environ.get('DJANGO_DEBUG', 'true').lower() == 'true'

# Allowed hosts should be explicitly configured (comma-separated)
# Example: DJANGO_ALLOWED_HOSTS=example.com,www.example.com
_allowed_hosts_env = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1')
ALLOWED_HOSTS = [h.strip() for h in _allowed_hosts_env.split(',') if h.strip()]

if not SECRET_KEY:
    if DEBUG:
        # Dev fallback only; production must set DJANGO_SECRET_KEY
        SECRET_KEY = 'django-insecure-dev-only-change-me'
    else:
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured('DJANGO_SECRET_KEY environment variable is required when DEBUG is False')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'requests',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'locapro_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates', BASE_DIR / 'accounts' / 'templates', BASE_DIR.parent / 'pages'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'accounts.context_processors.user_flags',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG,  # Disable template caching in debug mode
        },
    },
]

WSGI_APPLICATION = 'locapro_project.wsgi.application'

import dj_database_url

# Database configuration - uses PostgreSQL in production, SQLite in development
# Print database info for debugging (remove in final production)
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    print(f"[DEBUG] DATABASE_URL configured: postgresql connection detected")
    print(f"[DEBUG] Database host: {DATABASE_URL.split('@')[1].split(':')[0] if '@' in DATABASE_URL else 'unknown'}")
    print("[DEBUG] Will run migrations to create PostgreSQL tables")
else:
    print("[DEBUG] No DATABASE_URL found, falling back to SQLite")

DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR / "db.sqlite3"}',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# ============================================================================
# SESSION / CSRF CONFIGURATION
# ============================================================================
# Django uses session cookies to maintain user authentication across page reloads
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store sessions in database
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (14 * 24 * 60 * 60)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing the cookie
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = False

# Secure cookies in production (assumes HTTPS at the edge / load balancer)
SESSION_COOKIE_SECURE = (not DEBUG) and (os.environ.get('DJANGO_SESSION_COOKIE_SECURE', 'true').lower() == 'true')
CSRF_COOKIE_SECURE = (not DEBUG) and (os.environ.get('DJANGO_CSRF_COOKIE_SECURE', 'true').lower() == 'true')

CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Trust origins for CSRF (comma-separated). Example:
# DJANGO_CSRF_TRUSTED_ORIGINS=https://example.com,https://www.example.com
_csrf_trusted = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_trusted.split(',') if o.strip()]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Use WhiteNoise compressed manifest storage in production (if installed)
if not DEBUG:
    try:
        import whitenoise  # noqa: F401
        STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
        # Insert middleware right after SecurityMiddleware if available
        if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
            MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
    except Exception:
        # WhiteNoise not installed; staticfiles must be served by the platform/CDN.
        pass

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Pages directory for static HTML files
PAGES_ROOT = BASE_DIR.parent / 'pages'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# -----------------------------------------------------------------------------
# Production security headers (enable when DEBUG is False)
# -----------------------------------------------------------------------------
# If you are behind a reverse proxy / load balancer that terminates SSL, set:
#   DJANGO_SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
_proxy_ssl_header = os.environ.get('DJANGO_SECURE_PROXY_SSL_HEADER', '')
if _proxy_ssl_header:
    try:
        _hdr, _val = [p.strip() for p in _proxy_ssl_header.split(',', 1)]
        SECURE_PROXY_SSL_HEADER = (_hdr, _val)
    except ValueError:
        # Leave unset if malformed
        SECURE_PROXY_SSL_HEADER = None

if not DEBUG:
    # Redirect HTTP->HTTPS (can be disabled if handled entirely at the edge)
    SECURE_SSL_REDIRECT = os.environ.get('DJANGO_SECURE_SSL_REDIRECT', 'true').lower() == 'true'

    # HTTP Strict Transport Security (set a short value first; increase after verification)
    SECURE_HSTS_SECONDS = int(os.environ.get('DJANGO_SECURE_HSTS_SECONDS', '3600'))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.environ.get('DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS', 'true').lower() == 'true'
    # Enable preload by default for production readiness; you may disable via env if needed.
    SECURE_HSTS_PRELOAD = os.environ.get('DJANGO_SECURE_HSTS_PRELOAD', 'true').lower() == 'true'

    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_REFERRER_POLICY = 'same-origin'
else:
    # Development defaults
    SECURE_SSL_REDIRECT = False
    SECURE_HSTS_SECONDS = 0

# ============================================================================
# EMAIL CONFIGURATION - For Notifications
# ============================================================================
# Read from environment variables or derived from SMTP provider.
# Primary environment variables:
# - EMAIL_BACKEND (default: smtp backend)
# - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# - EMAIL_USE_TLS, EMAIL_USE_SSL
# - DEFAULT_FROM_EMAIL, SERVER_EMAIL
# Convenience: set SMTP_PROVIDER to 'gmail' or 'outlook' to auto-derive sensible defaults
# 
# Example .env configuration:
#   SMTP_PROVIDER=gmail
#   EMAIL_HOST_USER=your-email@gmail.com
#   EMAIL_HOST_PASSWORD=your-app-specific-password
#
# For development, if no SMTP user is configured, console backend will be used
# which prints emails to console instead of sending them.
#
SMTP_PROVIDER = os.environ.get('SMTP_PROVIDER', '').lower()

# Defaults for providers (SSL by default for security)
if SMTP_PROVIDER == 'gmail':
    default_host = 'smtp.gmail.com'
    default_port = 465
    default_use_ssl = True
    default_use_tls = False
elif SMTP_PROVIDER in ('outlook', 'office365', 'microsoft'):
    default_host = 'smtp-mail.outlook.com'
    default_port = 465
    default_use_ssl = True
    default_use_tls = False
else:
    default_host = ''
    default_port = 465
    default_use_ssl = True
    default_use_tls = False

EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', default_host)
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', str(default_port)))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'true' if default_use_tls else 'false').lower() == 'true'
EMAIL_USE_SSL = os.environ.get('EMAIL_USE_SSL', 'true' if default_use_ssl else 'false').lower() == 'true'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', EMAIL_HOST_USER or 'noreply@locapro.local')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Email timeout (seconds) to avoid hanging requests
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))

# In development, default to console backend if no SMTP user provided
if DEBUG and (not EMAIL_HOST_USER) and os.environ.get('EMAIL_BACKEND') is None:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Site Configuration
# SITE_URL used for building absolute links when request object is not available
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')

# Contact form receiver email
CONTACT_RECEIVER_EMAIL = os.environ.get('CONTACT_RECEIVER_EMAIL', 'sandracollehkayeh@gmail.com')

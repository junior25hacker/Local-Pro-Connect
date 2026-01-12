import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (with override=True to ensure .env values are used)
load_dotenv(os.path.join(Path(__file__).resolve().parent.parent, '..', '.env'), override=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-please-change-this-key'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '*']

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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
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
# SESSION CONFIGURATION - For Persistent Login
# ============================================================================
# Django uses session cookies to maintain user authentication across page reloads
SESSION_ENGINE = 'django.contrib.sessions.backends.db'  # Store sessions in database
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds (14 * 24 * 60 * 60)
SESSION_COOKIE_SECURE = False  # Set to True in production (requires HTTPS)
SESSION_COOKIE_HTTPONLY = True  # Prevent JavaScript from accessing the cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection: only send cookie with safe cross-site requests
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Session persists even after browser close
SESSION_SAVE_EVERY_REQUEST = False  # Only update session when data changes (more efficient)
CSRF_COOKIE_SECURE = False  # Set to True in production
CSRF_COOKIE_HTTPONLY = True  # Prevent JavaScript access to CSRF token
CSRF_COOKIE_SAMESITE = 'Lax'

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Pages directory for static HTML files
PAGES_ROOT = BASE_DIR.parent / 'pages'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

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

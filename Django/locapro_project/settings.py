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
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
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

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files (uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Pages directory for static HTML files
PAGES_ROOT = BASE_DIR.parent / 'pages'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration (read from environment variables or derived from provider)
# Primary envs (can be set directly):
# - EMAIL_BACKEND (default: smtp backend)
# - EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
# - EMAIL_USE_TLS, EMAIL_USE_SSL
# - DEFAULT_FROM_EMAIL, SERVER_EMAIL
# Convenience: set SMTP_PROVIDER to 'gmail' or 'outlook' to auto-derive sensible defaults
SMTP_PROVIDER = os.environ.get('SMTP_PROVIDER', '').lower()

# Defaults for providers (SSL by default as requested)
if SMTP_PROVIDER == 'gmail':
    default_host = 'smtp.gmail.com'
    default_port = 465
    default_use_ssl = True
    default_use_tls = False
elif SMTP_PROVIDER in ('outlook', 'office365', 'microsoft'):  # Outlook also supports TLS:587; honoring SSL per request
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

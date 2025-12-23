import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

<<<<<<< HEAD
SECRET_KEY = 'django-insecure-please-change-this-key'
=======
SECRET_KEY = 'replace-this-with-a-secure-key'
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
<<<<<<< HEAD
    'rest_framework',
=======
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
    'accounts',
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
<<<<<<< HEAD
        'DIRS': [],
=======
        'DIRS': [BASE_DIR / 'accounts' / 'templates'],
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112
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
<<<<<<< HEAD
USE_TZ = True

STATIC_URL = '/static/'
=======
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'assets']
>>>>>>> f9ab2a26f914e776428e2c1383a3ef813a0d9112

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Modal Backend - Setup & Deployment Guide

## Quick Start

### 1. Verify Installation

```bash
cd Django
python manage.py check
```

Expected output: No errors (only deployment warnings)

### 2. Test URL Configuration

```bash
python manage.py shell
from django.urls import reverse
print(reverse('requests:api_request_decline', kwargs={'request_id': 1}))
# Should print: /requests/api/1/decline/
```

### 3. Run Server

```bash
python manage.py runserver 0.0.0.0:8000
```

### 4. Test Decline Endpoint

```bash
# In another terminal
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: DUMMY" \
  -b "sessionid=YOUR_SESSION_ID" \
  -d '{"reason": "price"}'
```

---

## Environment Setup

### Prerequisites

```
Python 3.8+
Django 3.2+
PostgreSQL (recommended for production)
Redis (optional, for caching)
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Create Superuser (if needed)

```bash
python manage.py createsuperuser
```

### Run Migrations

```bash
python manage.py migrate
```

---

## Configuration

### Django Settings

Ensure these settings are in your `locapro_project/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'noreply@locapro.com'

# CSRF Protection
CSRF_COOKIE_SECURE = True  # In production
SESSION_COOKIE_SECURE = True  # In production
CSRF_COOKIE_HTTPONLY = False  # Required for AJAX

# Security
SECURE_SSL_REDIRECT = True  # In production
SECURE_HSTS_SECONDS = 31536000  # In production

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'django_runtime.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

---

## Testing the Implementation

### Manual Testing

#### Test Decline Endpoint

```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -b "sessionid=SESSION" \
  -d '{"reason": "price", "message": "Too expensive"}'
```

#### Check Database

```bash
python manage.py shell
```

```python
from requests.models import ServiceRequest
request = ServiceRequest.objects.get(id=1)
print(f"Status: {request.status}")
print(f"Reason: {request.decline_reason}")
```

---

## Deployment Checklist

- [ ] All tests passing
- [ ] No syntax errors  
- [ ] Database migrated
- [ ] Email configured
- [ ] CSRF settings correct
- [ ] Logging configured
- [ ] Security settings in place

---

## Troubleshooting

### CSRF Token Missing

```python
# In settings.py
CSRF_COOKIE_HTTPONLY = False  # Must be False for AJAX
```

### Permission Denied

Check that user is the correct provider/creator and is authenticated.

### Email Not Sending

```python
from requests.email_service import test_email_configuration
result = test_email_configuration()
print(result)
```

---

## Monitoring

### View Logs

```bash
tail -f django_runtime.log
```

### Monitor Key Metrics

```python
from django.db.models import Count
from requests.models import ServiceRequest
from django.utils import timezone
from datetime import timedelta

yesterday = timezone.now() - timedelta(days=1)

stats = {
    'total_requests': ServiceRequest.objects.filter(created_at__gte=yesterday).count(),
    'declined': ServiceRequest.objects.filter(status='declined', declined_at__gte=yesterday).count(),
    'accepted': ServiceRequest.objects.filter(status='accepted', accepted_at__gte=yesterday).count(),
}

print(stats)
```

---

**Status**: Ready for Production Deployment

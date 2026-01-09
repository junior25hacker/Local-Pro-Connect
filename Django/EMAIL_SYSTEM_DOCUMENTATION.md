# LocaPro Email System Documentation

## Overview

The email system provides comprehensive notification functionality for service requests, including:
- **Provider Notifications** - When new requests are submitted
- **User Confirmations** - When requests are created
- **Acceptance Notifications** - When providers accept requests
- **Decline Notifications** - When providers decline requests
- **Email Tracking** - Database tracking of all email operations
- **Retry Logic** - Automatic retries for failed emails
- **Async Sending** - Background thread-based email delivery

## Architecture

### Components

1. **Email Service Module** (`requests/email_service.py`)
   - Centralized email sending functions
   - Template rendering
   - Error handling and logging
   - Retry logic with exponential backoff
   - Async sending support

2. **Signals** (`requests/signals.py`)
   - Automatically triggered on request creation/update
   - Calls email service functions
   - Handles all email workflows

3. **Email Templates** (`requests/templates/emails/`)
   - HTML and plain text versions
   - Mobile-responsive design
   - Personalized content

4. **Database Tracking** (`ServiceRequest` model)
   - Email send status and timestamps
   - Response tracking

## Email Workflows

### 1. Request Submission Workflow

When a user creates a service request:

```
1. ServiceRequest.objects.create() is called
2. post_save signal triggers
3. send_request_to_provider() is called
   - Looks up provider email
   - Creates decision token (7-day expiration)
   - Generates accept/decline links
   - Renders HTML and text templates
   - Sends async email in background thread
   - Updates email_sent_to_provider = True

4. send_user_confirmation_email() is called
   - Renders confirmation templates
   - Sends async email to user
   - Updates email_sent_to_user = True
```

### 2. Provider Acceptance Workflow

When a provider accepts a request:

```
1. ServiceRequest.accept(provider) is called
2. post_save signal triggers (status changed to 'accepted')
3. send_acceptance_email() is called
   - Retrieves provider details
   - Renders acceptance templates
   - Sends async email to customer
   - Updates email_response_timestamp
```

### 3. Provider Decline Workflow

When a provider declines a request:

```
1. ServiceRequest.decline(reason, message) is called
2. post_save signal triggers (status changed to 'declined')
3. send_decline_email() is called
   - Includes decline reason and message
   - Renders decline templates
   - Sends async email to customer
   - Updates email_response_timestamp
```

## Configuration

### SMTP Configuration

Email configuration is managed through `Django/locapro_project/settings.py`. See SMTP_CONFIGURATION_GUIDE.md for detailed setup.

### Environment Variables

Configuration can be set via environment variables (`.env` file):

```bash
# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP Provider
SMTP_PROVIDER=gmail

# Gmail Configuration
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Site URL
SITE_URL=http://localhost:8000
```

## API Reference

### Core Functions

#### `send_request_to_provider(service_request, provider_profile=None, async_send=True)`

Sends notification email to provider when request is submitted.

#### `send_user_confirmation_email(service_request, async_send=True)`

Sends confirmation email to user after request submission.

#### `send_acceptance_email(service_request, async_send=True)`

Sends acceptance notification to customer when provider accepts.

#### `send_decline_email(service_request, decline_reason=None, decline_message=None, async_send=True)`

Sends decline notification to customer.

#### `test_email_configuration(recipient_email=None)`

Tests email configuration by sending a test email.

## Database Fields

The `ServiceRequest` model includes email tracking fields:

- `email_sent_to_provider` (bool)
- `email_sent_to_provider_timestamp` (datetime)
- `email_sent_to_user` (bool)
- `email_sent_to_user_timestamp` (datetime)
- `email_read_timestamp` (datetime)
- `email_response_timestamp` (datetime)

## Email Templates

Located in `Django/requests/templates/emails/`:

1. **request_to_provider_email.html/txt** - Provider notification
2. **request_confirmation_email.html/txt** - User confirmation
3. **request_accepted_email.html/txt** - Acceptance notification
4. **request_declined_email.html/txt** - Decline notification

## Testing

### Console Backend Test

```bash
cd Django
python manage.py shell

# In shell:
from requests.models import ServiceRequest
from django.contrib.auth.models import User

customer = User.objects.first()
request = ServiceRequest.objects.create(
    user=customer,
    provider_name='Test Provider',
    description='Test request',
)
# Emails printed to console
```

### Manual Function Testing

```python
from requests.email_service import (
    test_email_configuration,
    send_request_to_provider,
    send_acceptance_email,
)

# Test configuration
result = test_email_configuration()

# Test sending
request = ServiceRequest.objects.first()
result = send_request_to_provider(request, async_send=False)
```

## Troubleshooting

### Emails Not Sending

Check email configuration:
```python
from django.conf import settings
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
```

Test connection:
```python
from requests.email_service import test_email_configuration
result = test_email_configuration()
```

### SMTP Connection Errors

**Common causes:**
1. Invalid credentials
2. Firewall blocking port 465/587
3. Gmail app password not generated
4. SSL/TLS configuration incorrect

**Solutions:**
1. Verify credentials with your email provider
2. Check firewall settings
3. Generate app-specific password for Gmail
4. Use console backend for testing

## Best Practices

1. Use app-specific passwords for Gmail/Outlook
2. Test configuration before production
3. Monitor email logs
4. Use email service providers for production
5. Implement SPF/DKIM/DMARC
6. Personalize email content
7. Test all templates before deployment
8. Use async sending
9. Implement rate limiting
10. Log all email operations

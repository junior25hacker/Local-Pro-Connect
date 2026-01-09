# Email System Quick Reference

## Files Modified/Created

### New Files
- `requests/email_service.py` - Core email service module
- `requests/templates/emails/request_confirmation_email.html` - User confirmation
- `requests/templates/emails/request_confirmation_email.txt` - User confirmation
- `requests/migrations/0005_*.py` - Database schema migration
- `EMAIL_SYSTEM_DOCUMENTATION.md` - Full documentation
- `SMTP_CONFIGURATION_GUIDE.md` - SMTP setup guide

### Modified Files
- `requests/models.py` - Added email tracking fields
- `requests/signals.py` - Updated to use new email service
- `locapro_project/settings.py` - Already has email configuration

### Existing Templates Updated
- `requests/templates/emails/request_to_provider_email.html/txt`
- `requests/templates/emails/request_accepted_email.html/txt`
- `requests/templates/emails/request_declined_email.html/txt`

## Quick Setup

### 1. Development (Default - Console Backend)

No setup needed! Emails print to console.

### 2. Gmail Setup (5 minutes)

```bash
# 1. Go to https://myaccount.google.com/apppasswords
# 2. Generate app password
# 3. Set environment variables:

export SMTP_PROVIDER=gmail
export EMAIL_HOST_USER=your-email@gmail.com
export EMAIL_HOST_PASSWORD=your-app-password
export DEFAULT_FROM_EMAIL=your-email@gmail.com

# 4. Test
cd Django
python manage.py shell
from requests.email_service import test_email_configuration
print(test_email_configuration())
```

## Email Workflows

### When Request Created
```
User submits request
  ↓
Signal: post_save on ServiceRequest
  ↓
Email 1: send_request_to_provider()
  - Sends to: Provider email
  - Contains: Request details, accept/decline links
  
Email 2: send_user_confirmation_email()
  - Sends to: User email
  - Contains: Confirmation, next steps
```

### When Request Accepted
```
Provider clicks "Accept"
  ↓
Signal: post_save (status = 'accepted')
  ↓
Email: send_acceptance_email()
  - Sends to: User email
  - Contains: Provider details, next steps
```

### When Request Declined
```
Provider clicks "Decline"
  ↓
Signal: post_save (status = 'declined')
  ↓
Email: send_decline_email()
  - Sends to: User email
  - Contains: Decline reason, browse other providers
```

## Common Tasks

### Test Email Configuration

```python
from requests.email_service import test_email_configuration
result = test_email_configuration()
print(result)
```

### Get Current Configuration

```python
from requests.email_service import get_email_configuration_info
config = get_email_configuration_info()
print(config)
```

### Send Specific Email Manually

```python
from requests.email_service import (
    send_request_to_provider,
    send_acceptance_email,
    send_decline_email,
)
from requests.models import ServiceRequest

request = ServiceRequest.objects.get(id=1)

# Send provider notification
result = send_request_to_provider(request, async_send=False)
print(result)

# Send acceptance
result = send_acceptance_email(request, async_send=False)
print(result)

# Send decline
result = send_decline_email(request, async_send=False)
print(result)
```

### Check Email Tracking

```python
from requests.models import ServiceRequest

request = ServiceRequest.objects.get(id=1)
print(f"Provider email sent: {request.email_sent_to_provider}")
print(f"Provider email time: {request.email_sent_to_provider_timestamp}")
print(f"User email sent: {request.email_sent_to_user}")
print(f"User email time: {request.email_sent_to_user_timestamp}")
print(f"Response time: {request.email_response_timestamp}")
```

## Troubleshooting

### Emails Not Sending?

1. **Check backend:**
   ```python
   from django.conf import settings
   print(settings.EMAIL_BACKEND)
   ```

2. **Test connection:**
   ```python
   from requests.email_service import test_email_configuration
   result = test_email_configuration()
   ```

3. **Check logs:**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   # Try sending again
   ```

### Gmail Connection Error?

1. **Verify credentials:**
   - Email: `your-email@gmail.com`
   - Password: App-specific password (not regular password)
   - Source: https://myaccount.google.com/apppasswords

2. **Check environment variables:**
   ```bash
   echo $EMAIL_HOST_USER
   echo $EMAIL_HOST_PASSWORD
   ```

### Email Templates Missing?

All templates should be in:
```
Django/requests/templates/emails/
├── request_to_provider_email.html
├── request_to_provider_email.txt
├── request_confirmation_email.html
├── request_confirmation_email.txt
├── request_accepted_email.html
├── request_accepted_email.txt
├── request_declined_email.html
└── request_declined_email.txt
```

## Database Schema

Added to `ServiceRequest` model:

```python
email_sent_to_provider (bool)                  # Default: False
email_sent_to_provider_timestamp (datetime)    # Default: None
email_sent_to_user (bool)                      # Default: False
email_sent_to_user_timestamp (datetime)        # Default: None
email_read_timestamp (datetime)                # Default: None (future use)
email_response_timestamp (datetime)            # Default: None
```

## API Reference

### send_request_to_provider()
```python
result = send_request_to_provider(
    service_request,           # ServiceRequest instance
    provider_profile=None,     # ProviderProfile (auto-lookup if None)
    async_send=True           # Send in background thread
)
# Returns: {'success': bool, 'message': str, 'email_sent': bool}
```

### send_user_confirmation_email()
```python
result = send_user_confirmation_email(
    service_request,          # ServiceRequest instance
    async_send=True          # Send in background thread
)
# Returns: {'success': bool, 'message': str}
```

### send_acceptance_email()
```python
result = send_acceptance_email(
    service_request,          # ServiceRequest instance (must have provider)
    async_send=True          # Send in background thread
)
# Returns: {'success': bool, 'message': str}
```

### send_decline_email()
```python
result = send_decline_email(
    service_request,          # ServiceRequest instance
    decline_reason=None,      # Reason code
    decline_message=None,     # Custom message
    async_send=True          # Send in background thread
)
# Returns: {'success': bool, 'message': str}
```

### test_email_configuration()
```python
result = test_email_configuration(
    recipient_email=None      # Test recipient (defaults to DEFAULT_FROM_EMAIL)
)
# Returns: {'success': bool, 'message': str, 'config': dict}
```

### get_email_configuration_info()
```python
config = get_email_configuration_info()
# Returns: {
#     'backend': str,
#     'host': str,
#     'port': int,
#     'use_tls': bool,
#     'use_ssl': bool,
#     'from_email': str,
#     'host_user': str,
#     'smtp_provider': str,
# }
```

## Settings Reference

In `Django/locapro_project/settings.py`:

```python
# Email Backend
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')

# SMTP Configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '465'))
EMAIL_USE_SSL = True  # For port 465
EMAIL_USE_TLS = False  # Not with SSL
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')

# Default Emails
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@locapro.local')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)

# Timeout
EMAIL_TIMEOUT = int(os.environ.get('EMAIL_TIMEOUT', '10'))

# Site URL
SITE_URL = os.environ.get('SITE_URL', 'http://localhost:8000')
```

## Testing Checklist

- [ ] Email configuration loads correctly
- [ ] Console backend works (development)
- [ ] SMTP connection succeeds (if credentials set)
- [ ] Request submission triggers 2 emails
- [ ] Provider acceptance triggers 1 email
- [ ] Provider decline triggers 1 email
- [ ] Email tracking fields updated
- [ ] Decision tokens generated (7-day expiry)
- [ ] Email templates render without errors
- [ ] Emails contain correct personalization
- [ ] Links in emails are correct
- [ ] HTML and text versions both work

## Integration Points

### In Views
Signals handle emails automatically. Views don't need to call email functions directly.

### In Models
`ServiceRequest.accept()` and `ServiceRequest.decline()` trigger signals.

### Custom Integration
```python
from requests.email_service import send_request_to_provider

# Manual email send (if needed)
result = send_request_to_provider(service_request)
```

## Logging

All email operations logged to `requests.email_service`:

```python
import logging
logger = logging.getLogger('requests.email_service')
logger.info("Email sent")
logger.warning("Email retry")
logger.error("Email failed")
```

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Notes

- Emails sent asynchronously in background threads by default
- Doesn't block user requests
- Retry logic with 3 attempts and 2-second delays
- Should handle 100+ emails per request without issues
- For high volume, consider Celery task queue

## Future Enhancements

- [ ] Celery task queue integration
- [ ] Email open tracking
- [ ] Click tracking on decision links
- [ ] User email preferences
- [ ] Scheduled emails
- [ ] Email templates in admin
- [ ] SendGrid/AWS SES integration
- [ ] Email analytics dashboard
- [ ] A/B testing
- [ ] Bulk email operations

## Getting Help

1. **Read documentation:** `EMAIL_SYSTEM_DOCUMENTATION.md`
2. **SMTP setup:** `SMTP_CONFIGURATION_GUIDE.md`
3. **Check logs:** Enable DEBUG logging
4. **Test configuration:** `test_email_configuration()`
5. **Test send:** Call email functions directly
6. **Check database:** Verify email tracking fields
7. **Review templates:** Check template syntax and variables

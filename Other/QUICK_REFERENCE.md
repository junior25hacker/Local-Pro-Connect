# Service Request Workflow - Quick Reference

## 🎯 Quick Facts

- **Status:** ✅ Complete and tested
- **Email Backend:** Console (development), SMTP (production)
- **Token Expiration:** 7 days
- **One-Time Use:** Yes (tokens marked as used)
- **Automatic:** Yes (Django signals handle emails)

---

## 📂 Key Files

| File | Purpose |
|------|---------|
| `Django/requests/models.py` | Models: ServiceRequest, RequestDecisionToken |
| `Django/requests/forms.py` | ServiceRequestForm with provider_name |
| `Django/requests/views.py` | Views: create_request, provider_decision |
| `Django/requests/signals.py` | Email signal handlers |
| `Django/requests/utils.py` | Utility functions |
| `Django/requests/urls.py` | URL routing |
| `Django/requests/admin.py` | Admin interface |
| `Django/locapro_project/settings.py` | Email configuration |

---

## 🚀 Running the System

### Start Server
```bash
cd Django
python manage.py runserver
```

### Apply Migrations
```bash
python manage.py migrate requests
```

### Test Workflow
1. Visit: http://localhost:8000/requests/create/
2. Fill form with provider_name, description, etc.
3. Submit
4. Check console for email output
5. Copy decision link
6. Visit decision link to accept/decline

---

## 📧 Email Flow

```
User Creates Request
        ↓
Signal: send_provider_notification_email()
        ↓
Email sent to provider with decision links
        ↓
Provider clicks Accept/Decline link
        ↓
View validates token and processes decision
        ↓
Status updated (accepted/declined)
        ↓
Signal triggers appropriate notification
        ↓
Email sent to customer (accepted or declined)
```

---

## 🔑 Key Models

### ServiceRequest
```python
# Core fields
user                 # Who requested
provider             # Who accepted (optional)
provider_name        # Name/service type
description          # Service description
status               # pending/accepted/declined

# Optional fields
date_time            # When service needed
price_range          # Budget range
urgent               # Priority flag

# Decline fields
decline_reason       # Why declined
decline_message      # Additional notes

# Timestamps
created_at           # Request creation
accepted_at          # When accepted
declined_at          # When declined

# Methods
.accept(provider)    # Mark as accepted
.decline(reason, msg) # Mark as declined
```

### RequestDecisionToken
```python
service_request      # Associated request
token               # Secure random token
created_at          # Creation time
expires_at          # Expiration (7 days)
used                # Is it used?
used_at             # When used?

# Methods
.is_expired()       # Check expiration
.is_valid()         # Can be used?
.mark_as_used()     # Record usage
```

---

## 🔗 URL Endpoints

```
POST   /requests/create/                                    Create request
GET    /requests/success/                                   Success page
GET    /requests/decision/<id>/<action>/<token>/           Show decision page
POST   /requests/decision/<id>/<action>/<token>/           Process decision
```

**Actions:** `accept` or `decline`

---

## 📨 Email Templates

| Name | Sent To | Trigger |
|------|---------|---------|
| request_to_provider_email | Provider | Request created |
| request_accepted_email | Customer | Provider accepts |
| request_declined_email | Customer | Provider declines |

Each has `.html` and `.txt` versions.

---

## 🛡️ Security

- **Tokens:** Cryptographically secure, one-time use, 7-day expiration
- **CSRF:** Protected on all POST requests
- **Cache:** Decision pages never cached
- **TLS:** SMTP configured for encrypted email

---

## 🧪 Testing

### Create Test Request
```python
from requests.models import ServiceRequest
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

ServiceRequest.objects.create(
    user=user,
    provider_name='John Plumbing',
    description='Broken pipe',
    status='pending'
)
```

### Check Emails
```bash
# Emails print to console in development
# Look for email output with decision links
```

### Accept/Decline
```python
from requests.models import ServiceRequest

request = ServiceRequest.objects.first()

# Accept
provider_user = User.objects.get(username='provider')
request.accept(provider_user)

# Decline
request.decline('price', 'Too expensive')
```

---

## ⚙️ Configuration

### Development (Default)
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
# Emails print to console
```

### Production
```python
# In settings.py:
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# In .env:
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-password
SITE_URL=https://yourdomain.com
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Emails not appearing | Check EMAIL_BACKEND setting |
| Token invalid | Verify token hasn't expired (7 days) |
| Email not found | Check ProviderProfile.company_name |
| Signal not firing | Verify apps.py ready() method called |
| 404 on decision link | Check token and request ID in URL |

---

## 📊 Admin Interface

### Service Requests
- View all requests with status, user, provider
- Filter by status, urgency, date
- Search by description or provider name
- See inline photos and decision tokens

### Decision Tokens
- Monitor token usage and expiration
- See which tokens are valid
- Track when tokens are used

---

## 📝 Form Fields

### create_request POST

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| provider_name | CharField | Yes | Name of provider/service |
| description | TextField | Yes | What they need |
| date_time | DateTime | No | When they need it |
| price_range | Select | No | Budget range |
| urgent | Checkbox | No | Priority flag |
| photos | File | No | Multiple files ok |

---

## 🔌 Signal Handlers

All in `requests/signals.py`:

1. **send_provider_notification_email**
   - Triggers: On ServiceRequest creation
   - Creates: Decision token, generates URLs
   - Sends: Email to provider with links

2. **send_acceptance_notification_email**
   - Triggers: On status change to 'accepted'
   - Sends: Email to customer with confirmation

3. **send_decline_notification_email**
   - Triggers: On status change to 'declined'
   - Sends: Email to customer with reason

---

## 📦 Dependencies

- Django 3.2+ (or current version)
- Python 3.8+
- Built-in modules: smtplib, secrets, hmac

No external email libraries required.

---

## 🎓 Common Tasks

### Create a request programmatically
```python
ServiceRequest.objects.create(
    user=user,
    provider_name='Service Name',
    description='Description',
    urgent=True
)
# Email automatically sent via signal
```

### Accept a request
```python
request = ServiceRequest.objects.get(id=1)
provider = User.objects.get(username='provider')
request.accept(provider)
# Email automatically sent via signal
```

### Decline a request
```python
request = ServiceRequest.objects.get(id=1)
request.decline('price', 'Too low for this job')
# Email automatically sent via signal
```

### Get request status
```python
request = ServiceRequest.objects.get(id=1)
print(request.status)  # pending, accepted, or declined
```

### Check if token is valid
```python
token = RequestDecisionToken.objects.get(service_request_id=1)
if token.is_valid():
    print("Token can be used")
else:
    print("Token expired or already used")
```

---

## 📋 Status Values

| Status | Meaning | Next |
|--------|---------|------|
| pending | Waiting for provider | Accept/Decline |
| accepted | Provider accepted | Complete |
| declined | Provider declined | Retry with different provider |

---

## 🎯 Decline Reasons

| Code | Display |
|------|---------|
| price | Price too low |
| distance | Too far away |
| other | Other reason |
| no_reason | No reason provided |

---

*For detailed documentation, see WORKFLOW_IMPLEMENTATION.md*

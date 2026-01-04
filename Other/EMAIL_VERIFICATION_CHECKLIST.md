# Email Workflow - Verification Checklist

Complete this checklist to ensure your email workflow is working properly.

---

## Phase 1: Environment Setup

### Email Variables Exported
- [ ] `SMTP_PROVIDER` set (gmail/outlook/manual)
- [ ] `EMAIL_BACKEND` set correctly
- [ ] `EMAIL_HOST` set to SMTP server
- [ ] `EMAIL_PORT` set to correct port (465 for SSL)
- [ ] `EMAIL_USE_SSL` set to true (for Gmail/Outlook)
- [ ] `EMAIL_USE_TLS` set to false (when using SSL)
- [ ] `EMAIL_HOST_USER` set to email address
- [ ] `EMAIL_HOST_PASSWORD` set to password/app-password
- [ ] `DEFAULT_FROM_EMAIL` set
- [ ] `SERVER_EMAIL` set
- [ ] `SITE_URL` set to http://localhost:8000

**Verification Command:**
```bash
# Check if variables are exported
env | grep EMAIL_
env | grep SITE_URL
```

---

## Phase 2: Email Credentials

### Gmail Setup (if using Gmail)
- [ ] 2-Step Verification enabled on Gmail account
- [ ] App password generated (not regular password)
- [ ] App password is 16 characters
- [ ] Using app password in `EMAIL_HOST_PASSWORD` (not Gmail password)

### Outlook Setup (if using Outlook)
- [ ] Email address is correct
- [ ] Password is correct
- [ ] Account doesn't require app password (or app password is used)

---

## Phase 3: Connection Testing

### Connection Test
```bash
cd Django
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import get_connection
connection = get_connection()
connection.open()
print("✓ Connected successfully")
connection.close()
```

- [ ] Connection opens without errors
- [ ] No SMTPAuthenticationError
- [ ] No timeout errors

**If Connection Fails:**
- [ ] Verify EMAIL_HOST_USER is correct email
- [ ] Verify EMAIL_HOST_PASSWORD is correct (app password for Gmail)
- [ ] Verify EMAIL_PORT matches provider (465 for SSL)
- [ ] Verify EMAIL_USE_SSL=true and EMAIL_USE_TLS=false

---

## Phase 4: Simple Email Test

### Send Test Email
```bash
cd Django
python manage.py shell
```

Then in the shell:
```python
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

subject = "Test Email from LocaPro"
text_body = "This is a test email from LocaPro workflow testing."
html_body = "<h1>LocaPro Test Email</h1><p>If you see this, email is working!</p>"

email = EmailMultiAlternatives(
    subject=subject,
    body=text_body,
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=["recipient@example.com"]  # Change to your test email
)
email.attach_alternative(html_body, "text/html")
result = email.send()

print(f"Email sent: {result}")  # Should print: Email sent: 1
exit()
```

- [ ] Script runs without errors
- [ ] `result` equals 1 (email sent successfully)
- [ ] Email appears in recipient inbox within 30 seconds

**If Email Doesn't Arrive:**
- [ ] Check spam/junk folder
- [ ] Wait 1-2 minutes (Gmail can be slow)
- [ ] Check email headers for bounce message
- [ ] Verify recipient address is correct

---

## Phase 5: Test User Creation

### Create Test Accounts
```bash
cd Django
python manage.py shell
```

Then in the shell:
```python
from django.contrib.auth.models import User
from accounts.models import ProviderProfile

# Create customer user
customer = User.objects.create_user(
    username='test_customer',
    email='your_test_email@gmail.com',  # Use YOUR email
    password='testpass123',
    first_name='Test',
    last_name='Customer'
)

# Create provider user
provider = User.objects.create_user(
    username='test_provider',
    email='your_provider_email@gmail.com',  # Use a DIFFERENT email if possible
    password='testpass123',
    first_name='Test',
    last_name='Provider'
)

# Create provider profile
profile = ProviderProfile.objects.create(
    user=provider,
    company_name="Test Provider Company"
)

print(f"✓ Created: {customer.username} ({customer.email})")
print(f"✓ Created: {provider.username} ({provider.email})")
print(f"✓ Created profile: {profile.company_name}")
exit()
```

- [ ] Customer user created
- [ ] Provider user created
- [ ] Provider profile created with company name

---

## Phase 6: Full Workflow Test

### Run Automated Test Script
```bash
cd Django
python manage.py shell < scripts/test_email_workflow.py
```

Expected Output:
- [ ] Email configuration verified
- [ ] Email connection successful
- [ ] Test users created
- [ ] Service request created
- [ ] Decision token generated
- [ ] Token expires in 7 days
- [ ] Provider acceptance processed

**Check Email Inbox:**
- [ ] Received email from `DEFAULT_FROM_EMAIL`
- [ ] Subject contains "New Service Request"
- [ ] Email contains request details
- [ ] Email has Accept and Decline buttons/links
- [ ] Accept and Decline links are clickable
- [ ] Links contain token (long alphanumeric string)

---

## Phase 7: Provider Decision Flow

### Test Accept Workflow
1. **Copy Accept Link** from the email (right-click → Copy Link)
2. **Open in Browser** (paste in address bar)
3. **Verify Confirmation Page** shows
   - [ ] Request details display correctly
   - [ ] Customer name shown
   - [ ] Provider name shown
   - [ ] "Accept Request" button visible
4. **Submit Acceptance**
   - [ ] Click "Accept Request" button
   - [ ] Confirmation page shows "successfully accepted"
   - [ ] Database updated: `SELECT status FROM requests_servicerequest WHERE id=1;`

**Check Customer Email:**
- [ ] Customer receives "Your Service Request Has Been Accepted"
- [ ] Email contains provider details
- [ ] Email contains "accepted" status

### Test Decline Workflow
1. **Copy Decline Link** from another test email
2. **Open in Browser**
3. **Verify Confirmation Page**
   - [ ] Request details display correctly
   - [ ] "Decline Request" button visible
   - [ ] Decline reason options show
4. **Submit Decline**
   - [ ] Select decline reason
   - [ ] Enter optional message
   - [ ] Click "Decline Request"
   - [ ] Confirmation page shows "successfully declined"

**Check Customer Email:**
- [ ] Customer receives "Service Request Update" (decline notification)
- [ ] Email contains decline reason
- [ ] Email contains optional decline message

---

## Phase 8: Token Expiration

### Verify 7-Day Expiration
```bash
cd Django
python manage.py shell

from requests.models import RequestDecisionToken
from django.utils import timezone

token = RequestDecisionToken.objects.first()
print(f"Created: {token.created_at}")
print(f"Expires: {token.expires_at}")
days = (token.expires_at - timezone.now()).days
print(f"Days until expiration: {days}")
print(f"Is valid: {token.is_valid()}")

# Manually set expiration to past for testing
from datetime import timedelta
token.expires_at = timezone.now() - timedelta(hours=1)
token.save()
print(f"Manually expired token - Is valid now: {token.is_valid()}")

exit()
```

- [ ] Token created timestamp recorded
- [ ] Token expiration is 7 days in future
- [ ] Token marked as valid (not expired, not used)
- [ ] After expiration, token becomes invalid
- [ ] Expired token link shows error page

---

## Phase 9: Email Template Verification

### Render and Check Templates
```bash
cd Django
python manage.py shell

from django.template.loader import render_to_string

# Test provider notification template
context = {
    'request_id': 1,
    'provider_name': 'Test Provider',
    'customer_name': 'Test Customer',
    'description': 'Test service request',
    'urgent': True,
    'created_at': '2024-01-15 10:30 AM',
    'accept_link': 'http://localhost:8000/requests/1/accept/token123',
    'decline_link': 'http://localhost:8000/requests/1/decline/token123',
    'expires_at': '2024-01-22 10:30 AM',
}

html = render_to_string('emails/request_to_provider_email.html', context)
txt = render_to_string('emails/request_to_provider_email.txt', context)

print("HTML Length:", len(html))
print("Text Length:", len(txt))
print("✓ Templates render successfully")

exit()
```

- [ ] HTML template renders without error
- [ ] Text template renders without error
- [ ] HTML contains all context variables
- [ ] Links are properly formatted

---

## Phase 10: Database Verification

### Check Request States
```bash
sqlite3 db.sqlite3

-- View all service requests
SELECT id, user_id, provider_name, status, created_at FROM requests_servicerequest;

-- View decision tokens
SELECT id, service_request_id, used, is_expired FROM requests_requestdecisiontoken;

-- View photos (if any)
SELECT id, service_request_id FROM requests_requestphoto;

.quit
```

- [ ] Requests created with correct status (pending)
- [ ] Provider name matches
- [ ] Timestamps are recent
- [ ] Decision tokens have valid expiration
- [ ] Status updates to accepted/declined after decision

---

## Phase 11: End-to-End Manual Test

### Complete User Journey
1. **Start fresh** (optional: reset test database)
2. **Create new user** via web UI at `/accounts/register/`
3. **Create new provider** via web UI at `/accounts/register/provider/`
4. **Log in as user**
5. **Create service request** at `/requests/create/`
   - [ ] Form submits successfully
   - [ ] Redirected to success page
6. **Check email**
   - [ ] Provider receives notification email
   - [ ] Email appears within 30 seconds
7. **Click Accept/Decline link**
   - [ ] Link is clickable and opens in browser
   - [ ] Shows confirmation page
8. **Submit decision**
   - [ ] Confirmation message shows
9. **Check email again**
   - [ ] Customer receives notification
   - [ ] Notification includes correct decision status

---

## Phase 12: Troubleshooting Log

### Enable Debug Logging
Add to `Django/locapro_project/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'email_debug.log',
        },
    },
    'loggers': {
        'django.core.mail': {
            'handlers': ['file'],
            'level': 'DEBUG',
        },
    },
}
```

Then check logs:
```bash
tail -f Django/email_debug.log
```

- [ ] Debug logs show email sending attempts
- [ ] Any errors logged clearly
- [ ] Connection details logged
- [ ] Email recipients logged

---

## Final Checklist Summary

**Core Functionality:**
- [ ] Email variables exported correctly
- [ ] Connection to SMTP server successful
- [ ] Simple test email sent and received
- [ ] Test accounts created
- [ ] Service request workflow completes
- [ ] Provider notification email sent
- [ ] Provider can accept/decline request
- [ ] Customer receives confirmation email
- [ ] Decision tokens work and expire properly

**Quality Checks:**
- [ ] Emails render HTML and text correctly
- [ ] All request details display in emails
- [ ] Links are clickable and valid
- [ ] Tokens expire after 7 days
- [ ] Used tokens cannot be reused
- [ ] Error handling works (expired token shows error)
- [ ] No email sending errors in logs

---

## Support & Next Steps

If all checks pass:
- ✓ Email workflow is fully functional
- ✓ Ready for production deployment

If any checks fail:
1. See **Troubleshooting** section in `EMAIL_WORKFLOW_TESTING_GUIDE.md`
2. Check email provider logs (Gmail Security, Outlook Activity)
3. Review Django error logs
4. Verify firewall/network access to SMTP server
5. Test with different email provider if first choice fails

For detailed troubleshooting: See `EMAIL_WORKFLOW_TESTING_GUIDE.md` → **Troubleshooting** section

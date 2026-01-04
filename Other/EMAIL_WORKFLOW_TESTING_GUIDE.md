# Email Request Workflow - Testing & Setup Guide

## Table of Contents
1. [Email Configuration](#email-configuration)
2. [Environment Variable Setup](#environment-variable-setup)
3. [Testing the Workflow](#testing-the-workflow)
4. [Verification Methods](#verification-methods)
5. [Troubleshooting](#troubleshooting)

---

## Email Configuration

### Overview
The LocaPro email system sends notifications at three key points in the workflow:

| Event | Recipient | Template | Trigger |
|-------|-----------|----------|---------|
| **New Request** | Provider | `request_to_provider_email` | When user creates service request |
| **Request Accepted** | Customer | `request_accepted_email` | When provider clicks accept link |
| **Request Declined** | Customer | `request_declined_email` | When provider clicks decline link |

### Architecture
- **Backend**: Django SMTP (EmailMultiAlternatives)
- **Email Types**: HTML + Plain Text (fallback)
- **Security**: Secure decision tokens with 7-day expiration
- **Token Storage**: `RequestDecisionToken` model in database

---

## Environment Variable Setup

### Step 1: Export EMAIL Configuration Variables

Choose your email provider and export the variables to your shell environment:

#### **Option A: Gmail (Recommended for Testing)**

```bash
# Export Gmail Configuration
export SMTP_PROVIDER=gmail
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp.gmail.com
export EMAIL_PORT=465
export EMAIL_USE_TLS=false
export EMAIL_USE_SSL=true
export EMAIL_HOST_USER="your_email@gmail.com"
export EMAIL_HOST_PASSWORD="your_app_password_here"
export DEFAULT_FROM_EMAIL="your_email@gmail.com"
export SERVER_EMAIL="your_email@gmail.com"
export SITE_URL=http://localhost:8000
```

**Gmail App Password Setup:**
1. Go to myaccount.google.com
2. Select "Security" (left sidebar)
3. Enable "2-Step Verification" if not already enabled
4. Go back to Security, scroll to "App passwords"
5. Select "Mail" and "Windows Computer" (or your device)
6. Copy the 16-character password
7. Use this as `EMAIL_HOST_PASSWORD`

#### **Option B: Outlook/Office 365**

```bash
# Export Outlook Configuration
export SMTP_PROVIDER=outlook
export EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
export EMAIL_HOST=smtp-mail.outlook.com
export EMAIL_PORT=465
export EMAIL_USE_TLS=false
export EMAIL_USE_SSL=true
export EMAIL_HOST_USER="your_email@outlook.com"
export EMAIL_HOST_PASSWORD="your_password"
export DEFAULT_FROM_EMAIL="your_email@outlook.com"
export SERVER_EMAIL="your_email@outlook.com"
export SITE_URL=http://localhost:8000
```

#### **Option C: Development/Testing (Console Output)**

For testing without actually sending emails:

```bash
# Use Console Backend (prints to console instead of sending)
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export DEFAULT_FROM_EMAIL=test@locapro.local
export SITE_URL=http://localhost:8000
```

### Step 2: Verify Environment Variables

```bash
# Display current email configuration
echo "=== Email Configuration ==="
echo "SMTP_PROVIDER: $SMTP_PROVIDER"
echo "EMAIL_HOST: $EMAIL_HOST"
echo "EMAIL_PORT: $EMAIL_PORT"
echo "EMAIL_USE_SSL: $EMAIL_USE_SSL"
echo "EMAIL_HOST_USER: $EMAIL_HOST_USER"
echo "DEFAULT_FROM_EMAIL: $DEFAULT_FROM_EMAIL"
echo "SITE_URL: $SITE_URL"
```

### Step 3: Persist Configuration (Optional)

Add to your `.env` file for permanent storage:

```bash
# Add to .env file
SMTP_PROVIDER=gmail
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_TLS=false
EMAIL_USE_SSL=true
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password_here
DEFAULT_FROM_EMAIL=your_email@gmail.com
SERVER_EMAIL=your_email@gmail.com
SITE_URL=http://localhost:8000
```

Then load with:
```bash
set -a
source .env
set +a
```

---

## Testing the Workflow

### Prerequisites
```bash
# 1. Make sure you're in the Django directory
cd Django

# 2. Activate virtual environment
source ../venv/bin/activate

# 3. Export email configuration (see Step 1 above)
export EMAIL_HOST_USER="your_email@gmail.com"
export EMAIL_HOST_PASSWORD="your_app_password"
# ... (export other variables)

# 4. Run migrations if needed
python manage.py migrate

# 5. Create test data (optional)
python manage.py shell < ../Django/scripts/create_test_data.py
```

### Test 1: Send Test Email Directly

```bash
# From Django directory
python manage.py shell

# Inside shell:
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

subject = "Test Email - LocaPro"
text_body = "This is a plain text test email."
html_body = "<h1>This is an HTML test email</h1>"
from_email = settings.DEFAULT_FROM_EMAIL
to_email = "recipient@example.com"

email = EmailMultiAlternatives(subject, text_body, from_email, [to_email])
email.attach_alternative(html_body, "text/html")
result = email.send()

print(f"Email sent: {result}")  # Should print: Email sent: 1
exit()
```

### Test 2: Test Complete Request Workflow

See **test_email_workflow.py** script (provided separately)

### Test 3: Manual Web UI Testing

1. **Start Django server:**
   ```bash
   python manage.py runserver
   ```

2. **Create user account:**
   - Navigate to `http://localhost:8000/accounts/register/`
   - Create a regular user account

3. **Create provider account:**
   - Navigate to `http://localhost:8000/accounts/register/provider/`
   - Create a provider account
   - **Important**: Use a real email address you have access to

4. **Create service request:**
   - Log in as regular user
   - Navigate to `/requests/create/`
   - Fill in the form:
     - Provider Name: (Match the provider's company name exactly)
     - Description: Test request
     - Leave other fields optional or fill as desired
   - Submit

5. **Check email:**
   - Check provider's inbox for: "New Service Request"
   - Verify all request details are displayed
   - Click "Accept Request" or "Decline Request" link

6. **Verify decision email:**
   - Log out or use different email
   - Check customer's inbox for acceptance/decline notification

---

## Verification Methods

### Method 1: Django Shell Inspection

```bash
python manage.py shell

# Check sent emails (if using Console backend)
from django.core.mail import outbox
print(f"Emails sent: {len(outbox)}")
for email in outbox:
    print(f"  To: {email.to}")
    print(f"  Subject: {email.subject}")

# Check service requests
from requests.models import ServiceRequest
requests = ServiceRequest.objects.all()
for r in requests:
    print(f"Request #{r.id}: {r.status}")

# Check decision tokens
from requests.models import RequestDecisionToken
tokens = RequestDecisionToken.objects.all()
for t in tokens:
    print(f"Token for Request #{t.service_request_id}: Valid={t.is_valid()}")

exit()
```

### Method 2: Database Queries

```bash
sqlite3 db.sqlite3

-- Check requests created
SELECT id, provider_name, status, created_at FROM requests_servicerequest;

-- Check decision tokens
SELECT id, service_request_id, used, expires_at FROM requests_requestdecisiontoken;

-- Check request photos
SELECT id, service_request_id FROM requests_requestphoto;

.quit
```

### Method 3: Log File Analysis

```bash
# Check Django logs
tail -f django_runtime.log

# Search for email-related messages
grep -i "email" django_runtime.log
grep -i "sending" django_runtime.log
grep -i "error" django_runtime.log
```

### Method 4: Email Provider's Web UI

**Gmail:**
- Log into Gmail at mail.google.com
- Check "Sent Mail" folder for outgoing emails
- Check "All Mail" for both sent and received

**Outlook:**
- Log into Outlook at outlook.com
- Check "Sent Items" folder
- Verify email headers and content

---

## Troubleshooting

### Issue: "SMTPAuthenticationError"

**Cause**: Invalid credentials
```bash
# Solution: Verify email credentials
export EMAIL_HOST_USER="correct_email@gmail.com"
export EMAIL_HOST_PASSWORD="correct_app_password"

# Test connection
python manage.py shell
from django.core.mail import get_connection
connection = get_connection()
try:
    connection.open()
    print("✓ Connection successful!")
    connection.close()
except Exception as e:
    print(f"✗ Connection failed: {e}")
exit()
```

### Issue: "SMTPServerDisconnected" or Connection Timeout

**Cause**: Wrong port or SSL/TLS mismatch
```bash
# Gmail fix:
export EMAIL_PORT=465
export EMAIL_USE_SSL=true
export EMAIL_USE_TLS=false

# Outlook fix:
export EMAIL_PORT=465
export EMAIL_USE_SSL=true
export EMAIL_USE_TLS=false
```

### Issue: Provider Email Not Found

**Cause**: Provider name doesn't match database
```bash
# Check provider in database
python manage.py shell
from accounts.models import ProviderProfile
providers = ProviderProfile.objects.all()
for p in providers:
    print(f"Company: {p.company_name} | User: {p.user.email}")
exit()

# Use exact company name when creating request
```

### Issue: Emails Not Appearing in Inbox

**Cause**: Sent to SMTP but not delivered
```bash
# Check email headers and bounce messages
# 1. Enable "All Mail" view in Gmail/Outlook
# 2. Search for the recipient address
# 3. Check spam/junk folder
# 4. Look for bounce/delivery failure messages

# Debug: Use console backend to verify email is being sent
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
python manage.py runserver
# Create a request - email will print to console
```

### Issue: Templates Not Rendering Properly

**Cause**: Template not found or context missing
```bash
# Verify template paths
ls -la Django/requests/templates/emails/

# Check template syntax errors
python manage.py shell
from django.template.loader import render_to_string
try:
    html = render_to_string('emails/request_to_provider_email.html', {'request_id': 1})
    print("✓ Template renders successfully")
except Exception as e:
    print(f"✗ Template error: {e}")
exit()
```

---

## Email Workflow Diagram

```
User creates request
        ↓
ServiceRequest saved to DB
        ↓
Signal: post_save triggered
        ↓
Generate secure token → Store in RequestDecisionToken
        ↓
Render email templates (HTML + TXT)
        ↓
Send to Provider via SMTP
        ↓
Provider receives email with Accept/Decline links
        ↓
Provider clicks link (7-day expiration)
        ↓
Confirmation page shown (GET)
        ↓
Provider submits form (POST)
        ↓
Update ServiceRequest status
        ↓
Mark token as used
        ↓
Send notification email to Customer
        ↓
Customer receives acceptance/decline notification
```

---

## Quick Reference Commands

```bash
# Export Gmail
export SMTP_PROVIDER=gmail EMAIL_HOST=smtp.gmail.com EMAIL_PORT=465 EMAIL_USE_SSL=true EMAIL_USE_TLS=false EMAIL_HOST_USER="test@gmail.com" EMAIL_HOST_PASSWORD="password" DEFAULT_FROM_EMAIL="test@gmail.com" SITE_URL=http://localhost:8000

# Export Outlook
export SMTP_PROVIDER=outlook EMAIL_HOST=smtp-mail.outlook.com EMAIL_PORT=465 EMAIL_USE_SSL=true EMAIL_USE_TLS=false EMAIL_HOST_USER="test@outlook.com" EMAIL_HOST_PASSWORD="password" DEFAULT_FROM_EMAIL="test@outlook.com" SITE_URL=http://localhost:8000

# Use console (for testing without actual email)
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Start server
cd Django && python manage.py runserver

# Test connection
python manage.py shell -c "from django.core.mail import get_connection; c = get_connection(); c.open(); print('✓ Connected'); c.close()"

# View emails (console backend)
python manage.py shell -c "from django.core.mail import outbox; print(f'Emails: {len(outbox)}')"
```

---

## Success Checklist

- [ ] EMAIL_HOST_USER is set and valid
- [ ] EMAIL_HOST_PASSWORD is set (Gmail app password or email password)
- [ ] EMAIL_PORT matches provider (465 for SSL)
- [ ] EMAIL_USE_SSL=true (for Gmail/Outlook)
- [ ] EMAIL_USE_TLS=false (when using SSL)
- [ ] DEFAULT_FROM_EMAIL is set
- [ ] SITE_URL is correct
- [ ] Test email sent successfully
- [ ] Provider received request email
- [ ] Customer received acceptance/decline email
- [ ] Decision links work and have 7-day expiration
- [ ] Tokens marked as used after decision
- [ ] No SMTPAuthenticationError
- [ ] No connection timeouts

---

## Support

For issues with:
- **Gmail SMTP**: Use port 465, SSL=true, TLS=false, app password required
- **Outlook SMTP**: Use port 465, SSL=true, TLS=false
- **Custom SMTP**: Set EMAIL_HOST, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD explicitly
- **Console testing**: Use EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend


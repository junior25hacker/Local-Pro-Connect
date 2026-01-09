# Email Request Workflow - Complete Testing Instructions

## Quick Start (5 Minutes)

### Step 1: Export Email Variables

Choose your provider and run one of these commands:

**Gmail:**
```bash
export SMTP_PROVIDER=gmail \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp.gmail.com \
  EMAIL_PORT=465 \
  EMAIL_USE_TLS=false \
  EMAIL_USE_SSL=true \
  EMAIL_HOST_USER="your_email@gmail.com" \
  EMAIL_HOST_PASSWORD="your_16char_app_password" \
  DEFAULT_FROM_EMAIL="your_email@gmail.com" \
  SERVER_EMAIL="your_email@gmail.com" \
  SITE_URL=http://localhost:8000
```

**Outlook:**
```bash
export SMTP_PROVIDER=outlook \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp-mail.outlook.com \
  EMAIL_PORT=465 \
  EMAIL_USE_TLS=false \
  EMAIL_USE_SSL=true \
  EMAIL_HOST_USER="your_email@outlook.com" \
  EMAIL_HOST_PASSWORD="your_password" \
  DEFAULT_FROM_EMAIL="your_email@outlook.com" \
  SERVER_EMAIL="your_email@outlook.com" \
  SITE_URL=http://localhost:8000
```

**Console (Development - prints to console, no actual emails):**
```bash
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend \
  DEFAULT_FROM_EMAIL=test@locapro.local \
  SITE_URL=http://localhost:8000
```

### Step 2: Verify Variables

```bash
echo "Email Configuration:"
env | grep -E "^(SMTP_PROVIDER|EMAIL_|DEFAULT_FROM|SITE_URL)" | sort
```

### Step 3: Test Connection

```bash
cd Django
python manage.py shell -c "
from django.core.mail import get_connection
try:
    c = get_connection()
    c.open()
    print('✓ Email connection successful!')
    c.close()
except Exception as e:
    print(f'✗ Connection failed: {e}')
"
```

### Step 4: Run Full Test

```bash
cd Django
python manage.py shell < scripts/test_email_workflow.py
```

### Step 5: Check Email

Open your email inbox and look for:
- **Subject:** "New Service Request"
- **From:** Your configured email address
- **Contains:** Request details, Accept/Decline buttons

---

## Detailed Testing Guide

### Environment Variable Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `SMTP_PROVIDER` | Email provider type | `gmail`, `outlook` |
| `EMAIL_BACKEND` | Django email backend | `django.core.mail.backends.smtp.EmailBackend` |
| `EMAIL_HOST` | SMTP server hostname | `smtp.gmail.com` |
| `EMAIL_PORT` | SMTP server port | `465` (SSL) or `587` (TLS) |
| `EMAIL_USE_SSL` | Use SSL encryption | `true` or `false` |
| `EMAIL_USE_TLS` | Use TLS encryption | `true` or `false` |
| `EMAIL_HOST_USER` | SMTP username | `your_email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | SMTP password | (Gmail app password, not Gmail password) |
| `DEFAULT_FROM_EMAIL` | Sender email address | `your_email@gmail.com` |
| `SERVER_EMAIL` | Server error email | `your_email@gmail.com` |
| `SITE_URL` | Base URL for links | `http://localhost:8000` |

### Gmail App Password Setup

1. Go to **myaccount.google.com**
2. Click **Security** in the left sidebar
3. Enable **2-Step Verification** (if not already enabled)
4. Go back to Security, scroll to **App passwords**
5. Select:
   - App: **Mail**
   - Device: **Windows Computer** (or your OS)
6. Copy the **16-character password**
7. Use this in `EMAIL_HOST_PASSWORD` (not your Gmail password!)

### Outlook Setup

- **Host:** `smtp-mail.outlook.com`
- **Port:** `465`
- **SSL:** `true`
- **TLS:** `false`
- **Username:** Full email address
- **Password:** Your Outlook password (or app password if enabled)

---

## Testing Workflow

### Option A: Automated Testing (Recommended)

**Step 1: Run the test script**
```bash
cd Django
python manage.py shell < scripts/test_email_workflow.py
```

This script will:
- Verify email configuration
- Test SMTP connection
- Create test users (customer & provider)
- Create a service request
- Generate decision token (7-day expiration)
- Send provider notification email
- Process provider acceptance
- Send customer confirmation email
- Display all links and details

**Step 2: Check your inbox**
- Open email from `DEFAULT_FROM_EMAIL`
- Verify request details are displayed
- Click Accept or Decline link (valid for 7 days)

**Step 3: Verify decision email**
- Check email for acceptance/decline confirmation
- Verify status is correctly stated

### Option B: Manual Web UI Testing

**Step 1: Start Django server**
```bash
cd Django
python manage.py runserver
```

**Step 2: Create accounts**
- Go to `http://localhost:8000/accounts/register/`
- Create a regular user account with valid email
- Go to `http://localhost:8000/accounts/register/provider/`
- Create a provider account with different email
- Note the provider's company name

**Step 3: Create a service request**
- Log in as regular user
- Go to `http://localhost:8000/requests/create/`
- Fill in the form:
  - **Provider Name:** (Match provider's company name exactly)
  - **Description:** Test request description
  - **Date/Time:** (Optional) Select future date
  - **Price Range:** (Optional) Select from dropdown
  - **Urgent:** (Optional) Check if needed
  - **Photos:** (Optional) Upload images
- Click **Submit**

**Step 4: Check provider email**
- Open provider's email inbox
- Find email with subject "New Service Request"
- Verify all request details display correctly
- Click **Accept Request** or **Decline Request** button

**Step 5: Process provider decision**
- Browser opens confirmation page
- If accepting: Click "Accept Request"
- If declining: Select reason, enter optional message, click "Decline Request"

**Step 6: Check customer email**
- Customer receives notification email
- Subject: "Your Service Request Has Been Accepted" or similar
- Verify status is correctly shown

### Option C: Console Backend (Development Testing)

For testing without sending actual emails:

```bash
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
export DEFAULT_FROM_EMAIL=test@locapro.local
export SITE_URL=http://localhost:8000

cd Django
python manage.py runserver
```

When you create a request, emails will print to console instead of being sent.

---

## Verification Points

### Email Delivery Verification

**Indicators of Success:**
- ✓ Email appears in inbox within 30 seconds
- ✓ "From" address matches `DEFAULT_FROM_EMAIL`
- ✓ Request ID is in subject line
- ✓ Email displays in both HTML and text (check "View Plain Text")
- ✓ Accept/Decline links are clickable
- ✓ No error messages or bounces

**Common Issues:**
- Email in spam/junk folder → Check filters, mark as "not spam"
- Email doesn't arrive → Check credentials, wait longer, check logs
- Links don't work → Verify `SITE_URL` is correct, token isn't expired

### Decision Link Verification

**Accept Link Should:**
- ✓ Be clickable and open confirmation page
- ✓ Show all request details
- ✓ Have "Accept Request" button
- ✓ Update request status to "accepted" after click
- ✓ Mark token as used (can't be used twice)
- ✓ Be valid for 7 days from creation

**Decline Link Should:**
- ✓ Be clickable and open confirmation page
- ✓ Show reason dropdown
- ✓ Allow optional decline message
- ✓ Have "Decline Request" button
- ✓ Update request status to "declined" after click
- ✓ Send notification to customer

### Customer Notification Verification

**After Provider Accepts:**
- ✓ Customer receives email with subject containing "Accepted"
- ✓ Email contains provider details
- ✓ Email contains link to dashboard/request details
- ✓ Status shown as "accepted"

**After Provider Declines:**
- ✓ Customer receives email with subject containing "Update" or "Declined"
- ✓ Email shows decline reason
- ✓ Email shows provider's optional decline message
- ✓ Status shown as "declined"

---

## Database Verification

### Check Requests Were Created

```bash
cd Django
sqlite3 db.sqlite3 "SELECT id, provider_name, status, created_at FROM requests_servicerequest ORDER BY id DESC LIMIT 5;"
```

Expected: List of recent requests with status "pending", "accepted", or "declined"

### Check Decision Tokens

```bash
cd Django
sqlite3 db.sqlite3 "SELECT id, service_request_id, used, expires_at FROM requests_requestdecisiontoken ORDER BY id DESC LIMIT 5;"
```

Expected: Tokens with future `expires_at` dates

### Check Provider Profiles

```bash
cd Django
sqlite3 db.sqlite3 "SELECT user_id, company_name FROM accounts_providerprofile LIMIT 5;"
```

Expected: List of providers with company names

---

## Troubleshooting

### "SMTPAuthenticationError"

**Problem:** Email credentials rejected
```
SMTPAuthenticationError: (535, b'5.7.8 Username and password not accepted')
```

**Solutions:**
1. Verify `EMAIL_HOST_USER` is correct email address
2. For Gmail: Use **app password**, not Gmail password
3. For Outlook: Use app password if 2-factor enabled
4. Verify no trailing spaces in credentials
5. Test credentials at provider's login page

### "SMTPServerDisconnected" or Connection Timeout

**Problem:** Cannot connect to SMTP server
```
SMTPServerDisconnected: (-1, 'Unexpected EOF')
timeout: timed out
```

**Solutions:**
1. Verify correct `EMAIL_HOST` for provider:
   - Gmail: `smtp.gmail.com`
   - Outlook: `smtp-mail.outlook.com`
2. Verify correct `EMAIL_PORT`:
   - SSL: `465`
   - TLS: `587`
3. Verify `EMAIL_USE_SSL` and `EMAIL_USE_TLS` match port
4. Check firewall allows outbound on that port
5. Try different provider to isolate issue

### Email Not Appearing in Inbox

**Problem:** Email sent but not in inbox
```
python manage.py shell -c "from django.core.mail import outbox; print(len(outbox))"
# Output: 1 (email sent)
# But email not in inbox
```

**Solutions:**
1. Check **spam/junk folder**
2. Wait 1-2 minutes (Gmail can be slow)
3. Check email headers for bounce message
4. Verify recipient email is correct
5. Use console backend to verify email object created

### "Provider Email Not Found"

**Problem:** Email not sent to provider
```
Warning: Could not find email for provider 'Company Name'
```

**Solutions:**
1. Verify provider exists in database:
   ```bash
   cd Django
   sqlite3 db.sqlite3 "SELECT company_name FROM accounts_providerprofile;"
   ```
2. Verify `provider_name` in request matches company name exactly (case-sensitive)
3. Verify provider user has email address set
4. Use exact company name when creating request

### Links Expired Before Testing

**Problem:** Decision links show "expired" error
```
This decision link has expired or has already been used
```

**Solutions:**
1. Links valid for 7 days - verify token creation date
2. Check database:
   ```bash
   cd Django
   sqlite3 db.sqlite3 "SELECT expires_at FROM requests_requestdecisiontoken WHERE id=1;"
   ```
3. For testing, create request then test within 7 days
4. Can manually extend expiration in database if needed

### Templates Not Rendering

**Problem:** Template error when sending email
```
TemplateDoesNotExist: emails/request_to_provider_email.html
```

**Solutions:**
1. Verify template files exist:
   ```bash
   ls Django/requests/templates/emails/
   ```
2. Check template syntax in Django shell:
   ```bash
   cd Django
   python manage.py shell
   from django.template.loader import render_to_string
   render_to_string('emails/request_to_provider_email.html', {})
   ```
3. Verify INSTALLED_APPS includes 'requests'
4. Verify APP_DIRS=True in TEMPLATES settings

---

## Debugging Commands

### View Current Configuration

```bash
cd Django
python manage.py shell -c "
from django.conf import settings
print(f'Backend: {settings.EMAIL_BACKEND}')
print(f'Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}')
print(f'SSL: {settings.EMAIL_USE_SSL}, TLS: {settings.EMAIL_USE_TLS}')
print(f'From: {settings.DEFAULT_FROM_EMAIL}')
print(f'Site URL: {settings.SITE_URL}')
"
```

### Test Sending Email Directly

```bash
cd Django
python manage.py shell

from django.core.mail import EmailMultiAlternatives
from django.conf import settings

email = EmailMultiAlternatives(
    subject='Test Email',
    body='Plain text body',
    from_email=settings.DEFAULT_FROM_EMAIL,
    to=['recipient@example.com']
)
email.attach_alternative('<h1>HTML body</h1>', 'text/html')
result = email.send()
print(f'Sent: {result}')  # Should print 1 if successful
exit()
```

### View Sent Emails (Console Backend)

```bash
cd Django
python manage.py shell

from django.core.mail import outbox
for i, email in enumerate(outbox, 1):
    print(f'Email {i}:')
    print(f'  To: {email.to}')
    print(f'  Subject: {email.subject}')
    print(f'  Body preview: {email.body[:100]}...')
exit()
```

### Check Request Status in Database

```bash
cd Django
python manage.py shell

from requests.models import ServiceRequest
for req in ServiceRequest.objects.all():
    print(f'Request #{req.id}: {req.status} - {req.provider_name}')
    if req.decision_token:
        print(f'  Token valid: {req.decision_token.is_valid()}')
exit()
```

---

## Success Checklist

Before considering workflow complete:

**Setup Phase:**
- [ ] All EMAIL_* variables exported
- [ ] Variables verified with `env | grep EMAIL_`

**Connection Phase:**
- [ ] SMTP connection test succeeds
- [ ] No authentication errors

**Email Send Phase:**
- [ ] Test email sent successfully
- [ ] Test email received in inbox
- [ ] Email displays both HTML and text versions

**Workflow Phase:**
- [ ] Service request created via web or script
- [ ] Provider receives notification email
- [ ] Email contains correct request details
- [ ] Decision links are clickable

**Decision Phase:**
- [ ] Provider can click Accept link
- [ ] Confirmation page displays
- [ ] Accept/Decline action processes
- [ ] Status updates in database

**Notification Phase:**
- [ ] Customer receives acceptance/decline email
- [ ] Email contains correct status
- [ ] Customer can see decision details

---

## Next Steps

**After successful testing:**
1. Update `.env` file with working configuration (optional, for persistence)
2. Deploy code to staging/production
3. Reconfigure EMAIL_* variables in production environment
4. Run automated tests again in production
5. Monitor logs for email delivery issues

**For production:**
- Use verified domain for `DEFAULT_FROM_EMAIL`
- Set up SPF/DKIM records for better deliverability
- Monitor email delivery metrics
- Set up error alerts for failed emails
- Consider email service provider (SendGrid, Mailgun) for reliability

---

## Files Reference

| File | Purpose |
|------|---------|
| `EMAIL_WORKFLOW_TESTING_GUIDE.md` | Comprehensive reference documentation |
| `EMAIL_VERIFICATION_CHECKLIST.md` | Step-by-step verification checklist |
| `EMAIL_SETUP_QUICK_START.sh` | Interactive setup script (bash) |
| `EMAIL_TESTING_INSTRUCTIONS.md` | This file - complete testing guide |
| `Django/scripts/test_email_workflow.py` | Automated test script |
| `Django/requests/signals.py` | Email sending logic |
| `Django/requests/utils.py` | Token generation and URL building |

---

## Support Resources

- **Django Email Documentation:** https://docs.djangoproject.com/en/stable/topics/email/
- **Gmail SMTP Settings:** https://support.google.com/mail/answer/7126229
- **Outlook SMTP Settings:** https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-d088b986-291d-42b8-9564-9c414e2ad184
- **Python `secrets` Module:** https://docs.python.org/3/library/secrets.html

---

**Last Updated:** 2024-01-15
**Email Workflow Version:** 1.0
**Status:** Ready for Testing

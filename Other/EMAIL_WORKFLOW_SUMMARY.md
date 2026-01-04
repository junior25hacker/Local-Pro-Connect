# Email Request Workflow - Testing Summary & Quick Reference

## Overview

The LocaPro email workflow automates notifications across the service request lifecycle:

```
User Creates Request → Provider Gets Email → Provider Decides → Customer Gets Notification
```

---

## What Gets Tested

### 1. Provider Notification Email
- **Sent to:** Provider's email address
- **When:** User creates service request
- **Contains:** Request details, Accept/Decline links
- **Links Valid:** 7 days
- **Template:** `request_to_provider_email.html` + `.txt`

### 2. Customer Acceptance Notification
- **Sent to:** Customer's email address
- **When:** Provider clicks Accept link
- **Contains:** Confirmation, provider details
- **Template:** `request_accepted_email.html` + `.txt`

### 3. Customer Decline Notification
- **Sent to:** Customer's email address
- **When:** Provider clicks Decline link
- **Contains:** Decline reason, optional message
- **Template:** `request_declined_email.html` + `.txt`

---

## Quick Start (Copy-Paste Ready)

### 1. Export Gmail Configuration

```bash
export SMTP_PROVIDER=gmail \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp.gmail.com \
  EMAIL_PORT=465 \
  EMAIL_USE_TLS=false \
  EMAIL_USE_SSL=true \
  EMAIL_HOST_USER="your_gmail@gmail.com" \
  EMAIL_HOST_PASSWORD="your_16_char_app_password" \
  DEFAULT_FROM_EMAIL="your_gmail@gmail.com" \
  SERVER_EMAIL="your_gmail@gmail.com" \
  SITE_URL=http://localhost:8000
```

**Get Gmail App Password:**
1. Go to myaccount.google.com → Security
2. Enable 2-Step Verification (if needed)
3. Go to "App passwords"
4. Select Mail + Windows Computer
5. Copy 16-character password

### 2. Export Outlook Configuration

```bash
export SMTP_PROVIDER=outlook \
  EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend \
  EMAIL_HOST=smtp-mail.outlook.com \
  EMAIL_PORT=465 \
  EMAIL_USE_TLS=false \
  EMAIL_USE_SSL=true \
  EMAIL_HOST_USER="your_outlook@outlook.com" \
  EMAIL_HOST_PASSWORD="your_password" \
  DEFAULT_FROM_EMAIL="your_outlook@outlook.com" \
  SERVER_EMAIL="your_outlook@outlook.com" \
  SITE_URL=http://localhost:8000
```

### 3. Verify Configuration

```bash
# Check variables are exported
env | grep -E "^(SMTP_PROVIDER|EMAIL_|DEFAULT_FROM|SITE_URL)" | sort

# Expected output:
# DEFAULT_FROM_EMAIL=your_email@gmail.com
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_HOST_PASSWORD=your_app_password
# EMAIL_HOST_USER=your_email@gmail.com
# EMAIL_PORT=465
# EMAIL_USE_SSL=true
# EMAIL_USE_TLS=false
# SITE_URL=http://localhost:8000
```

### 4. Test Connection

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

### 5. Run Automated Test

```bash
cd Django
python manage.py shell < scripts/test_email_workflow.py
```

### 6. Check Email

Open inbox and verify:
- Email from `DEFAULT_FROM_EMAIL`
- Subject contains "New Service Request"
- Shows request details
- Has Accept/Decline links

---

## Test Methods

### Method 1: Automated Script (Fastest)
```bash
cd Django && python manage.py shell < scripts/test_email_workflow.py
```
**Pros:** Quick, creates all test data, full workflow
**Cons:** Less hands-on verification

### Method 2: Web UI (Most Realistic)
```bash
cd Django && python manage.py runserver
# 1. Visit http://localhost:8000/accounts/register/
# 2. Create user and provider accounts
# 3. Go to /requests/create/ and submit request
# 4. Check email inbox
```
**Pros:** Tests real user flow, visual verification
**Cons:** Slower, requires manual steps

### Method 3: Console Backend (Dev Testing)
```bash
export EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
cd Django && python manage.py runserver
```
**Pros:** No real emails sent, instant feedback
**Cons:** Doesn't test actual email delivery

---

## Email Configuration Variables

| Variable | For Gmail | For Outlook |
|----------|-----------|-------------|
| `SMTP_PROVIDER` | `gmail` | `outlook` |
| `EMAIL_HOST` | `smtp.gmail.com` | `smtp-mail.outlook.com` |
| `EMAIL_PORT` | `465` | `465` |
| `EMAIL_USE_SSL` | `true` | `true` |
| `EMAIL_USE_TLS` | `false` | `false` |
| `EMAIL_HOST_USER` | your@gmail.com | your@outlook.com |
| `EMAIL_HOST_PASSWORD` | app_password | password |

---

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| `SMTPAuthenticationError` | Wrong credentials | Use app password for Gmail, verify email/password |
| Connection timeout | Wrong port/host | Gmail: 465 with SSL; Outlook: 465 with SSL |
| Email not received | Spam folder | Check spam/junk, wait 1-2 min, check headers |
| "Provider not found" | Name mismatch | Use exact provider company name in request |
| Links expired | Too old | Links valid 7 days, create fresh request for testing |
| Template error | Missing file | Run `ls Django/requests/templates/emails/` |

---

## Verification Points

**Email Content:**
- ✓ Contains request ID in subject
- ✓ Shows provider name and customer name
- ✓ Lists service description
- ✓ Shows price range if set
- ✓ Marks urgent requests
- ✓ Shows request creation time

**Decision Links:**
- ✓ Accept link works and updates status
- ✓ Decline link works and collects reason
- ✓ Links expire after 7 days
- ✓ Links can't be reused after first use
- ✓ Invalid/expired links show error page

**Notifications:**
- ✓ Provider gets initial request notification
- ✓ Customer gets decision confirmation
- ✓ Customer notification includes decision details
- ✓ Decline notification shows reason

---

## Database Checks

### View Created Requests
```bash
cd Django
sqlite3 db.sqlite3 "SELECT id, provider_name, status, created_at FROM requests_servicerequest ORDER BY id DESC LIMIT 5;"
```

### View Decision Tokens
```bash
sqlite3 db.sqlite3 "SELECT id, service_request_id, used, expires_at FROM requests_requestdecisiontoken ORDER BY id DESC LIMIT 5;"
```

### View Providers
```bash
sqlite3 db.sqlite3 "SELECT user_id, company_name FROM accounts_providerprofile;"
```

---

## File Reference

| File | What It Does |
|------|--------------|
| `EMAIL_WORKFLOW_TESTING_GUIDE.md` | Detailed reference (all options, troubleshooting) |
| `EMAIL_VERIFICATION_CHECKLIST.md` | 12-phase verification checklist |
| `EMAIL_TESTING_INSTRUCTIONS.md` | Step-by-step testing procedures |
| `EMAIL_SETUP_QUICK_START.sh` | Interactive bash setup script |
| `EMAIL_WORKFLOW_SUMMARY.md` | This file - quick reference |
| `Django/scripts/test_email_workflow.py` | Automated testing script |

---

## Testing Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    EXPORT EMAIL CONFIGURATION                    │
│  (SMTP_PROVIDER, EMAIL_HOST, EMAIL_HOST_USER, PASSWORD, etc.)   │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│                  TEST EMAIL CONNECTION                           │
│  python manage.py shell -c "from django.core.mail import..."    │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│              CREATE SERVICE REQUEST (Via Script or Web UI)       │
│  - Create test customer user                                    │
│  - Create test provider user & profile                          │
│  - Submit service request form                                  │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│           EMAIL SIGNAL TRIGGERED (post_save)                     │
│  - Generate secure token (7-day expiration)                     │
│  - Render HTML & text templates                                 │
│  - Send to provider via SMTP                                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│          PROVIDER RECEIVES EMAIL & DECIDES                       │
│  - Opens Accept or Decline link from email                      │
│  - Confirmation page shown                                      │
│  - Submits acceptance or decline form                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│           STATUS UPDATED & TOKEN MARKED USED                     │
│  - Request status → "accepted" or "declined"                    │
│  - Token marked as used (can't reuse)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│      CUSTOMER NOTIFICATION EMAIL SENT (post_save signal)        │
│  - Email rendered with decision details                         │
│  - Sent to customer (request creator)                           │
│  - Contains status and any decline reason                       │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│          CUSTOMER RECEIVES & VERIFIES NOTIFICATION               │
│  - Check email for confirmation                                 │
│  - Verify status matches expected outcome                       │
│  - Workflow complete ✓                                          │
└─────────────────────────────────────────────────────────────────┘
```

---

## Success Indicators

You'll know the workflow is working when:

✓ **Email Received:** Provider's inbox shows request email within 30 seconds

✓ **Content Correct:** Email displays all request details accurately

✓ **Links Work:** Accept/Decline buttons are clickable

✓ **Decision Processes:** Clicking link updates request status in database

✓ **Token Used:** Same link clicked twice shows error (used only once)

✓ **Customer Notified:** Customer receives confirmation within 30 seconds

✓ **Status Confirmed:** Customer notification shows correct accept/decline status

✓ **No Errors:** Django logs show no email-related exceptions

---

## Environment Variable Export Methods

### Method 1: One-Time Export (Current Terminal Only)
```bash
export EMAIL_HOST_USER="your_email@gmail.com"
export EMAIL_HOST_PASSWORD="your_app_password"
# ... other variables
```
Valid only in current terminal session.

### Method 2: Add to .env File (Persistent)
```bash
# Edit .env file and add:
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password

# Load in terminal:
set -a
source .env
set +a
```
Persists across terminal restarts.

### Method 3: Use Setup Script (Interactive)
```bash
bash EMAIL_SETUP_QUICK_START.sh
```
Interactive prompts, can save to `.env`.

### Method 4: Django Shell Environment
```bash
cd Django
SMTP_PROVIDER=gmail EMAIL_HOST_USER="..." EMAIL_HOST_PASSWORD="..." \
python manage.py runserver
```
Inline export, valid for that command only.

---

## Troubleshooting Quick Links

**Connection Issues:** See `EMAIL_WORKFLOW_TESTING_GUIDE.md` → Troubleshooting → "SMTPAuthenticationError"

**Email Not Arriving:** See `EMAIL_WORKFLOW_TESTING_GUIDE.md` → Troubleshooting → "Emails Not Appearing in Inbox"

**Provider Not Found:** See `EMAIL_WORKFLOW_TESTING_GUIDE.md` → Troubleshooting → "Provider Email Not Found"

**Template Errors:** See `EMAIL_WORKFLOW_TESTING_GUIDE.md` → Troubleshooting → "Templates Not Rendering Properly"

---

## Next Steps

1. **Choose email provider** (Gmail recommended for testing)
2. **Export EMAIL_* variables** using quick start commands above
3. **Test connection** with verification command
4. **Run automated test** with test script
5. **Check email inbox** for provider notification
6. **Click decision link** to test acceptance/decline
7. **Verify database** shows updated status
8. **Check customer email** for confirmation
9. **Repeat with decline** to test full workflow
10. **Review EMAIL_VERIFICATION_CHECKLIST.md** for complete validation

---

## Production Considerations

Before deploying to production:

- [ ] Use verified domain for `DEFAULT_FROM_EMAIL` (not Gmail/Outlook)
- [ ] Set up SPF, DKIM records for domain
- [ ] Use dedicated email service (SendGrid, Mailgun) if possible
- [ ] Monitor email delivery rates
- [ ] Set up error alerts for failed sends
- [ ] Test with real customer emails in staging
- [ ] Have backup email provider configured
- [ ] Review email security best practices
- [ ] Set up bounce/complaint handling

---

## Support & Resources

**Documentation:**
- `EMAIL_WORKFLOW_TESTING_GUIDE.md` - Complete reference
- `EMAIL_VERIFICATION_CHECKLIST.md` - Phase-by-phase checklist
- `EMAIL_TESTING_INSTRUCTIONS.md` - Detailed procedures

**Test Scripts:**
- `Django/scripts/test_email_workflow.py` - Automated testing

**Email Providers:**
- Gmail: https://support.google.com/mail/answer/7126229
- Outlook: https://support.microsoft.com/en-us/office/pop-imap-and-smtp-settings-d088b986-291d-42b8-9564-9c414e2ad184

**Django:**
- Email Documentation: https://docs.djangoproject.com/en/stable/topics/email/
- Signals: https://docs.djangoproject.com/en/stable/topics/signals/

---

## Version Information

- **Email Workflow Version:** 1.0
- **Django Version:** 5.2+
- **Email Backend:** SMTP (EmailMultiAlternatives)
- **Security:** Secure tokens with HMAC-SHA256
- **Token Expiration:** 7 days
- **Templates:** HTML + Plain Text

---

**Last Updated:** 2024-01-15
**Status:** Ready for Testing
**Estimated Testing Time:** 10-15 minutes (end-to-end)

# SMTP Configuration Guide for LocaPro

This guide covers configuring SMTP email for local development and production deployment.

## Quick Start

### Development (Console Backend)

For local development, emails are printed to console. No configuration needed!

```python
# Django/locapro_project/settings.py already configured for this
DEBUG = True
# If EMAIL_HOST_USER is not set, uses console backend automatically
```

### Production (Gmail)

1. Create Gmail app password:
   - Go to https://accounts.google.com/SignUpWithoutGmail
   - Enable 2-Factor Authentication
   - Generate App Password at https://myaccount.google.com/apppasswords

2. Set environment variables:
   ```bash
   export SMTP_PROVIDER=gmail
   export EMAIL_HOST_USER=your-email@gmail.com
   export EMAIL_HOST_PASSWORD=your-app-password
   export DEFAULT_FROM_EMAIL=your-email@gmail.com
   export SITE_URL=https://your-domain.com
   ```

3. Or add to `.env` file:
   ```
   SMTP_PROVIDER=gmail
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   SITE_URL=https://your-domain.com
   ```

## Configuration Methods

### Method 1: Environment Variables (Recommended)

Create `.env` file in project root:

```bash
# Email Configuration
SMTP_PROVIDER=gmail
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
EMAIL_TIMEOUT=10
SITE_URL=http://localhost:8000
```

Load automatically via Django settings (already configured).

### Method 2: Direct Settings File

Edit `Django/locapro_project/settings.py`:

```python
# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'
SERVER_EMAIL = 'your-email@gmail.com'
SITE_URL = 'http://localhost:8000'
```

### Method 3: Runtime Configuration

```python
from django.conf import settings

# Override settings at runtime
settings.EMAIL_HOST = 'your-smtp-server.com'
settings.EMAIL_PORT = 587
settings.EMAIL_HOST_USER = 'your-username'
settings.EMAIL_HOST_PASSWORD = 'your-password'
```

## Provider-Specific Configurations

### Gmail

**Settings:**
```
SMTP_PROVIDER = gmail
EMAIL_HOST = smtp.gmail.com
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
```

**Setup:**
1. Enable 2FA on your Google account
2. Generate app password: https://myaccount.google.com/apppasswords
3. Use app password (not regular password)
4. Update EMAIL_HOST_USER with your Gmail address

**Alternative (Less Secure - Not Recommended):**
- Enable "Less secure app access": https://myaccount.google.com/lesssecureapps
- Use your regular Gmail password

### Outlook / Office 365

**Settings:**
```
SMTP_PROVIDER = outlook
EMAIL_HOST = smtp-mail.outlook.com
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
```

**Setup:**
1. Use your Outlook/Office365 email address
2. Use your regular password or app password
3. Enable POP/IMAP in Outlook settings if needed

### SendGrid (Production Recommended)

**Settings:**
```
EMAIL_HOST = smtp.sendgrid.net
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = apikey
EMAIL_HOST_PASSWORD = SG.your-sendgrid-api-key
```

**Setup:**
1. Create SendGrid account: https://sendgrid.com
2. Create API key
3. Set EMAIL_HOST_USER to 'apikey'
4. Set EMAIL_HOST_PASSWORD to your API key with 'SG.' prefix

**Benefits:**
- Better deliverability
- Email analytics
- Bounce handling
- Unsubscribe management
- High volume support

### AWS SES (Production Recommended)

**Settings:**
```
EMAIL_BACKEND = 'django_ses.SESBackend'
AWS_SES_REGION_NAME = 'us-east-1'
AWS_SES_REGION_ENDPOINT = 'email.us-east-1.amazonaws.com'
AWS_ACCESS_KEY_ID = 'your-aws-access-key'
AWS_SECRET_ACCESS_KEY = 'your-aws-secret-key'
```

**Setup:**
1. Create AWS account and configure SES
2. Verify sender email address
3. Install django-ses: `pip install django-ses`
4. Configure AWS credentials

### Custom SMTP Server

**Settings (TLS):**
```
EMAIL_HOST = your-smtp-server.com
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = your-username
EMAIL_HOST_PASSWORD = your-password
```

**Settings (SSL):**
```
EMAIL_HOST = your-smtp-server.com
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = your-username
EMAIL_HOST_PASSWORD = your-password
```

## Testing Your Configuration

### Test 1: Check Settings

```python
python manage.py shell

from django.conf import settings
print(f"Backend: {settings.EMAIL_BACKEND}")
print(f"Host: {settings.EMAIL_HOST}:{settings.EMAIL_PORT}")
print(f"User: {settings.EMAIL_HOST_USER}")
print(f"Use SSL: {settings.EMAIL_USE_SSL}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
print(f"From Email: {settings.DEFAULT_FROM_EMAIL}")
```

### Test 2: Test Connection

```python
python manage.py shell

from requests.email_service import test_email_configuration
result = test_email_configuration()
print(f"Success: {result['success']}")
print(f"Message: {result['message']}")
if not result['success']:
    print(f"Error: {result['config'].get('error')}")
```

### Test 3: Send Test Email

```python
python manage.py shell

from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from LocaPro',
    'from@example.com',
    ['to@example.com'],
)
print("Email sent!")
```

### Test 4: Run Full Workflow Test

```bash
cd Django
python manage.py shell < ../scripts/test_email_workflow_comprehensive.py
```

## Troubleshooting

### Error: "SMTPAuthenticationError"

**Problem:** Authentication failed

**Solutions:**
1. Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
2. For Gmail: Use app password, not regular password
3. For Gmail: Enable less secure apps (not recommended)
4. Check username format (should include @domain.com)

### Error: "SMTPServerDisconnected"

**Problem:** Connection dropped

**Solutions:**
1. Check EMAIL_PORT matches EMAIL_USE_SSL/TLS
2. Verify firewall allows outbound connections on port
3. Check email provider's SMTP settings
4. Increase EMAIL_TIMEOUT in settings

### Error: "ConnectionRefusedError"

**Problem:** Cannot connect to server

**Solutions:**
1. Verify EMAIL_HOST is correct
2. Check EMAIL_PORT is correct
3. Verify firewall allows outbound connections
4. Check if SMTP server is running
5. Use console backend for testing

### Error: "SMTPNotSupportedError"

**Problem:** SSL/TLS not available

**Solutions:**
1. Check SSL/TLS settings match server requirements
2. For port 465, use EMAIL_USE_SSL = True
3. For port 587, use EMAIL_USE_TLS = True
4. Don't use both SSL and TLS

### Emails Going to Spam

**Solutions:**
1. Configure SPF record for your domain:
   ```
   v=spf1 include:sendgrid.net ~all
   ```

2. Configure DKIM for your domain
   - SendGrid: https://sendgrid.com/docs/ui/account-and-settings/dkim-records/
   - AWS SES: https://docs.aws.amazon.com/ses/latest/dg/send-email-authentication.html

3. Configure DMARC for your domain

4. Use professional email provider (SendGrid, AWS SES)

5. Avoid spam trigger words

### Email Template Issues

**Problem:** Email not rendering correctly

**Solutions:**
1. Check template syntax in `requests/templates/emails/`
2. Verify all template variables are passed in context
3. Test with console backend to see raw email
4. Use email preview services

## Environment File Example (.env)

```bash
# ============================================================================
# Email Configuration
# ============================================================================

# Email Backend
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend

# SMTP Provider (gmail, outlook, or leave empty for custom)
SMTP_PROVIDER=gmail

# Gmail Settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=true
EMAIL_USE_TLS=false
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Alternative: Outlook Settings (comment out Gmail above if using this)
# EMAIL_HOST=smtp-mail.outlook.com
# EMAIL_PORT=465
# EMAIL_USE_SSL=true
# EMAIL_USE_TLS=false
# EMAIL_HOST_USER=your-email@outlook.com
# EMAIL_HOST_PASSWORD=your-password

# Default Email Settings
DEFAULT_FROM_EMAIL=your-email@gmail.com
SERVER_EMAIL=your-email@gmail.com
EMAIL_TIMEOUT=10

# Site Configuration
SITE_URL=http://localhost:8000

# Disable this in production
DEBUG=True
```

## Production Checklist

- [ ] Configured real SMTP provider (SendGrid, AWS SES, etc.)
- [ ] Used app-specific passwords for Gmail/Outlook
- [ ] Set DEBUG = False
- [ ] Configured SITE_URL with production domain
- [ ] Set up SPF/DKIM/DMARC records
- [ ] Tested email sending in production
- [ ] Verified email templates render correctly
- [ ] Monitored email delivery and bounce rates
- [ ] Set up email analytics dashboard
- [ ] Configured error logging and alerts
- [ ] Tested email in spam folder scenario
- [ ] Added unsubscribe links if applicable

## Security Best Practices

1. **Never commit credentials** to git
   - Use `.env` file (add to `.gitignore`)
   - Use environment variables in deployment

2. **Use app-specific passwords**
   - Gmail: Generate app password
   - Outlook: Use app password when available
   - Never use your main password

3. **Enable 2FA** on email accounts used for sending

4. **Limit permissions** for email accounts
   - Use dedicated email accounts
   - Don't use personal email in production

5. **Rotate credentials regularly**
   - Change passwords periodically
   - Regenerate API keys

6. **Monitor email logs** for suspicious activity

7. **Use HTTPS** for sites with email links

8. **Implement rate limiting** to prevent spam

## References

- Django Email Documentation: https://docs.djangoproject.com/en/stable/topics/email/
- Gmail App Passwords: https://support.google.com/accounts/answer/185833
- Outlook Settings: https://support.microsoft.com/en-us
- SendGrid SMTP: https://sendgrid.com/docs/for-developers/sending-email/smtp-service/
- AWS SES: https://docs.aws.amazon.com/ses/
- SPF/DKIM/DMARC: https://mxtoolbox.com/

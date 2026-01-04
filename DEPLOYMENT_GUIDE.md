# Service Request Workflow - Deployment Guide

## 🚀 Deployment Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Database backed up
- [ ] Code committed to version control
- [ ] Environment variables documented
- [ ] Email credentials ready

### Deployment Steps
- [ ] Pull latest code
- [ ] Install dependencies
- [ ] Apply migrations
- [ ] Collect static files
- [ ] Verify email configuration
- [ ] Test workflow end-to-end
- [ ] Monitor logs for errors

### Post-Deployment
- [ ] Verify all services running
- [ ] Test provider email delivery
- [ ] Test decision links
- [ ] Check admin interface
- [ ] Monitor error logs

---

## 📋 Pre-Deployment Checklist

### 1. Code Review
```bash
# Verify all files are in place
cd Django
find requests -type f -name "*.py" -o -name "*.html" -o -name "*.txt"

# Check for syntax errors
python manage.py check
```

### 2. Database Backup
```bash
# Backup existing database
cp db.sqlite3 db.sqlite3.backup

# Or for PostgreSQL/MySQL
pg_dump yourdb > backup.sql
```

### 3. Environment Variables
Create `.env` file with:
```bash
# Email Settings (Production)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Site Configuration
SITE_URL=https://yourdomain.com

# Django Settings
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
SECRET_KEY=your-secret-key
```

### 4. Update Settings (Production)
Edit `Django/locapro_project/settings.py`:
```python
# Change email backend
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Load environment variables
from decouple import config
SITE_URL = config('SITE_URL', default='http://localhost:8000')
```

---

## 🔧 Deployment Steps

### Step 1: Pull Code
```bash
cd /path/to/project
git pull origin main
```

### Step 2: Install Dependencies
```bash
cd Django
pip install -r requirements.txt
```

### Step 3: Apply Migrations
```bash
python manage.py migrate requests
```

### Step 4: Collect Static Files
```bash
python manage.py collectstatic --noinput
```

### Step 5: Test Configuration
```bash
python manage.py check
```

### Step 6: Create Superuser (if needed)
```bash
python manage.py createsuperuser
```

### Step 7: Test Email Configuration
```bash
python manage.py shell
```

```python
from django.core.mail import send_mail

send_mail(
    'Test Email from LocaPro',
    'This is a test email to verify configuration.',
    'noreply@locapro.com',
    ['your-email@gmail.com'],
    fail_silently=False,
)
```

### Step 8: Start Services
```bash
# For development
python manage.py runserver

# For production (using gunicorn)
gunicorn locapro_project.wsgi:application --bind 0.0.0.0:8000

# Or use your deployment platform (Heroku, AWS, etc.)
```

---

## 📊 Testing After Deployment

### 1. Test Admin Interface
```
Visit: https://yourdomain.com/admin/
Login with superuser credentials
Navigate to: Requests > Service Requests
```

### 2. Test Request Creation
```
Visit: https://yourdomain.com/requests/create/
Fill form with:
- provider_name: Test Provider
- description: Test request
- Submit
Check email console/logs for provider email
```

### 3. Test Decision Flow
```
1. Copy decision link from provider email
2. Visit: https://yourdomain.com/requests/decision/<id>/<action>/<token>/
3. Should see confirmation page
4. Submit decision
5. Check email console for customer notification
```

### 4. Test Error Handling
```
1. Visit decision link with invalid token
2. Should see: "Invalid or expired token"
3. Visit decision link twice
4. Should see: "Link has already been used"
5. Try expired token (modify date in database)
6. Should show expiration message
```

---

## 🔍 Monitoring

### Log Files to Monitor
```bash
# Check application logs
tail -f /var/log/locapro.log

# Check email logs
grep -i email /var/log/locapro.log

# Check Django errors
python manage.py shell
from django.core import logging
logging.basicConfig(level=logging.DEBUG)
```

### Key Metrics to Track
- Email delivery success rate
- Decision token usage
- Request acceptance rate
- Request decline rate
- Error occurrence

### Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Emails not sending | Email backend not configured | Check EMAIL_BACKEND in settings |
| Invalid token error | Token expired or used | Verify token expiration logic |
| Provider email not found | Provider lookup failed | Check ProviderProfile.company_name |
| 404 on decision link | Invalid request ID | Verify request exists in database |
| CSRF token error | POST without CSRF | Ensure form includes {% csrf_token %} |

---

## 🆘 Troubleshooting

### Email Not Sending

1. **Check Email Backend**
```python
# In Django shell
from django.conf import settings
print(settings.EMAIL_BACKEND)
# Should show SMTP backend in production
```

2. **Verify Email Credentials**
```python
from django.core.mail import get_connection
connection = get_connection()
connection.open()
# Should connect without error
```

3. **Check Email Logs**
```bash
tail -f /var/log/mail.log
# Look for authentication errors
```

### Token Issues

1. **Check Token in Database**
```python
from requests.models import RequestDecisionToken
token = RequestDecisionToken.objects.first()
print(f"Valid: {token.is_valid()}")
print(f"Expired: {token.is_expired()}")
print(f"Used: {token.used}")
```

2. **Manually Verify Token**
```python
from requests.utils import verify_signed_token
result = verify_signed_token('your-token')
print(f"Verification result: {result}")
```

### Provider Email Lookup

1. **Check ProviderProfile**
```python
from accounts.models import ProviderProfile
providers = ProviderProfile.objects.all()
for p in providers:
    print(f"{p.company_name}: {p.user.email}")
```

2. **Test Email Lookup**
```python
from requests.utils import get_provider_email_by_name
email = get_provider_email_by_name('John Plumbing')
print(f"Found email: {email}")
```

---

## 📈 Performance Optimization

### Database Optimization
```python
# Add indexes to frequently queried fields
class ServiceRequest(models.Model):
    # Already optimized with Meta.ordering
    class Meta:
        indexes = [
            models.Index(fields=['status', '-created_at']),
            models.Index(fields=['user', 'status']),
        ]
```

### Email Optimization
```python
# For bulk email sending, consider:
# 1. Celery for async tasks
# 2. Email queue system
# 3. Batch email processing

# For now, emails are sent synchronously
# Consider async for high volume
```

### Query Optimization
```python
# Use select_related for foreign keys
requests = ServiceRequest.objects.select_related('user', 'provider')

# Use prefetch_related for reverse relationships
requests = ServiceRequest.objects.prefetch_related('photos')

# Use only() to limit fields
requests = ServiceRequest.objects.only('id', 'status', 'created_at')
```

---

## 🔐 Security Hardening

### Email Security
```python
# Ensure TLS is enabled
EMAIL_USE_TLS = True
EMAIL_PORT = 587

# Use separate credentials for email
# Don't use admin credentials for email
```

### Database Security
```bash
# Regular backups
pg_dump mydb | gzip > backup-$(date +%Y%m%d).sql.gz

# Restrict access
chmod 600 db.sqlite3
```

### Application Security
```python
# Keep SECRET_KEY secret
SECRET_KEY = os.environ.get('SECRET_KEY')

# Enable security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_SECURITY_POLICY = {...}

# HTTPS only in production
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
```

---

## 📞 Support & Monitoring

### Alert Conditions
Set up alerts for:
- [ ] Email delivery failures
- [ ] HTTP 5xx errors
- [ ] Database connection errors
- [ ] Disk space warnings
- [ ] High memory usage

### Monitoring Tools
- Django Debug Toolbar (development)
- Sentry (error tracking)
- New Relic / DataDog (performance)
- AWS CloudWatch / Google Cloud Logging

### Daily Checks
```bash
# Check for errors
grep ERROR /var/log/locapro.log

# Check database size
du -h db.sqlite3

# Check email queue
python manage.py shell
from requests.models import ServiceRequest
print(ServiceRequest.objects.filter(status='pending').count())
```

---

## 🚀 Rollback Plan

If issues occur after deployment:

### Quick Rollback
```bash
# Revert code
git revert HEAD

# Restore database backup
cp db.sqlite3.backup db.sqlite3

# Restart services
systemctl restart gunicorn
```

### Database Rollback
```bash
# If migrations cause issues
python manage.py migrate requests 0001_initial

# Reapply migration after fix
python manage.py migrate requests 0002_service_request_workflow
```

---

## 📊 Success Metrics

After deployment, verify:
- [ ] All requests show in admin
- [ ] Emails send on request creation
- [ ] Decision links work
- [ ] Acceptance emails send
- [ ] Decline emails send
- [ ] No errors in logs
- [ ] Response times acceptable
- [ ] Admin interface loads quickly

---

## 🎯 Final Verification

Run this verification script:
```python
# Django shell
from requests.models import ServiceRequest, RequestDecisionToken
from accounts.models import ProviderProfile

# Check models exist
print("✓ Models imported successfully")

# Check database
print(f"✓ Service Requests: {ServiceRequest.objects.count()}")
print(f"✓ Decision Tokens: {RequestDecisionToken.objects.count()}")
print(f"✓ Providers: {ProviderProfile.objects.count()}")

# Check settings
from django.conf import settings
print(f"✓ Email Backend: {settings.EMAIL_BACKEND}")
print(f"✓ From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"✓ Site URL: {settings.SITE_URL}")

print("\n✅ Deployment verification complete!")
```

---

## 📝 Post-Deployment Documentation

Update these files after deployment:
- [ ] DEPLOYMENT_NOTES.md - Specific deployment details
- [ ] CONFIGURATION.md - Current configuration
- [ ] MONITORING.md - Monitoring setup

---

**Deployment Status: Ready**

Follow these steps for a successful deployment. Monitor logs closely during first 24 hours.

For questions, refer to:
- QUICK_REFERENCE.md
- WORKFLOW_IMPLEMENTATION.md
- VERIFICATION_CHECKLIST.md

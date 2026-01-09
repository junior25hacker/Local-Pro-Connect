# Rejection Modal Integration - Deployment Guide

## Pre-Deployment Verification

### 1. Code Review Checklist

- [ ] All files have been reviewed for syntax errors
- [ ] No hardcoded URLs or settings
- [ ] All imports are correct
- [ ] No debug code left in place
- [ ] Comments are clear and helpful

### 2. Database Backup

```bash
# PostgreSQL backup
pg_dump -h localhost -U username database_name > backup_$(date +%Y%m%d_%H%M%S).sql

# SQLite backup (development)
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d_%H%M%S)
```

### 3. Static Files

```bash
# Collect static files
python manage.py collectstatic --no-input --clear

# Verify CSS and JS files exist
ls Django/static/css/rejection_modal.css
ls Django/static/js/rejection_modal.js
```

## Deployment Steps

### Step 1: Pull Latest Code

```bash
git pull origin main
# or your deployment branch
```

### Step 2: Install Dependencies (if needed)

```bash
pip install -r requirements.txt
```

### Step 3: Run Migrations

```bash
python manage.py migrate requests

# Verify migration was applied
python manage.py showmigrations requests
```

**Expected output:**
```
requests
 [X] 0001_initial
 [X] 0002_service_request_workflow
 [X] 0003_update_decline_reason_choices
```

### Step 4: Collect Static Files

```bash
python manage.py collectstatic --no-input

# If using S3/CloudFront
python manage.py collectstatic --no-input --s3sync
```

### Step 5: Verify Configuration

Check that the following settings are configured in `settings.py`:

```python
# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-email-host'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@example.com'
EMAIL_HOST_PASSWORD = 'your-password'

# Site URL for email links
SITE_URL = 'https://yourdomain.com'

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/path/to/static/files'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/path/to/media/files'
```

### Step 6: Restart Application Server

#### For Gunicorn:
```bash
# Graceful restart (SIGHUP)
kill -HUP $(pgrep -f gunicorn)

# Or full restart
sudo systemctl restart gunicorn

# Check status
sudo systemctl status gunicorn
```

#### For uWSGI:
```bash
# Touch the reload file
touch /var/www/your-app/reload-app.py

# Or restart service
sudo systemctl restart uwsgi
```

#### For Development (Django runserver):
```bash
# Simply stop and restart
python manage.py runserver 0.0.0.0:8000
```

### Step 7: Verify Deployment

```bash
# Check application is running
curl -I https://yourdomain.com/

# Check static files are served
curl -I https://yourdomain.com/static/css/rejection_modal.css

# Check that migrations are applied
python manage.py check
```

### Step 8: Monitor Application

```bash
# Check application logs
tail -f /var/log/gunicorn/error.log
tail -f /var/log/gunicorn/access.log

# Check Django logs (if configured)
tail -f logs/django.log

# Monitor system resources
htop
```

## Testing After Deployment

### Smoke Test (5 minutes)

1. **Navigate to Decline Page:**
   ```
   https://yourdomain.com/requests/decision/1/decline/your-token/
   ```
   - ✓ Page loads without errors
   - ✓ Request details display correctly

2. **Open Modal:**
   - ✓ Click "Decline Request" button
   - ✓ Modal appears with animation
   - ✓ All 4 reason options visible

3. **Select Reason:**
   - ✓ Click "Price" option
   - ✓ Card highlights in green
   - ✓ Description field appears

4. **Submit Form:**
   - ✓ Add description text
   - ✓ Click "Submit Rejection"
   - ✓ Success notification appears
   - ✓ Page redirects to success page

5. **Check Email:**
   - ✓ Decline notification received
   - ✓ Email includes "Price" reason
   - ✓ Email includes description text
   - ✓ All formatting is correct

### Extended Test (15 minutes)

1. **Test All Reasons:**
   - Try declining with Distance, Price, Time, Other
   - Verify each reason saves correctly

2. **Test Edge Cases:**
   - Decline without description
   - Decline with 500 character description
   - Decline with special characters

3. **Test Responsive Design:**
   - Test on desktop, tablet, mobile
   - Verify modal is usable on all sizes

4. **Test Browser Compatibility:**
   - Chrome/Edge
   - Firefox
   - Safari
   - Mobile Safari

5. **Test Security:**
   - Verify token validation
   - Verify CSRF protection
   - Attempt to reuse token (should fail)

## Rollback Procedures

### If Issues Occur

#### Option 1: Quick Rollback (Last Deployment)

```bash
# Revert code to previous deployment
git revert HEAD
git push origin main

# Restart application
sudo systemctl restart gunicorn

# Verify old version is running
curl -I https://yourdomain.com/
```

#### Option 2: Database Rollback

```bash
# Reverse the migration
python manage.py migrate requests 0002_service_request_workflow

# Restart application
sudo systemctl restart gunicorn
```

#### Option 3: Full Rollback

```bash
# 1. Restore database from backup
psql -h localhost -U username database_name < backup_20240115_120000.sql

# 2. Revert code
git checkout v1.2.3  # or previous tag

# 3. Collect static files
python manage.py collectstatic --no-input

# 4. Restart application
sudo systemctl restart gunicorn
```

## Performance Monitoring

### Key Metrics to Monitor

1. **Response Time**
   - Decline page load time: < 2 seconds
   - Modal rendering: < 500ms
   - Form submission: < 5 seconds

2. **Error Rates**
   - 4xx errors: < 1%
   - 5xx errors: < 0.1%
   - Email failures: < 0.1%

3. **Resource Usage**
   - Memory: < 80% of available
   - CPU: < 70% average
   - Database connections: < 80% of max

### Monitoring Tools

```bash
# Check application errors
grep -i "error" /var/log/gunicorn/error.log | tail -20

# Check slow requests
grep "GET /requests/decision" /var/log/gunicorn/access.log | awk '{print $4}' | sort -rn | head -10

# Database query performance
# Enable Django query logging and check slow queries

# Monitor email sending
grep -i "email" /var/log/django.log | grep -i "error"
```

## Post-Deployment Communication

### Notify Teams

- [ ] Backend team: Deployment complete
- [ ] Frontend team: Modal integration live
- [ ] QA team: Begin regression testing
- [ ] Support team: Update documentation
- [ ] Product team: Feature is live

### Documentation Updates

- [ ] Update support docs with new workflow
- [ ] Add FAQ for common issues
- [ ] Document troubleshooting steps
- [ ] Update API documentation if needed

## Monitoring & Maintenance

### Weekly Checks

```bash
# Check database size
SELECT pg_size_pretty(pg_database_size('database_name'));

# Check for failed migrations
python manage.py showmigrations requests

# Monitor email delivery
# Check if any decline emails are bouncing

# Review error logs for patterns
grep -i "rejection" /var/log/django.log | wc -l
```

### Monthly Checks

```bash
# Database maintenance
VACUUM ANALYZE;  -- PostgreSQL

# Check for orphaned tokens
SELECT * FROM requests_requestdecisiontoken WHERE used = FALSE AND expires_at < NOW();

# Review decline reasons statistics
SELECT decline_reason, COUNT(*) FROM requests_servicerequest 
WHERE status = 'declined' 
GROUP BY decline_reason;

# Backup and cleanup old data
# Archive old decline records if needed
```

## Troubleshooting Common Issues

### Issue 1: Modal CSS Not Loading

**Symptoms:** Modal appears but without styling

**Solution:**
```bash
# Verify CSS file exists
ls -la Django/static/css/rejection_modal.css

# Recollect static files
python manage.py collectstatic --clear --no-input

# Check browser developer tools for CSS errors
# In Chrome DevTools: Check Network tab for rejection_modal.css
```

### Issue 2: Modal JavaScript Not Working

**Symptoms:** Modal appears but buttons don't work

**Solution:**
```bash
# Check browser console for JS errors
# Verify JavaScript file is loaded
# In Chrome DevTools: Check Network tab for rejection_modal.js

# Recollect static files
python manage.py collectstatic --clear --no-input

# Check for JavaScript syntax errors
node -c Django/static/js/rejection_modal.js
```

### Issue 3: Emails Not Sending

**Symptoms:** Decline email not received

**Solution:**
```bash
# Verify email configuration
python manage.py shell
>>> from django.conf import settings
>>> print(settings.EMAIL_HOST)
>>> print(settings.EMAIL_PORT)

# Test email sending
from django.core.mail import send_mail
send_mail('Test', 'Test message', 'from@example.com', ['to@example.com'])

# Check email logs
grep -i "email\|mail" /var/log/django.log | tail -20

# Verify recipient email is valid
# Check spam folder in recipient's email
```

### Issue 4: Token Validation Errors

**Symptoms:** "Invalid or expired token" error

**Solution:**
```bash
# Verify token exists in database
python manage.py shell
>>> from requests.models import RequestDecisionToken
>>> RequestDecisionToken.objects.filter(token='your-token').first()

# Check token expiry
>>> token = RequestDecisionToken.objects.get(token='...')
>>> print(token.expires_at)
>>> print(token.is_valid())

# Check if token was already used
>>> print(token.used)
>>> print(token.used_at)
```

## Support Contact

For deployment issues or questions:
- DevOps Team: devops@company.com
- Backend Lead: backend@company.com
- On-Call Engineer: check on-call schedule

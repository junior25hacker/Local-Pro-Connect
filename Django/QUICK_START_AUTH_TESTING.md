# Quick Start: Testing Authentication, Session Management & RBAC

This guide walks you through testing the authentication, session management, and RBAC features.

## Prerequisites

- Django server running: `python manage.py runserver`
- Test database with sample data

## Quick Test (5 minutes)

### 1. Test Persistent Login

```bash
# Terminal 1: Start Django server
cd Django
python manage.py runserver
```

**In Browser:**

1. Open http://localhost:8000/accounts/login/
2. Login with test credentials (e.g., username: `testuser`, password: `password123`)
3. Navigate to home page (should show logged in user)
4. **Refresh the page (F5)** - should STAY logged in ✓
5. **Close the browser completely**
6. **Open browser again** and navigate to http://localhost:8000/
7. **Should STILL be logged in** ✓

### 2. Test Provider Profile RBAC (Read-Only for Users)

**As Regular User:**

1. Login as regular user (non-provider)
2. Navigate to "Professionals List" or find a provider profile
3. Click on provider profile to view details
4. **Verify: No "Edit" button is visible** ✓
5. Try to manually access: http://localhost:8000/accounts/profile/provider/1/edit/
6. **Verify: 403 Forbidden error shown** ✓

**As Provider:**

1. Logout first
2. Login as provider (user with provider profile)
3. Navigate to your profile or search for it
4. **Verify: "Edit" button IS visible** ✓
5. Click edit and change a field (e.g., bio)
6. Save the changes
7. **Verify: Profile updated successfully** ✓
8. **Verify: Notification in console if email configured** ✓

### 3. Test Provider Dashboard Access Control

**As Regular User:**

1. Login as regular user
2. Try to access: http://localhost:8000/accounts/dashboard/provider/
3. **Verify: 403 Forbidden or permission denied error** ✓
4. Logout

**As Provider:**

1. Login as provider
2. Navigate to: http://localhost:8000/accounts/dashboard/provider/
3. **Verify: Dashboard loads successfully** ✓
4. **Verify: List of provider's requests displayed** ✓

### 4. Test Email Configuration

```bash
cd Django

# Test email configuration
python manage.py test_email
```

**Expected Output:**

```
✓ Test email sent successfully! Email configuration is working.
```

**Check Email:**

- If SMTP configured: Check your email inbox
- If console backend: Check Django console output

---

## Complete Test Scenario

### Setup

```bash
# Create test users
cd Django
python manage.py shell

# In Python shell:
from django.contrib.auth.models import User
from accounts.models import ProviderProfile

# Create test regular user
user1 = User.objects.create_user(username='regular_user', email='user@test.com', password='pass123')

# Create test provider
provider_user = User.objects.create_user(username='test_provider', email='provider@test.com', password='pass123')
provider = ProviderProfile.objects.create(
    user=provider_user,
    company_name='Test Plumbing Co',
    service_type='plumbing',
    city='New York',
    state='NY'
)

print(f"Created user: {user1.username}")
print(f"Created provider: {provider.company_name}")
```

### Test Workflow

#### Step 1: Test Session Persistence
- [ ] Login as `regular_user` with password `pass123`
- [ ] Refresh page - stays logged in
- [ ] Close browser - reopen and verify still logged in
- [ ] Logout

#### Step 2: Test Provider Profile Read-Only Access
- [ ] Login as `regular_user`
- [ ] Visit provider profile (ID: see output from shell script)
- [ ] Verify no edit button
- [ ] Try to access edit URL: 403 error
- [ ] Logout

#### Step 3: Test Provider Profile Edit Access
- [ ] Login as `test_provider` with password `pass123`
- [ ] Visit own provider profile
- [ ] Verify edit button IS visible
- [ ] Edit profile (change company name or bio)
- [ ] Save changes
- [ ] Verify success message
- [ ] Check console for profile update email

#### Step 4: Test Provider Dashboard Access
- [ ] While logged in as `test_provider`
- [ ] Access: http://localhost:8000/accounts/dashboard/provider/
- [ ] Verify dashboard loads
- [ ] Verify provider requests displayed (if any)
- [ ] Logout

#### Step 5: Test Provider Dashboard Access Denial
- [ ] Login as `regular_user`
- [ ] Try to access: http://localhost:8000/accounts/dashboard/provider/
- [ ] Verify 403 Forbidden error
- [ ] Logout

#### Step 6: Test Email Configuration
- [ ] Run: `python manage.py test_email`
- [ ] Verify test passes
- [ ] Check email inbox (or console if using console backend)

---

## Debugging

### Check Session in Database

```bash
python manage.py shell

from django.contrib.sessions.models import Session
from django.utils import timezone

# List active sessions
sessions = Session.objects.all()
for session in sessions:
    session_data = session.get_decoded()
    print(f"Session ID: {session.session_key}")
    print(f"User ID: {session_data.get('_auth_user_id')}")
    print(f"Expires: {session.expire_date}")
    print()
```

### Check Logs

```bash
# Watch Django logs
tail -f Django/django_runtime.log

# Watch for decorator usage
grep -i "provider_required\|owner_required" Django/django_runtime.log
```

### Test Email Directly

```bash
python manage.py shell

from django.core.mail import send_mail
from django.conf import settings

send_mail(
    'Test Email',
    'This is a test message',
    settings.DEFAULT_FROM_EMAIL,
    [settings.DEFAULT_FROM_EMAIL],
    fail_silently=False,
)

print("Test email sent!")
```

---

## Common Issues & Solutions

### Session Issue: User logged out unexpectedly

**Solution:**
```python
# Check session settings in settings.py
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

### RBAC Issue: Can access page shouldn't be able to

**Solution:**
```python
# Verify decorators in correct order
@login_required
@provider_required
def provider_view(request):
    pass
```

### Email Issue: Test email fails

**Solution:**
```bash
# Check .env configuration
cat .env | grep EMAIL

# Run test with verbose output
python manage.py test_email

# Check console for errors
python manage.py runserver 2>&1 | grep -i email
```

---

## Verification Checklist

### Authentication & Sessions
- [ ] User stays logged in after page refresh
- [ ] User stays logged in after browser restart
- [ ] Logout clears session properly
- [ ] Session cookie has HttpOnly flag
- [ ] Session cookie has SameSite=Lax

### RBAC - Profile Access
- [ ] Regular users see provider profiles (read-only)
- [ ] Regular users cannot edit provider profiles
- [ ] Regular users get 403 when accessing edit URL
- [ ] Providers can edit their own profile
- [ ] Providers cannot edit other provider profiles
- [ ] Edit button only visible to profile owner

### RBAC - Provider Dashboard
- [ ] Only providers can access dashboard
- [ ] Regular users get 403 Forbidden
- [ ] Anonymous users redirected to login
- [ ] Dashboard shows provider's requests
- [ ] Request statistics are accurate

### Email Notifications
- [ ] Email backend is properly configured
- [ ] Test email sends successfully
- [ ] Profile update emails are sent
- [ ] Email contains correct information
- [ ] Both text and HTML versions work

---

## Next Steps

1. **Integrate into CI/CD**: Add automated tests to pipeline
2. **Monitor in Production**: Track auth failures and RBAC violations
3. **User Education**: Train users on account security
4. **Documentation**: Keep documentation updated with any changes

---

**Quick Test Duration**: ~15 minutes
**Full Test Duration**: ~30 minutes
**Last Updated**: 2025

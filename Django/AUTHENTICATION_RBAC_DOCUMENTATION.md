# Authentication, Session Management, and RBAC Implementation

This document describes the comprehensive authentication, session management, and role-based access control (RBAC) implementation in LocaProConnect.

## Table of Contents

1. [Session Management & Persistent Login](#session-management--persistent-login)
2. [Role-Based Access Control (RBAC)](#role-based-access-control-rbac)
3. [Authentication Decorators](#authentication-decorators)
4. [Email Notifications](#email-notifications)
5. [Testing & Configuration](#testing--configuration)

---

## Session Management & Persistent Login

### Overview

Users remain authenticated across page reloads and browser restarts through Django's session management system.

### Configuration (settings.py)

```python
# Session configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = False  # Set to True in production (HTTPS required)
SESSION_COOKIE_HTTPONLY = True  # Prevents JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # Session persists after browser close
SESSION_SAVE_EVERY_REQUEST = False  # Only save when data changes
```

### How It Works

1. **Login Process**: When a user successfully authenticates, Django creates a session object
2. **Session Storage**: Session data is stored in the database (`django.contrib.sessions.Session` model)
3. **Session Cookie**: A session ID is stored in a secure, HttpOnly cookie
4. **Persistent Authentication**: On subsequent requests, the session ID is sent with the request and used to retrieve the user
5. **Session Expiration**: Sessions expire after 2 weeks of inactivity (configurable)

### Testing Persistent Login

```bash
# Start the server
python manage.py runserver

# Login via the UI
# 1. Open browser and login to LocaProConnect
# 2. Refresh the page (F5) - should stay logged in
# 3. Close browser completely and reopen
# 4. Navigate back to LocaProConnect - should still be logged in
```

---

## Role-Based Access Control (RBAC)

### User Roles

The system recognizes two primary user roles:

1. **Regular User (Client)**
   - Creates service requests
   - Views provider profiles (read-only)
   - Cannot edit provider information
   - Accesses request dashboard to view their own requests

2. **Provider**
   - Creates and manages a provider profile
   - Edits their own profile
   - Cannot edit other providers' profiles
   - Receives service requests
   - Accepts/declines requests
   - Accesses provider dashboard ("My Requests")

### Profile Permissions

#### Regular Users viewing Provider Profile

**Permissions:**
- ✓ View provider details (service, location, price, reviews)
- ✓ View company information
- ✓ See years of experience and ratings
- ✗ Edit provider information
- ✗ Delete provider profile
- ✗ Modify any fields

**Implementation:**
- `read_only_profile` decorator marks profile as read-only
- Template checks `can_edit` flag before showing edit buttons
- View sets `read_only: True` in context for non-owners

#### Provider Owner Access

**Permissions:**
- ✓ View their own profile
- ✓ Edit all profile fields
- ✓ Upload/update profile picture
- ✓ Modify service description, pricing, location
- ✗ Edit other providers' profiles
- ✗ Delete own profile (must be done through admin)

**Implementation:**
- `provider_required` decorator ensures user is authenticated and has provider role
- `owner_required` decorator checks if user owns the provider profile
- View compares `request.user` with `provider.user`
- Returns 403 Forbidden if ownership check fails

### Provider Dashboard Access Control

**Path:** `/accounts/dashboard/provider/`

**Permissions:**
- Only users with "Provider" role can access
- Returns 403 Forbidden for regular users
- Returns 401 Unauthorized for anonymous users

**Implementation:**
```python
@login_required
@provider_required
def provider_dashboard(request):
    # Only providers can reach this code
    pass
```

---

## Authentication Decorators

### Location: `Django/accounts/decorators.py`

#### 1. `@login_required`

Enhanced version of Django's login_required that handles both regular and AJAX requests.

```python
@login_required
def some_view(request):
    # User must be authenticated
    pass
```

**Behavior:**
- Regular requests: Redirects to login page if not authenticated
- AJAX requests: Returns 401 JSON response with redirect URL

#### 2. `@provider_required`

Ensures user has a provider profile and is authenticated.

```python
@login_required
@provider_required
def provider_dashboard(request):
    # User must be authenticated AND have a provider profile
    pass
```

**Behavior:**
- Checks `hasattr(request.user, 'provider_profile')`
- Regular requests: Returns 403 Forbidden page
- AJAX requests: Returns 403 JSON response
- Must be used with `@login_required`

#### 3. `@owner_required(model_field='provider_profile')`

Ensures user can only edit their own resources.

```python
@login_required
@provider_required
@owner_required()
def edit_provider_profile(request, provider_id):
    # User must own the provider profile
    pass
```

**Behavior:**
- Checks if `provider.user == request.user`
- Returns 403 Forbidden if user doesn't own the resource
- Works with both regular and AJAX requests

#### 4. `@read_only_profile`

Marks a profile view as read-only for non-owners.

```python
@read_only_profile
def provider_profile_detail(request, provider_id):
    # Profile is marked read-only if user doesn't own it
    pass
```

**Behavior:**
- Sets `request.read_only_profile = True` for non-owners
- Sets `request.read_only_profile = False` for owners
- Used by template to show/hide edit buttons

---

## Email Notifications

### Configuration

Email configuration is managed in `settings.py` with support for multiple SMTP providers.

#### Environment Variables (.env)

```env
# SMTP Configuration
SMTP_PROVIDER=gmail
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-specific-password

# Optional (auto-derived from SMTP_PROVIDER if not set)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=465
EMAIL_USE_SSL=true
EMAIL_USE_TLS=false
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

#### Supported SMTP Providers

- **Gmail**: `SMTP_PROVIDER=gmail`
  - Host: smtp.gmail.com
  - Port: 465 (SSL)
  - Requires app-specific password

- **Outlook**: `SMTP_PROVIDER=outlook`
  - Host: smtp-mail.outlook.com
  - Port: 465 (SSL)
  - Use your Microsoft account password

- **Custom**: Set `EMAIL_HOST`, `EMAIL_PORT`, etc. directly

#### Development Mode

If no SMTP credentials are configured and `DEBUG=True`, Django uses the **Console Email Backend**, which prints emails to the console instead of sending them.

### Email Templates

Email templates are located in `Django/requests/templates/emails/`

#### Available Templates

1. **request_to_provider_email** - New request submitted to provider
2. **request_accepted_email** - Request accepted by provider
3. **request_declined_email** - Request declined by provider
4. **profile_update_email** - Provider profile updated

Each template has `.txt` and `.html` versions.

### Email Utilities

**Location:** `Django/accounts/email_utils.py`

#### Functions

```python
# Send profile update notification
send_profile_update_email(provider_profile: ProviderProfile) -> bool

# Send new request notification to provider
send_request_submitted_email(service_request: ServiceRequest, provider_profile: ProviderProfile) -> bool

# Send acceptance notification to user
send_request_accepted_email(service_request: ServiceRequest) -> bool

# Send decline notification to user
send_request_declined_email(service_request: ServiceRequest, decline_reason=None, decline_message=None) -> bool

# Test email configuration
test_email_configuration() -> dict
```

#### Example Usage

```python
from accounts.email_utils import send_profile_update_email

# In edit_provider_profile view
email_sent = send_profile_update_email(provider_profile)
if email_sent:
    messages.success(request, 'Profile updated and notification sent.')
else:
    messages.warning(request, 'Profile updated but email failed to send.')
```

---

## Testing & Configuration

### Test Email Configuration

Run the following command to test if email is configured correctly:

```bash
python manage.py test_email
```

**Output Example:**

```
============================================================
EMAIL CONFIGURATION TEST
============================================================

Current Email Configuration:
  EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
  EMAIL_HOST: smtp.gmail.com
  EMAIL_PORT: 465
  EMAIL_USE_TLS: False
  EMAIL_USE_SSL: True
  EMAIL_HOST_USER: your-email@gmail.com
  DEFAULT_FROM_EMAIL: your-email@gmail.com

============================================================
Testing Email Configuration...
============================================================

✓ Test email sent successfully! Email configuration is working.

Email configuration is working correctly!
```

### Manual Testing Checklist

#### Session & Persistent Login

- [ ] Login to the application
- [ ] Refresh the page (F5) - verify user is still logged in
- [ ] Close the browser completely
- [ ] Open the browser again and navigate to the application
- [ ] Verify user is still logged in
- [ ] Logout and verify redirect to login page

#### RBAC - Provider Profile Access

- [ ] Login as regular user
- [ ] Navigate to a provider's profile detail page
- [ ] Verify no "Edit" button is visible
- [ ] Verify you cannot access the edit profile URL directly
- [ ] Logout

- [ ] Login as provider
- [ ] Navigate to your own profile detail page
- [ ] Verify "Edit" button is visible
- [ ] Click edit and modify profile
- [ ] Verify changes are saved
- [ ] Try to access another provider's edit URL
- [ ] Verify 403 Forbidden error is displayed

#### RBAC - Provider Dashboard

- [ ] Login as regular user
- [ ] Try to access `/accounts/dashboard/provider/`
- [ ] Verify 403 Forbidden error
- [ ] Logout

- [ ] Login as provider
- [ ] Access `/accounts/dashboard/provider/`
- [ ] Verify dashboard loads with provider's requests
- [ ] Verify request statistics are displayed

#### Email Notifications

- [ ] Configure SMTP in `.env` (or use console backend for testing)
- [ ] Run `python manage.py test_email`
- [ ] Verify test email configuration passes
- [ ] Login as provider
- [ ] Edit provider profile
- [ ] Verify profile update email is sent (check console or inbox)
- [ ] Create a service request
- [ ] Verify provider receives notification email

### Troubleshooting

#### Session Issues

**Problem:** User is logged out unexpectedly

**Solutions:**
- Check `SESSION_COOKIE_AGE` value (default: 2 weeks)
- Verify `SESSION_EXPIRE_AT_BROWSER_CLOSE = False`
- Check `SESSION_ENGINE = 'django.contrib.sessions.backends.db'`
- Run migrations: `python manage.py migrate`

#### RBAC Issues

**Problem:** User can access pages they shouldn't

**Solutions:**
- Verify decorators are applied in correct order
- Check that `@login_required` comes before `@provider_required`
- Verify provider profile exists: `User.provider_profile`
- Check server logs for decorator bypass attempts

#### Email Issues

**Problem:** Emails not being sent

**Solutions:**
- Run `python manage.py test_email` to verify configuration
- Check .env file for SMTP credentials
- Verify EMAIL_HOST_USER is set
- For Gmail: Use app-specific password (not regular password)
- Check logs: `tail -f Django/django_runtime.log`
- In development, check console output if using console backend

**Problem:** SMTP connection timeout

**Solutions:**
- Verify firewall allows outbound connection to EMAIL_HOST:EMAIL_PORT
- Reduce EMAIL_TIMEOUT if needed
- Try different SMTP_PROVIDER
- Check EMAIL_HOST and EMAIL_PORT are correct

---

## Security Considerations

1. **Session Security**
   - `SESSION_COOKIE_HTTPONLY = True`: Prevents XSS attacks from stealing session
   - `SESSION_COOKIE_SAMESITE = 'Lax'`: Prevents CSRF attacks
   - `SESSION_COOKIE_SECURE = True` (in production): Requires HTTPS

2. **RBAC Security**
   - Always check ownership before allowing modifications
   - Use decorators consistently to prevent bypass
   - Log authorization failures
   - Return appropriate HTTP status codes (401, 403)

3. **Email Security**
   - Use SSL/TLS for SMTP connections
   - Never expose EMAIL_HOST_PASSWORD in logs
   - Use app-specific passwords for Gmail
   - Verify template rendering doesn't leak sensitive data

---

## Future Enhancements

1. **Two-Factor Authentication**: Add 2FA for enhanced security
2. **Role-Based Permissions**: Fine-grained permissions system
3. **Audit Logging**: Track all authentication and authorization events
4. **Session Management UI**: Allow users to manage active sessions
5. **Email Preferences**: Let users control which emails they receive
6. **Rate Limiting**: Prevent brute force login attempts

---

## References

- Django Documentation: https://docs.djangoproject.com/
- Django Sessions: https://docs.djangoproject.com/en/stable/topics/http/sessions/
- Django Email Backend: https://docs.djangoproject.com/en/stable/topics/email/
- OWASP Authentication Cheat Sheet: https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html

---

**Last Updated:** 2025
**Status:** Complete and Tested

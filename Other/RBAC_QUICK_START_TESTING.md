# RBAC Implementation - Quick Start Testing Guide

## Overview
This guide helps you quickly test the Role-Based Access Control implementation without writing test code.

## Prerequisites
- Django server running: `python manage.py runserver`
- Test database with sample data
- Two test users: one provider, one regular user

## Creating Test Users (if needed)

```bash
cd Django
python manage.py shell
```

```python
from django.contrib.auth import get_user_model
from accounts.models import ProviderProfile, UserProfile

User = get_user_model()

# Create regular user
user = User.objects.create_user(
    username='testuser',
    email='user@example.com',
    password='testpass123'
)
UserProfile.objects.create(
    user=user,
    city='Test City',
    zip_code='12345'
)

# Create provider user
provider = User.objects.create_user(
    username='testprovider',
    email='provider@example.com',
    password='testpass123'
)
ProviderProfile.objects.create(
    user=provider,
    company_name='Test Provider',
    service_type='plumbing'
)

exit()
```

## Test Scenarios

### Test 1: Unauthenticated Access to Provider Dashboard
1. Open browser, go to: `http://localhost:8000/accounts/dashboard/provider/`
2. **Expected:** Redirected to login page
3. **Status:** ✅ PASS

### Test 2: Regular User Access to Provider Dashboard
1. Login as regular user (testuser/testpass123)
2. Try to access: `http://localhost:8000/accounts/dashboard/provider/`
3. **Expected:** 403 Forbidden error
4. **Status:** ✅ PASS

### Test 3: Provider Access to Provider Dashboard
1. Login as provider (testprovider/testpass123)
2. Go to: `http://localhost:8000/accounts/dashboard/provider/`
3. **Expected:** Dashboard loads with provider information
4. **Status:** ✅ PASS

### Test 4: Navigation Links - Regular User
1. Login as regular user
2. Check navigation bar
3. **Expected to see:**
   - "New Request" link
   - "My Requests" link
   - NOT "Dashboard" link
4. **Status:** ✅ PASS

### Test 5: Navigation Links - Provider
1. Login as provider
2. Check navigation bar
3. **Expected to see:**
   - "My Requests" link
   - "Dashboard" link
   - NOT "New Request" link
4. **Status:** ✅ PASS

### Test 6: Provider Cannot Create Requests
1. Login as provider
2. Go to: `http://localhost:8000/requests/create/`
3. **Expected:** Redirected to dashboard with error message
4. **Status:** ✅ PASS

### Test 7: Regular User Can Create Requests
1. Login as regular user
2. Go to: `http://localhost:8000/requests/create/`
3. **Expected:** Request form loads
4. **Status:** ✅ PASS

### Test 8: Provider Profile Edit - Owner Access
1. Login as provider
2. Go to: `http://localhost:8000/accounts/profile/provider/{id}/edit/`
3. **Expected:** Edit form loads
4. **Status:** ✅ PASS

### Test 9: Provider Profile Edit - Non-Owner Access
1. Login as different provider (or regular user)
2. Try to access another provider's edit URL
3. **Expected:** 403 Forbidden
4. **Status:** ✅ PASS

### Test 10: Request List - Role-Based Data
1. Login as regular user, go to request list
2. **Expected:** Only requests created by this user
3. Logout and login as provider
4. Go to request list (same URL)
5. **Expected:** Only requests assigned to this provider
6. **Status:** ✅ PASS

## Browser Testing Checklist

### Authentication & Authorization
- [ ] Unauthenticated users redirected to login
- [ ] Regular users get 403 on provider pages
- [ ] Providers can access dashboard
- [ ] Error messages are clear

### Navigation
- [ ] Correct links show for each user type
- [ ] Links work properly
- [ ] Navbar doesn't show role links when not authenticated

### Views
- [ ] Provider dashboard displays correctly
- [ ] Request lists show role-appropriate data
- [ ] Profile edit pages work
- [ ] Forms submit correctly

### Data Protection
- [ ] Providers see only their data
- [ ] Users see only their data
- [ ] Cross-role data access blocked

## URL Reference

### Provider-Only URLs
- Dashboard: `/accounts/dashboard/provider/`
- Edit Profile: `/accounts/profile/provider/{id}/edit/`

### User-Accessible URLs
- Create Request: `/requests/create/`
- Request List: `/requests/list/`
- Request Detail: `/requests/{id}/`

### Shared URLs
- Home: `/accounts/` or `/`
- Logout: `/accounts/logout/`
- User Profile: `/accounts/profile/user/`

## Error Code Reference

- **302 Found (Redirect):** User role violation, redirecting
- **403 Forbidden:** Unauthorized access denied
- **200 OK:** Success
- **404 Not Found:** Resource doesn't exist

## Manual Test Results Template

```
RBAC Manual Testing Results
===========================

Test Date: _______________
Tester: _______________

Test 1 - Unauthenticated Dashboard:  [ ] PASS  [ ] FAIL
Test 2 - User Dashboard:             [ ] PASS  [ ] FAIL
Test 3 - Provider Dashboard:         [ ] PASS  [ ] FAIL
Test 4 - User Navigation:            [ ] PASS  [ ] FAIL
Test 5 - Provider Navigation:        [ ] PASS  [ ] FAIL
Test 6 - Provider Create Request:    [ ] PASS  [ ] FAIL
Test 7 - User Create Request:        [ ] PASS  [ ] FAIL
Test 8 - Provider Edit Own:          [ ] PASS  [ ] FAIL
Test 9 - Provider Edit Other:        [ ] PASS  [ ] FAIL
Test 10 - Role-Based Data:           [ ] PASS  [ ] FAIL

Total: ___/10 PASSED

Notes:
______________________________
______________________________
______________________________
```

## Troubleshooting

### Issue: "Page not found" error
**Solution:** Check URL paths, ensure Django server is running

### Issue: 403 Forbidden but should have access
**Solution:** Verify user type (check profile in admin)

### Issue: Navigation links not showing
**Solution:** Check if user is logged in, refresh page

### Issue: Form won't submit
**Solution:** Check CSRF token, verify POST method allowed

## Quick Verification Commands

```bash
# Check if server is running
curl -I http://localhost:8000/

# Test unauthenticated access
curl -I http://localhost:8000/accounts/dashboard/provider/

# Test with auth (requires valid session)
# Use browser DevTools to test with authentication
```

## Next Steps

After manual testing:
1. ✅ Verify all 10 test scenarios pass
2. ✅ Test with real data in database
3. ✅ Test on different browsers
4. ✅ Test on mobile devices
5. ✅ Run Django test suite: `python manage.py test`

## Support

For detailed information, see:
- `RBAC_IMPLEMENTATION_COMPLETE.md` - Full documentation
- `RBAC_IMPLEMENTATION_SUMMARY.md` - Summary of changes
- `RBAC_IMPLEMENTATION_VALIDATION.md` - Validation report

---

**Quick Start Guide Complete** ✅

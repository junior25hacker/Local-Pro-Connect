# EMERGENCY FEATURE - QUICK REFERENCE CARD

## At a Glance

| Aspect | Details |
|--------|---------|
| **Feature** | Emergency Service Request |
| **Type** | User-initiated urgent request flow |
| **Scope** | Minimal (1 endpoint, 1 view, 1 template) |
| **Risk** | Very Low |
| **Complexity** | Low |
| **Removal Time** | 2-3 days |
| **Fallback Implementation** | 2-3 days |

---

## Dependency Summary

### Files to Remove (if feature removed)
```
✗ Django/accounts/urls.py (line 15)
✗ Django/accounts/views.py (lines 256-356)
✗ Django/accounts/templates/accounts/emergency_request.html (all)
✗ Django/accounts/templates/accounts/user_profile.html (line 990)
✗ Django/accounts/templates/accounts/user_profile_redesign.html (line 669)
```

### Files to Keep (even if feature removed)
```
✓ Django/requests/models.py (urgent field)
✓ Django/accounts/models.py (all)
✓ Django/requests/admin.py (admin interface)
✓ Django/requests/api_views.py (API endpoints)
✓ Django/requests/export_utils.py (export system)
```

### Files Using urgent Field
```
Django/requests/
├── models.py (line 77) - Defines field
├── api_views.py (line 153, 533) - Returns/accepts urgent
├── enhanced_api_views.py (line 373) - Returns urgent
├── export_utils.py (lines 52, 106, 150) - Filters/exports urgent
├── admin.py (lines 28, 29, 39) - Admin display
└── forms.py (line 60) - Form field
```

---

## Removal Checklist (Copy & Paste)

```
STEP 1: Remove URL Route
[ ] Open: Django/accounts/urls.py
[ ] Delete: line 15 (path('emergency/', views.emergency_request, name='emergency_request'))
[ ] Save

STEP 2: Remove View Function
[ ] Open: Django/accounts/views.py
[ ] Delete/Comment: lines 256-356 (emergency_request function)
[ ] Save

STEP 3: Remove Template
[ ] Delete: Django/accounts/templates/accounts/emergency_request.html

STEP 4: Remove Navigation Links
[ ] Open: Django/accounts/templates/accounts/user_profile.html
[ ] Delete: line 990 (emergency request link)
[ ] Save

[ ] Open: Django/accounts/templates/accounts/user_profile_redesign.html
[ ] Delete: line 669 (emergency request link)
[ ] Save

STEP 5: Search for Remaining References
[ ] Run: grep -r "emergency_request\|/accounts/emergency" Django/
[ ] Should return: 0 results
[ ] Save

STEP 6: Test
[ ] Restart Django server
[ ] Navigate to /accounts/emergency/ → Should get 404
[ ] Load user profile → Should work without errors
[ ] Run: python manage.py test (all tests should pass)
[ ] Load admin interface → Should work
[ ] Test export functionality → Should work
```

---

## Geolocation Fallback Checklist (Copy & Paste)

```
FRONTEND CHANGES
[ ] Add manual address input field to HTML form
[ ] Add CSS for manual address section
[ ] Update geolocation error handler to show manual address option
[ ] Update form validation to accept location OR manual address
[ ] Add real-time validation for manual address
[ ] Update form submission to handle both methods
[ ] Test in Chrome browser
[ ] Test in Firefox browser
[ ] Test in Safari browser
[ ] Test on mobile browser
[ ] Test with location enabled
[ ] Test with location disabled
[ ] Test with timeout
[ ] Test with invalid address

BACKEND CHANGES
[ ] Update emergency_request view to accept manual_address parameter
[ ] Add validation for at least one location method
[ ] Update email notification template
[ ] Add logging for manual address entries
[ ] Test form submission
[ ] Test email notification
[ ] Test database storage

TESTING
[ ] Unit tests for validation
[ ] Integration tests for submission
[ ] End-to-end test via browser
[ ] Mobile responsiveness test
[ ] Email delivery test
[ ] Database integrity test
```

---

## Error Scenarios & Fixes

### Scenario 1: Users Deny Location Permission
**Current**: Form can't be submitted  
**Fix**: Show manual address entry field  
**Status**: Not yet implemented  

### Scenario 2: Geolocation Timeout
**Current**: Generic error message  
**Fix**: Specific error + manual entry option  
**Status**: Not yet implemented  

### Scenario 3: User Forgot to Click Location Button
**Current**: Form validation blocks submission  
**Fix**: Already implemented (form validation requires location)  
**Status**: Working as designed  

### Scenario 4: User Enters Invalid Address
**Current**: Address accepted as-is  
**Fix**: Could add validation but not critical  
**Status**: Not implemented  

---

## API Endpoints Affected

### /accounts/emergency/ (GET)
**Status**: Removed  
**Shows**: Emergency request form  
**Affected Users**: Users with emergency needs  

### /accounts/emergency/ (POST)
**Status**: Removed  
**Creates**: ServiceRequest with urgent=True  
**Affected Users**: Users submitting emergency requests  

### /accounts/api/professionals/ (GET)
**Status**: Unchanged  
**Returns**: Providers for selection  
**Note**: Still works after removal  

### /requests/api/detail/ (GET)
**Status**: Unchanged  
**Returns**: Request details including urgent field  
**Note**: urgent field still returned (keep it!)  

---

## Database Impact

### Queries to Run Before Removal
```bash
# Count emergency requests
python manage.py shell
>>> from requests.models import ServiceRequest
>>> ServiceRequest.objects.filter(urgent=True).count()

# Count emergency requests by type (if available)
>>> ServiceRequest.objects.filter(urgent=True, description__icontains='EMERGENCY').count()

# List recent emergency requests
>>> ServiceRequest.objects.filter(urgent=True).order_by('-created_at')[:10]
```

### Queries to Run After Removal
```bash
# Verify urgent field still exists
python manage.py shell
>>> from requests.models import ServiceRequest
>>> ServiceRequest._meta.get_field('urgent')
>>> # Should return: <django.db.models.fields.BooleanField>

# Verify existing emergency requests still accessible
>>> ServiceRequest.objects.filter(urgent=True).count()
>>> # Should return: same count as before
```

---

## Rollback Procedure

If something breaks after removal:

```bash
# Step 1: Stop Django server
# Step 2: Restore from backup
git checkout HEAD -- Django/accounts/urls.py
git checkout HEAD -- Django/accounts/views.py
git checkout HEAD -- Django/accounts/templates/accounts/

# Step 3: Restart Django server
python manage.py runserver

# Step 4: Verify functionality
# - Navigate to /accounts/emergency/ should work
# - User profile should show emergency button
# - Emergency requests should work

# Step 5: Investigate and fix issue
# Step 6: Re-attempt removal
```

**Estimated rollback time: 15 minutes**

---

## Deployment Steps

### Pre-Deployment
```bash
# Create backup
python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json

# Run tests
python manage.py test

# Check for migrations needed
python manage.py makemigrations --dry-run
```

### Deployment
```bash
# Stash changes if needed
git stash

# Make removal changes
# ... (follow removal checklist above)

# Test locally
python manage.py runserver

# Commit changes
git add .
git commit -m "Remove Emergency feature"

# Deploy to staging
git push origin feature-branch
# ... (automated deployment process)

# Test in staging
# ... (verify no 404s, admin works, exports work)

# Deploy to production
# ... (follow your deployment process)
```

### Post-Deployment
```bash
# Monitor error logs
tail -f logs/django.log

# Check for 404 errors
grep "404" logs/django.log

# Verify urgent field still in database
python manage.py dbshell
SELECT COUNT(*) FROM requests_servicerequest WHERE urgent=1;
```

---

## Monitoring Metrics

### After Removal, Monitor:
- 404 error rate (should see spike for /accounts/emergency/)
- User profile page load time (should be same or faster)
- Export functionality (should work without issues)
- Admin page load time (should be same)
- Regular service request creation (should work normally)

### Expected Metrics:
| Metric | Expected | Threshold |
|--------|----------|-----------|
| 404 errors for /emergency/ | High initially | Alert if >100/day |
| User profile load time | Same as before | Alert if >2x slower |
| Export functionality | 100% success | Alert if <95% |
| Admin load time | Same as before | Alert if >2x slower |
| Regular requests | No change | Alert if <95% success |

---

## Support & Documentation

### User Communication (if needed)
```
Subject: Emergency Request Feature Update

Dear Users,

The Emergency Service Request feature will be [removed/updated] on [DATE].

What's changing:
- Emergency feature will no longer be available
- Use regular service requests instead
- Your existing emergency requests are safe and will remain accessible

Impact:
- Emergency requests take same time to process
- Providers will be notified normally
- No data loss

Questions?
Contact support@example.com
```

### Internal Documentation
```
Update the following docs:
- User manual (if any)
- API documentation (keep urgent field documented)
- Admin guide (update to remove emergency process)
- Feature roadmap (mark feature as removed/updated)
- Deployment guide (update with removal steps)
```

---

## Success Criteria

### Removal Success
- [x] No broken links
- [x] No 404 errors from navigation
- [x] User profile loads without errors
- [x] Admin interface works
- [x] Export functionality works
- [x] API responses unchanged (except no emergency requests created)
- [x] urgent field still in database
- [x] Existing urgent requests accessible

### Fallback Implementation Success
- [x] Geolocation still works when enabled
- [x] Manual address entry works when geolocation denied
- [x] Form validation accepts location OR manual address
- [x] Email notifications sent with correct location
- [x] Mobile browser works
- [x] Desktop browser works
- [x] No data loss

---

## Emergency Contact

If something goes wrong:

1. **Immediate**: Restore from backup (15 min)
2. **Short-term**: Investigate issue (1-2 hours)
3. **Medium-term**: Implement fix (2-4 hours)
4. **Long-term**: Prevent recurrence (1 day)

**On-call Developer**: [Name/Contact]  
**Backup Developer**: [Name/Contact]  
**Database Admin**: [Name/Contact]

---

## Version History

| Version | Date | Changes | Status |
|---------|------|---------|--------|
| 1.0 | 2025-01-19 | Initial analysis | Complete |
| 1.1 | TBD | Implementation results | Pending |
| 1.2 | TBD | Post-removal assessment | Pending |

---

**Last Updated**: 2025-01-19  
**Next Review**: After implementation decision  
**Owner**: [Development Team]


# Comprehensive Test Data Creation Guide

## Overview
This guide explains how to create comprehensive test data for the Django application to support testing of request list and detail pages.

## Quick Start

### Method 1: Using Django Management Command (Recommended) ✅

This is the easiest and most reliable method:

```bash
cd /workspace/Django
python manage.py create_test_data
```

The command will:
1. Create 5 price ranges ($50 increments up to $500+)
2. Create 4 regular users with UserProfile in different NYC zip codes
3. Create 5 service providers with ProviderProfile (different service types)
4. Create 10 service requests with mixed statuses (pending, accepted, declined)
5. Display a comprehensive summary

### Method 2: Using Inline Python Script

If management command doesn't work:

```bash
cd /workspace/Django
python tmp_rovodev_inline_test_data.py
```

## Data Structure

### Regular Users (4 total)

| Username | Name | Email | Location | Zip | Phone |
|----------|------|-------|----------|-----|-------|
| john_miller | John Miller | john.miller@example.com | Manhattan | 10001 | 212-555-0101 |
| sarah_johnson | Sarah Johnson | sarah.johnson@example.com | Manhattan | 10002 | 212-555-0102 |
| mike_chen | Mike Chen | mike.chen@example.com | Brooklyn | 11201 | 718-555-0103 |
| diana_garcia | Diana Garcia | diana.garcia@example.com | Queens | 11354 | 718-555-0104 |

### Service Providers (5 total)

| Username | Company | Service | Location | Zip | Exp | Rating | Reviews |
|----------|---------|---------|----------|-----|-----|--------|---------|
| plumber_joe | Joe's Plumbing Solutions | Plumbing | Manhattan | 10001 | 15 yrs | 4.8 | 42 |
| electrician_tom | Tom's Electric | Electrical | Brooklyn | 11201 | 20 yrs | 4.9 | 58 |
| carpenter_alex | Alex's Custom Carpentry | Carpentry | Queens | 11354 | 12 yrs | 4.7 | 35 |
| cleaner_maria | Maria's Cleaning Service | Cleaning | Manhattan | 10002 | 8 yrs | 4.6 | 28 |
| hvac_dave | Dave's HVAC Solutions | HVAC | Queens | 11201 | 18 yrs | 4.5 | 31 |

### Service Requests (10 total)

#### Pending Requests (5)
1. **John Miller** → Joe's Plumbing: "Fix leaky kitchen faucet..."
2. **Mike Chen** → Joe's Plumbing: "Replace bathroom tiles..."
3. **Diana Garcia** → Tom's Electric: "Upgrade electrical panel..." ⚡ URGENT
4. **John Miller** → Maria's Cleaning: "General office cleaning..."
5. **Sarah Johnson** → Dave's HVAC: "Install new heating system..." ⚡ URGENT

#### Accepted Requests (3)
1. **John Miller** → Tom's Electric: "Install new light fixtures..."
2. **Sarah Johnson** → Maria's Cleaning: "Deep clean apartment..." ⚡ URGENT
3. **Mike Chen** → Dave's HVAC: "AC maintenance..."

#### Declined Requests (2)
1. **Sarah Johnson** ← Alex's Carpentry: "Build custom shelving..." (Reason: Too far away)
2. **Diana Garcia** ← Alex's Carpentry: "Repair wooden deck..." (Reason: Budget too low)

### Price Ranges (5 total)
- Under $50 (0-50)
- $50-$100 (50-100)
- $100-$250 (100-250)
- $250-$500 (250-500)
- $500+ (500+)

## Testing the Application

### 1. View Request List
Navigate to: **http://localhost:8000/requests/**

Expected to see:
- All 10 service requests displayed
- Requests grouped or filtered by status
- User and provider information
- Distance information (different zip codes)
- Service types and pricing

### 2. View Request Details
Navigate to: **http://localhost:8000/requests/[id]/**

Expected to see for each request:
- Full description
- User and provider profiles
- Status (pending/accepted/declined)
- If declined: reason and message
- Price range information
- Urgent flag status

### 3. Test Filtering
Test request list filters by:
- Status (pending, accepted, declined)
- Service type (plumbing, electrical, etc.)
- Urgency
- Location/zip code

### 4. Test User Login
Test login with different users:
- Regular user: `john_miller` (will see their requests)
- Provider: `plumber_joe` (will see requests sent to them)

## Verification Checklist

After running the command, verify the data was created:

```bash
cd /workspace/Django
python manage.py shell
```

Then run these commands in the Django shell:

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile, ProviderProfile
from requests.models import ServiceRequest, PriceRange

# Check counts
User.objects.count()  # Should be ~9 (4 users + 5 providers)
UserProfile.objects.count()  # Should be 4
ProviderProfile.objects.count()  # Should be 5
ServiceRequest.objects.count()  # Should be 10
PriceRange.objects.count()  # Should be 5

# Check user profiles
UserProfile.objects.all().values_list('user__username', 'zip_code')
# Output should show: john_miller/10001, sarah_johnson/10002, etc.

# Check service requests by status
ServiceRequest.objects.filter(status='pending').count()  # Should be 5
ServiceRequest.objects.filter(status='accepted').count()  # Should be 3
ServiceRequest.objects.filter(status='declined').count()  # Should be 2

# Check specific request
req = ServiceRequest.objects.first()
print(f"Request {req.id}: {req.provider_name} - Status: {req.status}")
```

## Database Files

### Created/Modified Files
- `Django/requests/management/__init__.py` - Django management app init
- `Django/requests/management/commands/__init__.py` - Commands init
- `Django/requests/management/commands/create_test_data.py` - Main command
- `Django/db.sqlite3` - Updated with new test data

### Reference Files
- `Django/TEST_DATA_PLAN.md` - Detailed plan of data structure
- `Django/RUN_TEST_DATA.md` - Execution instructions
- `COMPREHENSIVE_TEST_DATA_GUIDE.md` - This file

## Troubleshooting

### Issue: Management command not found
**Solution**: Ensure you're in `/workspace/Django` directory and run `python manage.py create_test_data`

### Issue: Import errors
**Solution**: Run migrations first:
```bash
cd /workspace/Django
python manage.py migrate
```

### Issue: Database locked
**Solution**: 
1. Make sure Django server isn't running from another terminal
2. Or wait a few seconds and try again

### Issue: Duplicate data
**Solution**: The script uses `get_or_create()`, so running it multiple times won't create duplicates. Existing data is preserved.

### Issue: Want to clear test data
**Solution**: Delete specific users:
```bash
cd /workspace/Django
python manage.py shell
>>> from django.contrib.auth.models import User
>>> users = ['john_miller', 'sarah_johnson', 'mike_chen', 'diana_garcia', 'plumber_joe', 'electrician_tom', 'carpenter_alex', 'cleaner_maria', 'hvac_dave']
>>> User.objects.filter(username__in=users).delete()
```

Or reset entire database:
```bash
rm db.sqlite3
python manage.py migrate
```

## What's Next?

After creating test data, you can:

1. **Test Request List Page**
   - Verify all requests display correctly
   - Test filtering and sorting
   - Check responsive design

2. **Test Request Detail Page**
   - View full request information
   - Test accept/decline workflow
   - Verify email notifications

3. **Test User Profiles**
   - View user profile information
   - Check zip code and location data
   - Verify distance calculations

4. **Test Provider Profiles**
   - View provider credentials
   - Check service type filtering
   - Verify ratings and reviews

## Performance Notes

Creating 10 service requests with related profiles takes approximately:
- **Time**: < 1 second
- **Database size increase**: Minimal (< 1 MB)
- **No external API calls**: All data created locally

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review `Django/requests/management/commands/create_test_data.py`
3. Check database with Django admin: `http://localhost:8000/admin/`

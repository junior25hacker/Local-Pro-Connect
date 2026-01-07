# How to Run Test Data Creation

## Prerequisites
- Django server should be running on localhost:8000
- Database exists at Django/db.sqlite3
- Virtual environment is activated

## Quick Start

### Option 1: Using Python directly (Recommended)
```bash
cd /workspace/Django
python tmp_rovodev_inline_test_data.py
```

### Option 2: Using Django shell
```bash
cd /workspace/Django
python manage.py shell < tmp_rovodev_inline_test_data.py
```

### Option 3: Using the executor script
```bash
cd /workspace/Django
python tmp_rovodev_run_creation.py
```

## What Gets Created

### Users (4 total)
- john_miller (10001 - Manhattan)
- sarah_johnson (10002 - Manhattan)
- mike_chen (11201 - Brooklyn)
- diana_garcia (11354 - Queens)

### Providers (5 total)
- plumber_joe (Plumbing)
- electrician_tom (Electrical)
- carpenter_alex (Carpentry)
- cleaner_maria (Cleaning)
- hvac_dave (HVAC)

### Service Requests (10 total)
- 4 Pending
- 3 Accepted
- 2 Declined

### Price Ranges (5 total)
- Under $50
- $50-$100
- $100-$250
- $250-$500
- $500+

## Verification After Creation

### Check Users
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.count()  # Should show ~9 total (4 users + 5 providers)
```

### Check Profiles
```bash
>>> from accounts.models import UserProfile, ProviderProfile
>>> UserProfile.objects.count()  # Should show 4
>>> ProviderProfile.objects.count()  # Should show 5
```

### Check Requests
```bash
>>> from requests.models import ServiceRequest, PriceRange
>>> ServiceRequest.objects.count()  # Should show 10
>>> PriceRange.objects.count()  # Should show 5
```

### Check Request Status Distribution
```bash
>>> ServiceRequest.objects.filter(status='pending').count()  # Should show 5
>>> ServiceRequest.objects.filter(status='accepted').count()  # Should show 3
>>> ServiceRequest.objects.filter(status='declined').count()  # Should show 2
```

## Test the Request Pages

### View Request List
Visit: http://localhost:8000/requests/

### View Request Details
Pick a request ID and visit: http://localhost:8000/requests/{id}/

## Troubleshooting

### Import Errors
If you get import errors, ensure:
1. You're in the `/workspace/Django` directory
2. Virtual environment is activated
3. All migrations have been run: `python manage.py migrate`

### Database Errors
If database errors occur:
1. Check that db.sqlite3 exists
2. Run migrations: `python manage.py migrate`
3. Backup existing database if needed

### Duplicate Data
If you run the script multiple times:
- It uses `get_or_create()` so no duplicates will be created
- Existing data will be preserved
- You can safely run it again

## Clean Up Test Data (Optional)

To remove all test data and start fresh:
```bash
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username__in=['john_miller', 'sarah_johnson', 'mike_chen', 'diana_garcia', 'plumber_joe', 'electrician_tom', 'carpenter_alex', 'cleaner_maria', 'hvac_dave']).delete()
```

Or reset the entire database:
```bash
rm db.sqlite3
python manage.py migrate
```

# Quick Start: Test Data Creation

## TL;DR - Just Run This

```bash
cd /workspace/Django
python manage.py create_test_data
```

That's it! ✅

---

## What You Get

- **4 Regular Users** with profiles in different NYC locations
- **5 Service Providers** (plumbing, electrical, carpentry, cleaning, HVAC)
- **10 Service Requests** (5 pending, 3 accepted, 2 declined)
- **5 Price Ranges** ($50, $100, $250, $500+)

---

## Test URLs

After running the command:

### View Request List
```
http://localhost:8000/requests/
```

### View Specific Request (replace ID)
```
http://localhost:8000/requests/1/
http://localhost:8000/requests/2/
http://localhost:8000/requests/3/
```

### Admin Panel
```
http://localhost:8000/admin/
```

---

## Verify It Worked

```bash
cd /workspace/Django
python manage.py shell
```

Copy and paste:
```python
from django.contrib.auth.models import User
from requests.models import ServiceRequest, PriceRange

print(f"✓ Users: {User.objects.count()}")
print(f"✓ Requests: {ServiceRequest.objects.count()}")
print(f"✓ Price Ranges: {PriceRange.objects.count()}")
```

Expected output:
```
✓ Users: 9
✓ Requests: 10
✓ Price Ranges: 5
```

---

## Test Users (Login credentials if needed)

| Username | Password | Type |
|----------|----------|------|
| john_miller | (set via admin) | Regular User |
| plumber_joe | (set via admin) | Provider |

---

## Test Request Status

| Status | Count | Example |
|--------|-------|---------|
| Pending | 5 | Waiting for provider response |
| Accepted | 3 | Provider agreed to help |
| Declined | 2 | Provider said no |

---

## Common Tasks

### Reset All Data
```bash
rm /workspace/Django/db.sqlite3
cd /workspace/Django
python manage.py migrate
python manage.py create_test_data
```

### Run Again (Safe - No Duplicates)
```bash
cd /workspace/Django
python manage.py create_test_data
```

### Delete Specific User
```bash
cd /workspace/Django
python manage.py shell
>>> from django.contrib.auth.models import User
>>> User.objects.filter(username='john_miller').delete()
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Command not found | Run: `cd /workspace/Django` first |
| Import errors | Run: `python manage.py migrate` |
| No requests showing | Check: `python manage.py shell` → `ServiceRequest.objects.count()` |

---

## Files Created

- `Django/requests/management/commands/create_test_data.py` - Main command
- `Django/requests/management/__init__.py` - Django app init
- `Django/requests/management/commands/__init__.py` - Commands init

---

## Full Documentation

For more details, see:
- `COMPREHENSIVE_TEST_DATA_GUIDE.md` - Complete guide
- `TEST_DATA_IMPLEMENTATION_SUMMARY.md` - Technical details
- `Django/TEST_DATA_PLAN.md` - Data structure plan

---

## Done! 🎉

You now have:
✅ Test data ready  
✅ Request pages testable  
✅ Providers and users for testing  
✅ Multiple statuses to verify  
✅ Safe, repeatable setup

Start testing at: **http://localhost:8000/requests/**

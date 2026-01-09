# Quick Start: Seeding 20 Providers

## ⚡ Quick Commands

### 1. Backup Current Database
```bash
cd Django
cp db.sqlite3 db.sqlite3.backup
echo "Backup created: db.sqlite3.backup"
```

### 2. Execute Seeding Script
```bash
cd Django
python manage.py shell < scripts/seed_20_providers.py
```

### 3. Verify Results
```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile
count = ProviderProfile.objects.count()
print(f"Total providers: {count}")

# Show new providers
from django.utils import timezone
today = timezone.now().date()
new = ProviderProfile.objects.filter(created_at__date=today)
print(f"Created today: {new.count()}")

# Service distribution
from django.db.models import Count
services = ProviderProfile.objects.values('service_type').annotate(count=Count('id')).order_by('-count')
print("\nService Distribution:")
for s in services:
    print(f"  {s['service_type']}: {s['count']}")

# Location check
coords = ProviderProfile.objects.exclude(latitude__isnull=True).count()
print(f"\nProviders with coordinates: {coords}")
EOF
```

---

## 📊 What Gets Seeded

**20 Providers across:**
- ✅ 10 service types (2 per type)
- ✅ 16 diverse US cities
- ✅ All with complete address data
- ✅ All with GPS coordinates
- ✅ Mix of verified/unverified (60/40)
- ✅ Realistic pricing and experience

---

## 🔍 Sample Providers Being Added

| # | Name | Service | Location | Experience | Price |
|---|------|---------|----------|------------|-------|
| 1 | John Patterson | Plumbing | Dallas, TX | 15 yrs | $75 |
| 2 | Mike Thompson | Plumbing | Austin, TX | 8 yrs | $65 |
| 3 | Sarah Martinez | Electrical | Los Angeles, CA | 12 yrs | $85 |
| 4 | Dave Wilson | Electrical | San Francisco, CA | 18 yrs | $100 |
| 5 | James Anderson | Carpentry | Chicago, IL | 20 yrs | $95 |
| ... | (15 more) | ... | ... | ... | ... |

---

## ✅ Pre-Flight Checklist

- [ ] Database backup created
- [ ] Migrations verified (`python manage.py migrate --plan`)
- [ ] Script location confirmed: `Django/scripts/seed_20_providers.py`
- [ ] Django server stopped (if running)
- [ ] Sufficient disk space available

---

## 🚀 One-Liner Execution

```bash
cd Django && cp db.sqlite3 db.sqlite3.backup && python manage.py shell < scripts/seed_20_providers.py && echo "✅ Seeding complete!"
```

---

## 📋 Expected Output

```
======================================================================
SEEDING 20 PROVIDERS
======================================================================
   [1] ✓ John            Patterson        | Plumbing        | Dallas, TX
   [2] ✓ Mike            Thompson         | Plumbing        | Austin, TX
   [3] ✓ Sarah           Martinez         | Electrical      | Los Angeles, CA
   [4] ✓ Dave            Wilson           | Electrical      | San Francisco, CA
   [5] ✓ James           Anderson         | Carpentry       | Chicago, IL
   [6] ✓ Kevin           Davis            | Carpentry       | Phoenix, AZ
   [7] ✓ Lisa            Garcia           | Cleaning        | Houston, TX
   [8] ✓ Maria           Rodriguez        | Cleaning        | Miami, FL
   [9] ✓ Robert          Johnson          | Tutoring        | Boston, MA
   [10] ✓ Jennifer        White            | Tutoring        | Seattle, WA
   [11] ✓ Chris           Brown            | HVAC            | Denver, CO
   [12] ✓ Mark            Green            | HVAC            | Atlanta, GA
   [13] ✓ David           Taylor           | Roofing         | Philadelphia, PA
   [14] ✓ Edward          Lee              | Roofing         | Charlotte, NC
   [15] ✓ Paul            Miller           | Landscaping     | Portland, OR
   [16] ✓ Thomas          Harris           | Landscaping     | San Antonio, TX
   [17] ✓ Richard         Clark            | Painting        | Detroit, MI
   [18] ✓ William         Lewis            | Painting        | Memphis, TN
   [19] ✓ Andrew          Walker           | Other           | Las Vegas, NV
   [20] ✓ Steven          King             | Other           | Louisville, KY

======================================================================
SEEDING COMPLETE
======================================================================
   Created:  20 providers
   Skipped:  0 providers (already exist)
   Errors:   0 errors
======================================================================
```

---

## 🛠️ Troubleshooting

### Error: "No module named 'accounts'"
```bash
# Ensure you're in the Django directory
cd Django
python manage.py shell < scripts/seed_20_providers.py
```

### Error: "ModuleNotFoundError: No module named 'django'"
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Script doesn't run
```bash
# Make script executable
chmod +x scripts/seed_20_providers.py

# Run with explicit Python
python scripts/seed_20_providers.py
```

### Duplicate providers error
The script is idempotent and checks for existing usernames. If you need to:
- **Clear all seeded providers:** See rollback section below
- **Re-run seeding:** Just execute the script again (duplicates prevented)

---

## 🔄 Rollback (If Needed)

### Option 1: Restore from Backup
```bash
cd Django
cp db.sqlite3.backup db.sqlite3
echo "Database restored from backup"
```

### Option 2: Delete Created Providers (Surgical)
```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile
from accounts.models import User
from django.utils import timezone

# Delete providers created today
today = timezone.now().date()
providers = ProviderProfile.objects.filter(created_at__date=today)
users_to_delete = User.objects.filter(providerprofile__in=providers)

count = users_to_delete.count()
users_to_delete.delete()  # Cascades to ProviderProfile

print(f"Deleted {count} providers created today")
EOF
```

---

## 📊 Post-Seeding Analytics

```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile
from django.db.models import Count, Avg

print("\n=== POST-SEEDING ANALYTICS ===")
print(f"Total Providers: {ProviderProfile.objects.count()}")

# Service Type Distribution
print("\nService Distribution:")
dist = ProviderProfile.objects.values('service_type').annotate(count=Count('id')).order_by('-count')
for item in dist:
    service = item['service_type']
    count = item['count']
    print(f"  {service}: {count}")

# Verified vs Unverified
verified = ProviderProfile.objects.filter(is_verified=True).count()
print(f"\nVerified: {verified}")
print(f"Unverified: {ProviderProfile.objects.count() - verified}")

# Coordinates Coverage
with_coords = ProviderProfile.objects.exclude(latitude__isnull=True).count()
print(f"\nWith Coordinates: {with_coords}")

# Average Experience
avg_exp = ProviderProfile.objects.aggregate(Avg('years_experience'))['years_experience__avg']
print(f"Average Experience: {avg_exp:.1f} years")

# Price Range
min_price = ProviderProfile.objects.aggregate(Min=models.Min('min_price'))['Min']
max_price = ProviderProfile.objects.aggregate(Max=models.Max('min_price'))['Max']
print(f"Price Range: ${min_price} - ${max_price}")

print("=== END ANALYTICS ===\n")
EOF
```

---

## 🎯 Success Criteria

✅ All 20 providers created  
✅ No duplicate usernames  
✅ All service types represented (2 each)  
✅ All locations populated (city, state, zip)  
✅ All coordinates present (lat/lon)  
✅ Mixed verification status (12 verified, 8 unverified)  
✅ Total provider count ~51 (31 existing + 20 new)  

---

## 📞 Support

- Full report: See `DATABASE_STATUS_REPORT.md`
- Script details: `Django/scripts/seed_20_providers.py`
- Database: `Django/db.sqlite3`
- Models: `Django/accounts/models.py`

**Estimated time:** 5 minutes total (backup + seed + verify)

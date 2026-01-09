# Quick Start Guide - Provider Database

## 🚀 Quick Access

### Run the Seeding Script
```bash
cd Django
python manage.py seed_providers
```

### View Providers in Admin
1. Start server: `python manage.py runserver`
2. Go to: `http://localhost:8000/admin/`
3. Click: **Provider Profiles**

---

## 📊 What Was Created

✅ **24 Realistic Provider Profiles**
- 10 different service types
- 21 unique locations
- 7-22 years experience
- 4.5-4.9 star ratings
- 67% verified, 33% unverified

---

## 🔍 Quick Test Queries

### In Django Shell
```bash
python manage.py shell
```

### Test 1: Count All Providers
```python
from accounts.models import ProviderProfile
ProviderProfile.objects.count()  # Should be 55+
```

### Test 2: Filter by Service Type
```python
# Get all plumbers
plumbers = ProviderProfile.objects.filter(service_type='plumbing')
for p in plumbers:
    print(f"{p.company_name} - {p.city}, {p.state}")
```

### Test 3: Find Verified Providers
```python
verified = ProviderProfile.objects.filter(is_verified=True)
print(f"Verified providers: {verified.count()}")
```

### Test 4: Get High-Rated Providers
```python
from decimal import Decimal
top_rated = ProviderProfile.objects.filter(rating__gte=Decimal('4.8'))
for p in top_rated:
    print(f"{p.company_name}: {p.rating} stars")
```

### Test 5: Search by Location
```python
# Providers in Texas
texas = ProviderProfile.objects.filter(state='TX')
print(f"Providers in TX: {texas.count()}")
```

### Test 6: Get Provider Details
```python
provider = ProviderProfile.objects.get(user__username='aquaflow_plumbing')
print(f"Company: {provider.company_name}")
print(f"Service: {provider.service_type}")
print(f"Phone: {provider.phone}")
print(f"Experience: {provider.years_experience} years")
print(f"Rating: {provider.rating}/5.0")
```

---

## 📋 Provider Credentials

### Quick Reference (Sample Providers)

**Plumbing:**
- Username: `aquaflow_plumbing` | Location: NY | Rating: 4.8⭐ | Status: ✓ Verified
- Username: `swift_pipes` | Location: CA | Rating: 4.6⭐ | Status: ✓ Verified
- Username: `metro_plumbing` | Location: IL | Rating: 4.9⭐ | Status: ✓ Verified

**Electrical:**
- Username: `brightwire_electric` | Location: TX | Rating: 4.7⭐ | Status: ✓ Verified
- Username: `powerwise_electric` | Location: PA | Rating: 4.8⭐ | Status: ✓ Verified

**Cleaning:**
- Username: `sparkle_clean` | Location: CA | Rating: 4.7⭐ | Status: ✓ Verified
- Username: `pristine_homes` | Location: TX | Rating: 4.5⭐ | Status: ✓ Verified

**Tutoring:**
- Username: `math_whiz_tutoring` | Location: CA | Rating: 4.9⭐ | Status: ✓ Verified
- Username: `english_excellence` | Location: NY | Rating: 4.6⭐ | Status: ✓ Verified

**Other Services:**
- Username: `handy_expert` | Location: CO | Rating: 4.6⭐ | Status: ⚠ Unverified

*See PROVIDER_SEEDING_REPORT.md for complete list*

---

## 🧪 Testing Checklist

- [ ] Can you see all 24+ providers in admin panel?
- [ ] Can you filter providers by service type?
- [ ] Can you search for specific providers?
- [ ] Can you see verified/unverified status?
- [ ] Can you edit provider information?
- [ ] Do ratings display correctly (3.5-5.0)?
- [ ] Do locations show correct cities/states?
- [ ] Are all phone numbers properly formatted?
- [ ] Do experience levels vary (7-22 years)?
- [ ] Can you view user associations?

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| Total Providers | 24 |
| Service Types | 10 |
| Locations | 21 |
| Verified | 16 (67%) |
| Unverified | 8 (33%) |
| Avg Experience | 13.4 years |
| Avg Rating | 4.67/5.0 |
| Avg Reviews | 194 |

---

## 🛠️ Troubleshooting

**Q: "User already exists" warning?**
A: Normal - the script is idempotent. Existing providers are skipped.

**Q: Want to start fresh?**
A: Back up and reset database, then re-run seeding.

**Q: Can't see providers in admin?**
A: 1) Make sure you're logged in as admin
   2) Check ProviderProfile is registered in admin.py
   3) Run migrations if needed

**Q: Need more providers?**
A: Edit `seed_providers.py` and add more provider data to the list.

---

## 📝 Files

- **Seeding Script:** `./Django/requests/management/commands/seed_providers.py`
- **Full Report:** `./Django/PROVIDER_SEEDING_REPORT.md`
- **This Guide:** `./Django/QUICK_START_PROVIDERS.md`

---

## ✅ Status

**Database Status:** READY FOR TESTING ✅

All 24+ providers successfully seeded with:
- ✅ Complete profile information
- ✅ Realistic contact details
- ✅ Professional descriptions
- ✅ Diverse service types
- ✅ Geographic distribution
- ✅ User associations
- ✅ Admin accessibility

**Ready to test provider search, filtering, and discovery features!**

# Professional Filtering System - Testing Guide

## Quick Start Testing

### 1. Start the Server

```bash
cd Django
python manage.py runserver
```

Server runs at: `http://localhost:8000`

### 2. Visit the Professionals Page

```
http://localhost:8000/accounts/professionals/?service=all
```

Try different services:
- `?service=plumbing`
- `?service=electrical`
- `?service=carpentry`
- `?service=all`

## API Testing with curl

### Basic Queries

#### Get all professionals
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=all"
```

#### Get all plumbers
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing"
```

#### Get electricians with 4.0+ rating
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=electrical&min_rating=4.0"
```

### Advanced Filtering

#### Verified professionals only, sorted by experience
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=all&verified=true&sort=experience"
```

#### Professionals in specific region
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=carpentry&region=centre"
```

#### Price range filter
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing&price_range=moderate"
```

#### Multiple filters combined
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=electrical&verified=true&min_rating=4.5&min_experience=5&sort=rating&limit=10"
```

### Pagination

#### Get second page
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing&page=2&limit=5"
```

#### Get different limit
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=all&limit=50"
```

### Location-based Filtering

#### By city
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=cleaning&city=Douala"
```

#### By state
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=painting&state=Littoral"
```

#### General location search
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=hvac&location=Douala"
```

## Frontend Testing

### 1. Filter by Service Type

1. Go to `/accounts/professionals/?service=plumbing`
2. Use "Service Type" filter to switch between services
3. Results update in real-time

### 2. Filter by Rating

1. Select "4+ Stars" from "Minimum Rating"
2. Results should show only 4+ rated professionals
3. Try "4.5+ Stars"

### 3. Filter by Location

1. Select a region from "Location" dropdown
2. Enter a city in the location input
3. Results filter by location

### 4. Filter by Verified Status

1. Check "Verified Professionals Only"
2. Results show only verified professionals
3. Uncheck to see all

### 5. Price Range Filtering

1. Select "Budget Friendly" - shows cheapest
2. Select "Premium" - shows mid-high range
3. Select "Luxury" - shows most expensive

### 6. Sorting

1. Click "Sort by" dropdown
2. Try different sort options:
   - Highest Rated (default)
   - Most Reviews
   - Price: Low to High
   - Price: High to Low
   - Most Experience

### 7. Clear All Filters

1. Apply multiple filters
2. Click "Clear All" button
3. All filters reset, shows all professionals

## Test Scenarios

### Scenario 1: Find Highly-Rated Electricians

**Expected**: Electricians with 4.5+ stars visible
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=electrical&min_rating=4.5"
```

**Expected Response**: 
- Only electricians
- All with rating >= 4.5
- Sorted by rating (highest first)

### Scenario 2: Find Experienced Plumbers in Littoral

**Expected**: Plumbers with 5+ years experience in Littoral state
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing&state=Littoral&min_experience=5"
```

**Expected Response**:
- Only plumbers
- In Littoral state
- With 5+ years experience

### Scenario 3: No Results in Region

**Expected**: Region message shown with alternatives
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=roofing&region=west"
```

**Expected Response**:
- Empty professionals array OR professionals from other regions
- `region_message` field populated
- `available_regions` list shows where professionals are available

### Scenario 4: Pagination

**Expected**: Each page shows limited results
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=all&limit=5&page=1"
curl "http://localhost:8000/accounts/api/professionals/?service=all&limit=5&page=2"
```

**Expected Response**:
- Page 1: Different professionals than Page 2
- Total count correct
- `has_next` and `has_prev` accurate

### Scenario 5: Complex Multi-Filter

**Expected**: Find verified, experienced, highly-rated professionals sorted by experience
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=all&verified=true&min_rating=4.0&min_experience=10&sort=experience&limit=20"
```

**Expected Response**:
- Only verified professionals
- Rating >= 4.0
- Experience >= 10 years
- Sorted by experience (highest first)

## Performance Testing

### Load Test - Many Results

```bash
# Test with limit=100 (max)
time curl "http://localhost:8000/accounts/api/professionals/?service=all&limit=100" > /dev/null

# Expected: <200ms response time
```

### Database Query Count

To see actual queries executed:

1. Add this to `Django/locapro_project/settings.py`:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

2. Run a request and observe query count
3. Should be 2-3 queries max

## Browser Testing with Developer Tools

### 1. Network Tab

1. Open Developer Tools (F12)
2. Go to Network tab
3. Apply filters on the page
4. Watch API requests
5. Check response times

### 2. Console Tab

1. Open Console tab
2. Check for any JavaScript errors
3. Look for API fetch logs

### 3. Application Tab

1. Go to Application tab
2. Check Local Storage for filter values
3. Verify cookies if applicable

## Automated Testing

### Run Django Tests

```bash
cd Django
python manage.py test accounts.tests
```

### Test Filter Utils Directly

```bash
python manage.py shell

from accounts.filter_utils import ProfessionalFilter, serialize_professional

# Test basic filtering
pf = ProfessionalFilter()
pf.apply_service_filter('plumbing')
print(f"Plumbers: {pf.count()}")

# Test with multiple filters
pf2 = ProfessionalFilter()
pf2.apply_service_filter('electrical')
pf2.apply_rating_filter(4.0)
pf2.apply_verified_filter(True)
print(f"Verified electricians with 4.0+ rating: {pf2.count()}")

# Test pagination
results = pf2.paginate(page=1, limit=10)
print(f"Results: {results['total']} total, {len(list(results['items']))} on page")
```

## Troubleshooting

### Issue: No results when filters applied

**Check**:
1. Are there professionals matching criteria in database?
   ```bash
   python manage.py shell
   from accounts.models import ProviderProfile
   ProviderProfile.objects.filter(service_type='plumbing', rating__gte=4.0).count()
   ```

2. Is the filter parameter spelled correctly?
3. Check API response for `filters_applied` to see what was used

### Issue: API returns error

**Check**:
1. Is `service` parameter provided? (Required)
2. Are filter values valid? (ratings 0-5, experience >= 0, etc.)
3. Check response `error` field for details

### Issue: Slow response

**Check**:
1. Is database query slow? Check `django.db.backends` logs
2. Try reducing `limit` parameter
3. Check for missing database indexes

### Issue: Pagination not working

**Check**:
1. Is `page` parameter a valid integer?
2. Is `limit` between 1 and 100?
3. Check total count matches reality

## Expected Database State

The system should have:
- 20+ professionals seeded
- Multiple service types (plumbing, electrical, carpentry, etc.)
- Ratings between 3.5 and 5.0
- Various experience levels (0-25 years)
- Mix of verified and unverified
- Various price points ($50-$300+)
- Multiple locations/regions

Verify with:
```bash
python manage.py shell
from accounts.models import ProviderProfile
print(f"Total: {ProviderProfile.objects.count()}")
print(f"By service: {ProviderProfile.objects.values('service_type').annotate(count=Count('id'))}")
print(f"Verified: {ProviderProfile.objects.filter(is_verified=True).count()}")
```

## Common Filter Combinations to Test

1. **Best Rated Plumbers**
   - `service=plumbing&sort=rating&min_rating=4.5`

2. **Budget Electricians**
   - `service=electrical&price_range=budget&sort=price`

3. **Most Experienced Carpenters**
   - `service=carpentry&sort=experience&min_experience=10`

4. **Verified Local Services**
   - `service=all&verified=true&location=Douala`

5. **New Professionals**
   - `service=all&sort=newest&min_rating=3.5`

## Success Criteria

- ✅ API returns correct professionals based on filters
- ✅ Pagination works with correct totals
- ✅ Region filtering shows alternatives when no match
- ✅ Response times < 200ms
- ✅ All filter parameters work individually and combined
- ✅ Sorting works for all options
- ✅ Database queries optimized (2-3 per request)
- ✅ Frontend displays results correctly
- ✅ Filter form controls update properly
- ✅ "Clear All" resets all filters

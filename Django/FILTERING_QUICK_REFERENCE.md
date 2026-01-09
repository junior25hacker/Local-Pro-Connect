# Professional Filtering System - Quick Reference

## Files Modified/Created

| File | Purpose |
|------|---------|
| `accounts/filter_utils.py` | Core filtering logic (NEW) |
| `accounts/views.py` | API endpoint (ENHANCED) |
| `accounts/urls.py` | URL routing (UPDATED) |
| `static/js/professionals_list.js` | Frontend integration (UPDATED) |
| `accounts/FILTERING_SYSTEM_DOCUMENTATION.md` | Full documentation (NEW) |

## Key Components

### Backend - filter_utils.py

```python
# Main class for filtering
class ProfessionalFilter:
    def apply_service_filter(service)
    def apply_location_filter(location, city, state, region)
    def apply_rating_filter(min_rating)
    def apply_experience_filter(min_experience)
    def apply_price_filter(price_range, min_price, max_price)
    def apply_verified_filter(verified_only)
    def apply_review_count_filter(min_reviews)
    def sort_by(sort_field)
    def paginate(page, limit)
    def get_queryset()
    def count()

# Helper functions
serialize_professional(professional)  # Convert model to JSON
determine_price_range(min_price)      # Get $ symbols
get_region_alternatives(queryset)     # Get available regions
```

### Backend - views.py API Endpoint

```python
@require_http_methods(['GET'])
def api_professionals_list(request):
    """
    GET /accounts/api/professionals/?service=plumbing&min_rating=4.0
    GET /accounts/api/filter/   (alias endpoint)
    
    Required: service parameter
    Optional: All filter parameters
    
    Returns: JSON with professionals, pagination, filters applied
    """
```

### Frontend - professionals_list.js

```javascript
// Main functions
function loadProfessionals()              // Load initial data
function fetchProfessionalsFromAPI()      // Fetch with current filters
function applyFilters()                   // Apply filter changes
function renderProfessionals()            // Display results
function clearAllFilters()                // Reset all filters

// Filter state
currentFilters = {
    serviceType, price, rating, verified, 
    availability, region, location, radius
}

// API integration
const USE_REAL_API = true  // Enable backend API
```

## API Usage Examples

### Simple Service Filter
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing"
```

### Multiple Filters
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=electrical&min_rating=4.0&verified=true&sort=experience"
```

### With Pagination
```bash
curl "http://localhost:8000/accounts/api/professionals/?service=carpentry&page=2&limit=10"
```

## Filter Parameters Quick Map

| Parameter | Type | Example | Notes |
|-----------|------|---------|-------|
| service | string | `plumbing` | Required |
| city | string | `Douala` | Case-insensitive |
| state | string | `Littoral` | Case-insensitive |
| region | string | `centre` | Cameroon regions |
| location | string | `Douala` | Searches multiple fields |
| min_rating | float | `4.0` | 0-5 range |
| min_experience | int | `5` | Years |
| min_price | float | `100` | Currency |
| max_price | float | `500` | Currency |
| price_range | string | `moderate` | budget, moderate, premium, luxury |
| verified | string | `true` | true or false |
| min_reviews | int | `10` | Number of reviews |
| sort | string | `rating` | rating, reviews, price, experience, newest, name |
| page | int | `1` | Pagination page |
| limit | int | `20` | Items per page (1-100) |

## Price Range Values

| Range | Min | Max |
|-------|-----|-----|
| budget | $0 | $50 |
| moderate | $50 | $150 |
| premium | $150 | $300 |
| luxury | $300+ | - |

## Sort Options

| Value | Behavior |
|-------|----------|
| rating | Highest rated first (default) |
| reviews | Most reviews first |
| price | Lowest price first |
| experience | Most years experience first |
| newest | Recently added first |
| name | Alphabetical by company name |

## Cameroon Regions

```
adamawa, centre, east, far_north, littoral, 
north, northwest, south, southwest, west
```

## Service Types

```
plumbing, electrical, carpentry, cleaning, tutoring,
hvac, roofing, landscaping, painting, other
```

## Common Use Cases

### 1. Homepage Service Listings
```javascript
// Load all professionals for a service
fetchProfessionalsFromAPI('plumbing', 1);
```

### 2. Search Results Page
```javascript
// Apply multiple filters
currentFilters = {
    serviceType: 'electrical',
    rating: '4.0',
    region: 'centre',
    verified: true
};
applyFilters();
```

### 3. Filter Suggestions
```bash
# Get all available regions for a service
curl "http://localhost:8000/accounts/api/professionals/?service=hvac" \
  | grep available_regions
```

### 4. Pagination
```javascript
// Load next page with same filters
fetchProfessionalsFromAPI('plumbing', currentPage + 1);
```

## Performance Tips

1. **Use pagination** - Default 20 items, max 100
2. **Cache common filters** - Popular combinations can be cached
3. **Index database** - Add indexes to: service_type, state, rating, is_verified
4. **Defer fields** - service_description is deferred by default
5. **Monitor queries** - Should be 2-3 per request

## Testing

### Quick Test
```bash
# Start server
cd Django
python manage.py runserver

# Test API
curl "http://localhost:8000/accounts/api/professionals/?service=all"

# Test with filters
curl "http://localhost:8000/accounts/api/professionals/?service=plumbing&min_rating=4.0"
```

### Load Test
```bash
# Time the API response
time curl "http://localhost:8000/accounts/api/professionals/?service=all&limit=100"
```

### Shell Test
```bash
python manage.py shell

from accounts.filter_utils import ProfessionalFilter
pf = ProfessionalFilter()
pf.apply_service_filter('plumbing').apply_rating_filter(4.0)
print(f"Results: {pf.count()}")
```

## Response Structure

```json
{
  "success": true/false,
  "service": "service_type",
  "professionals": [
    { /* professional object */ }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "service_type": "plumbing",
    "min_rating": 4.0
  },
  "region_message": "Optional message if no region match",
  "available_regions": ["Region1", "Region2"]
}
```

## Professional Object Fields

```json
{
  "id": 1,
  "name": "Company Name",
  "company": "Full Company Name",
  "avatar": "/media/profiles/avatar.jpg",
  "service": "Service Display Name",
  "serviceType": "service_code",
  "rating": 4.8,
  "reviews": 127,
  "verified": true,
  "experience": 12,
  "price_range": "$$",
  "min_price": 75.00,
  "location": "City, State",
  "city": "City",
  "state": "State",
  "region": "State",
  "bio": "Professional bio",
  "phone": "+237123456789",
  "verified_badge": true
}
```

## Error Handling

### Missing Required Service
```json
{
  "success": false,
  "error": "service parameter is required"
}
```

### Invalid Service Type
```json
{
  "success": false,
  "error": "Invalid service type: xyz. Valid options are: all, plumbing, ..."
}
```

### Server Error
```json
{
  "success": false,
  "error": "Error processing filter: {error details}"
}
```

## Database Optimization

### Current Indexes (Recommended)
```python
# In models.py, add indexes
class Meta:
    indexes = [
        models.Index(fields=['service_type']),
        models.Index(fields=['state']),
        models.Index(fields=['rating']),
        models.Index(fields=['is_verified']),
    ]
```

### Query Example (Auto-optimized)
```sql
SELECT * FROM accounts_providerprofile
INNER JOIN auth_user ON ...
WHERE user.is_active = true
  AND service_type = 'plumbing'
  AND rating >= 4.0
ORDER BY rating DESC
LIMIT 20
```

## Deployment Checklist

- [ ] Database indexes created
- [ ] filter_utils.py deployed
- [ ] views.py updated
- [ ] URLs updated
- [ ] JavaScript updated
- [ ] Test API endpoint works
- [ ] Test with multiple filters
- [ ] Monitor response times
- [ ] Enable query logging if needed
- [ ] Set up rate limiting
- [ ] Update cache strategy if needed

## Support & Debugging

### Enable Query Logging
Add to settings.py:
```python
LOGGING = {
    'version': 1,
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

### Check Filter Application
API response includes `filters_applied` dict showing what was used.

### View Generated SQL
```python
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    # Run your filter code
    pf = ProfessionalFilter()
    pf.apply_service_filter('plumbing')
    
for query in ctx:
    print(query['sql'])
```

## Related Files

- Models: `accounts/models.py` (ProviderProfile)
- Forms: `accounts/forms.py`
- Templates: `accounts/templates/accounts/professionals_list.html`
- CSS: `static/css/professionals_list.css`
- Tests: `accounts/tests/` (if available)

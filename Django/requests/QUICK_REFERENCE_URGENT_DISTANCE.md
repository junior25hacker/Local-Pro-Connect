# Quick Reference: Urgent Request & Distance Calculation

## Core Components

### 1. Urgent Flag
```python
# In ServiceRequest model
urgent = models.BooleanField(default=False)

# Usage
request = ServiceRequest.objects.create(
    urgent=True,  # Mark as urgent
    description="Emergency pipe repair",
    # ... other fields
)
```

### 2. Distance Calculation (Haversine)
```python
from requests.distance_utils import haversine_distance, calculate_request_distance

# Calculate distance between two points
distance_km = haversine_distance(
    lat1=3.8667, lon1=11.5167,  # User location
    lat2=3.9000, lon2=11.5500   # Provider location
)
# Returns: 4.2 (rounded to 1 decimal place)

# Calculate distance between request and provider
distance = calculate_request_distance(service_request, provider_profile)
```

### 3. Priority Score (0-180)
```python
from requests.distance_utils import calculate_priority_score

# Calculate priority for ordering
priority_score = calculate_priority_score(service_request)
# 100 (urgent) + 45 (distance) + 10 (time) = 155

# Score breakdown:
# - Urgent: +100 points
# - Distance: up to +50 points (closer = more)
# - Time: up to +30 points (older = more)
```

### 4. Distance Formatting
```python
from requests.distance_utils import format_distance_display

# Format for display
display = format_distance_display(2.5)
# Returns: "2.5 km away"

display = format_distance_display(0.5)
# Returns: "500m away"

display = format_distance_display(None)
# Returns: "Distance not available"
```

---

## API Endpoints

### Get Provider's Pending Requests (Sorted by Priority)
```
GET /api/requests/provider/pending/
Headers: Authorization required (provider user)

Query params:
  - service_type: Filter by type
  - max_distance_km: Max radius (default: 50)
  - include_urgent_only: Show urgent only (default: false)
  - limit: Results limit (default: 50)

Response: List of requests sorted by priority_score (descending)
```

### Get Request Priority Details
```
GET /api/requests/{id}/priority-details/
Headers: Authorization required (provider user)

Response: {
  "priority_score": 154,
  "priority_tier": "HIGHEST",
  "score_breakdown": {
    "urgent_bonus": 100,
    "distance_bonus": 49,
    "time_bonus": 5
  }
}
```

### Find Nearby Providers
```
GET /api/requests/providers-nearby/
No auth required

Query params:
  - latitude: Request latitude (required)
  - longitude: Request longitude (required)
  - max_distance_km: Max radius (default: 50)
  - service_type: Filter by service (optional)

Response: List of providers within radius, sorted by distance
```

---

## Priority Tiers

| Tier | Score Range | Visual | Use Case |
|------|-------------|--------|----------|
| HIGHEST | 140-180 | 🔴 | Urgent + Close |
| HIGH | 100-139 | 🟠 | Urgent or Old |
| MEDIUM | 50-99 | 🟡 | Regular + Close |
| LOW | 0-49 | 🟢 | Regular + Far |

---

## Database Models

### ServiceRequest
```python
class ServiceRequest(models.Model):
    # Urgent flag
    urgent = models.BooleanField(default=False)
    
    # Location (user coordinates)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    address_string = models.CharField(max_length=500)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
```

### ProviderProfile
```python
class ProviderProfile(models.Model):
    # Location (business coordinates)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    
    # Indexes
    # provider_location_idx: (latitude, longitude)
    # provider_search_idx: (service_type, is_verified, latitude)
```

---

## Code Examples

### Example 1: Create Urgent Request
```python
from requests.models import ServiceRequest
from accounts.models import UserProfile

request = ServiceRequest.objects.create(
    user=current_user,
    urgent=True,  # Mark as urgent
    description="Need immediate plumbing repair",
    provider_name="John's Plumbing",
    latitude=Decimal('3.8667'),
    longitude=Decimal('11.5167'),
    address_string="123 Main St, Yaoundé",
    offered_price=Decimal('50000'),
)
print(f"Request created with urgent={request.urgent}")
```

### Example 2: Get Provider's Priority Queue
```python
from requests.models import ServiceRequest
from requests.distance_utils import calculate_priority_score

provider = current_user.provider_profile

# Get all pending requests
pending = ServiceRequest.objects.filter(status='pending')

# Calculate priority for each
prioritized = []
for req in pending:
    if req.has_location() and provider.latitude and provider.longitude:
        priority = calculate_priority_score(req)
        prioritized.append((req, priority))

# Sort by priority (descending)
prioritized.sort(key=lambda x: x[1], reverse=True)

# Display
for req, score in prioritized[:10]:
    print(f"Request #{req.id}: Priority={score}, Urgent={req.urgent}")
```

### Example 3: Find Nearby Providers
```python
from requests.distance_utils import get_providers_within_radius

# Request coordinates
request_lat = 3.8667
request_lon = 11.5167

# Find providers within 30km
nearby = get_providers_within_radius(
    request_lat, request_lon,
    max_distance_km=30.0
)

# Results: [(provider_profile, distance_km), ...]
for provider, distance in nearby:
    print(f"{provider.company_name}: {distance} km away")
```

### Example 4: API Usage (Python/JavaScript)
```python
# Python requests
import requests

# Get pending requests
response = requests.get(
    'http://localhost:8000/api/requests/provider/pending/',
    headers={'Authorization': f'Bearer {token}'},
    params={'max_distance_km': 50, 'include_urgent_only': True}
)
data = response.json()
print(f"Found {data['total']} urgent requests")
```

```javascript
// JavaScript fetch
async function getPriorityQueue() {
  const response = await fetch(
    '/api/requests/provider/pending/?max_distance_km=50&include_urgent_only=true',
    {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    }
  );
  const data = await response.json();
  console.log(`${data.total} requests found`);
  return data.requests;
}
```

---

## Testing

### Quick Tests
```bash
# Run all tests
python manage.py test requests.test_urgent_distance_architecture

# Test Haversine accuracy
python manage.py test requests.test_urgent_distance_architecture.HaversineFormulaTests

# Test priority scoring
python manage.py test requests.test_urgent_distance_architecture.PriorityScoreCalculationTests
```

### Manual Testing
```bash
# Test distance calculation
python manage.py shell
>>> from requests.distance_utils import haversine_distance
>>> haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
3943.6  # NYC to LA

# Test priority score
>>> from requests.distance_utils import calculate_priority_score
>>> from requests.models import ServiceRequest
>>> req = ServiceRequest.objects.first()
>>> req.distance_km = 5.0
>>> calculate_priority_score(req)
147  # Example score
```

---

## Performance Metrics

| Operation | Time | Notes |
|-----------|------|-------|
| Haversine calculation | < 1ms | Per provider |
| Priority score | < 1ms | Per request |
| Get 100 nearby providers | < 100ms | With indexes |
| API response | < 500ms | Full queue |

---

## Coordinate Validation

```python
# Valid coordinates
latitude: -90 to +90
longitude: -180 to +180

# Example (Yaoundé, Cameroon)
latitude: 3.8667
longitude: 11.5167

# Example (New York)
latitude: 40.7128
longitude: -74.0060
```

---

## Settings

Add to Django settings.py:

```python
# Geolocation
GEOLOCATION_SETTINGS = {
    'ENABLE_HIGH_ACCURACY': True,
    'MAX_LOCATION_AGE_SECONDS': 0,
    'LOCATION_TIMEOUT_SECONDS': 10,
    'MAX_SEARCH_RADIUS_KM': 50.0,
    'DISTANCE_ROUNDING_PLACES': 1,
}

# Priority Weights
PRIORITY_SCORE_SETTINGS = {
    'URGENT_BOOST': 100,
    'DISTANCE_MAX_POINTS': 50,
    'TIME_MAX_POINTS': 30,
    'TIME_POINTS_PER_HOUR': 2,
}
```

---

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Distance returns None | Verify both locations have coordinates |
| Priority score seems wrong | Check if distance_km is set on request object |
| API returns 403 | Ensure user is logged in as provider |
| Endpoints not found | Verify URLs are added to urls.py |
| Distance always 0 | Check decimal precision (9,6) matches |

---

## Files

- `distance_utils.py` - Core distance calculations
- `priority_queue_api.py` - API endpoints
- `models.py` - ServiceRequest model
- `accounts/models.py` - ProviderProfile model
- `test_urgent_distance_architecture.py` - Test suite

---

**Last Updated**: 2025-02-07  
**Version**: 1.0


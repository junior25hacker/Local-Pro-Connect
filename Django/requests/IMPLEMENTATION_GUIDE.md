# Implementation Guide: Urgent Request Logic & Distance Calculation

## Quick Start

This guide walks through implementing the urgent request and distance calculation system in your Django project.

---

## 1. Database Migrations

### Step 1: Add Location Indexes

Run the database migration to add indexes for location fields:

```bash
cd Django
python manage.py migrate accounts
```

This creates three indexes:
- `provider_location_idx`: On (latitude, longitude) - speeds up radius queries
- `provider_search_idx`: On (service_type, is_verified, latitude) - optimizes filtered searches
- `provider_user_location_idx`: On (user, latitude, longitude) - for user-provider lookups

---

## 2. API Endpoint Integration

### New Endpoints Available

**1. Provider Pending Requests Queue**
```
GET /api/requests/provider/pending/
```

Returns all pending service requests ordered by priority score.

**Query Parameters:**
```
- service_type: Filter by service type (optional)
- max_distance_km: Maximum distance (default: 50)
- include_urgent_only: Show only urgent requests (default: false)
- limit: Number of results (default: 50, max: 200)
```

**Response:**
```json
{
  "success": true,
  "requests": [
    {
      "id": 1,
      "description": "Urgent pipe repair",
      "urgent": true,
      "distance_km": 2.5,
      "distance_display": "2.5 km away",
      "offered_price": 50000,
      "priority_score": 154,
      "priority_tier": "HIGHEST",
      "created_at": "2025-02-07T10:30:00Z",
      "user": {
        "id": 5,
        "name": "John Doe",
        "phone": "+237123456789"
      },
      "photos": [...]
    }
  ],
  "total": 12,
  "summary": {
    "urgent_count": 2,
    "regular_count": 10,
    "avg_distance_km": 15.3
  }
}
```

**Example Usage:**
```bash
# Get urgent requests within 30 km
curl "http://localhost:8000/api/requests/provider/pending/?include_urgent_only=true&max_distance_km=30"

# Get all plumbing requests
curl "http://localhost:8000/api/requests/provider/pending/?service_type=plumbing&limit=100"
```

---

**2. Request Priority Details**
```
GET /api/requests/{id}/priority-details/
```

Returns detailed priority score breakdown for a specific request.

**Response:**
```json
{
  "success": true,
  "request_id": 1,
  "priority_score": 154,
  "priority_tier": "HIGHEST",
  "score_breakdown": {
    "urgent_bonus": 100,
    "distance_bonus": 49,
    "time_bonus": 5,
    "total": 154
  },
  "factors": {
    "is_urgent": true,
    "distance_km": 2.5,
    "distance_display": "2.5 km away",
    "hours_old": 0.5,
    "created_at": "2025-02-07T10:30:00Z"
  }
}
```

---

**3. Nearby Providers**
```
GET /api/requests/providers-nearby/
```

Find providers within specified radius of a location.

**Query Parameters:**
```
- latitude: Request latitude (required)
- longitude: Request longitude (required)
- max_distance_km: Maximum distance (default: 50)
- service_type: Filter by service type (optional)
```

**Response:**
```json
{
  "success": true,
  "providers": [
    {
      "provider_id": 3,
      "user_id": 4,
      "company_name": "John's Plumbing",
      "distance_km": 2.5,
      "distance_display": "2.5 km away",
      "rating": 4.8,
      "total_reviews": 45,
      "service_type": "Plumbing",
      "phone": "+237123456789",
      "min_price": 25000,
      "years_experience": 5,
      "is_verified": true
    }
  ],
  "total": 5,
  "center": {
    "latitude": 3.8667,
    "longitude": 11.5167
  }
}
```

---

## 3. Frontend Integration

### HTML Form for Urgent Flag

```html
<div class="form-group">
  <label for="urgent-toggle" class="form-label">
    <input 
      type="checkbox" 
      id="urgent-toggle" 
      name="urgent" 
      class="form-check-input urgent-toggle"
    >
    <span class="form-label-text">Mark as Urgent</span>
  </label>
  <small class="form-text text-muted d-block mt-2">
    Urgent requests appear higher in provider queues and typically receive faster responses.
  </small>
</div>
```

### CSS Styling for Urgent Requests

```css
/* Urgent request styling */
.urgent-request {
  border-left: 4px solid #dc3545;
  background-color: #fff5f5;
}

.urgent-badge {
  display: inline-block;
  padding: 4px 8px;
  background-color: #dc3545;
  color: white;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-right: 8px;
}

.priority-badge {
  display: inline-block;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: bold;
}

.priority-highest {
  background-color: #dc3545;
  color: white;
}

.priority-high {
  background-color: #fd7e14;
  color: white;
}

.priority-medium {
  background-color: #ffc107;
  color: #333;
}

.priority-low {
  background-color: #e9ecef;
  color: #666;
}

.distance-badge {
  font-size: 13px;
  color: #666;
  font-weight: 500;
}
```

### JavaScript for Priority Queue Display

```javascript
// Fetch and display provider's pending requests
async function loadPriorityQueue() {
  try {
    const response = await fetch('/api/requests/provider/pending/?limit=50', {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    });
    
    const data = await response.json();
    
    if (data.success) {
      displayRequests(data.requests, data.summary);
    } else {
      console.error('Error:', data.error);
    }
  } catch (error) {
    console.error('Fetch error:', error);
  }
}

function displayRequests(requests, summary) {
  const container = document.getElementById('requests-container');
  container.innerHTML = '';
  
  // Display summary
  const summaryHtml = `
    <div class="summary-box">
      <span>Total: ${requests.length}</span>
      <span class="urgent">🔴 Urgent: ${summary.urgent_count}</span>
      <span>Average Distance: ${summary.avg_distance_km} km</span>
    </div>
  `;
  container.innerHTML += summaryHtml;
  
  // Display requests
  requests.forEach(request => {
    const priorityClass = `priority-${request.priority_tier.toLowerCase()}`;
    const urgentBadge = request.urgent ? '<span class="urgent-badge">🔴 URGENT</span>' : '';
    
    const html = `
      <div class="request-card ${request.urgent ? 'urgent-request' : ''}">
        <div class="request-header">
          ${urgentBadge}
          <span class="priority-badge ${priorityClass}">${request.priority_tier}</span>
          <span class="distance-badge">${request.distance_display}</span>
        </div>
        <div class="request-body">
          <p class="description">${request.description}</p>
          <p class="user-info">
            <strong>${request.user.name}</strong> - ${request.user.phone}
          </p>
        </div>
        <div class="request-footer">
          <span class="price">$${request.offered_price}</span>
          <span class="priority-score">Score: ${request.priority_score}</span>
          <button class="btn-view" onclick="viewRequest(${request.id})">View</button>
        </div>
      </div>
    `;
    
    container.innerHTML += html;
  });
}

// Get nearby providers for a request
async function loadNearbyProviders(latitude, longitude) {
  try {
    const response = await fetch(
      `/api/requests/providers-nearby/?latitude=${latitude}&longitude=${longitude}&max_distance_km=30`,
      {
        headers: {
          'X-Requested-With': 'XMLHttpRequest'
        }
      }
    );
    
    const data = await response.json();
    
    if (data.success) {
      displayProviders(data.providers);
    }
  } catch (error) {
    console.error('Error loading providers:', error);
  }
}

function displayProviders(providers) {
  const container = document.getElementById('providers-map');
  
  providers.forEach(provider => {
    const html = `
      <div class="provider-card">
        <h4>${provider.company_name}</h4>
        <p>${provider.distance_display}</p>
        <p>Rating: ${provider.rating} ⭐</p>
        <p>Min Price: $${provider.min_price}</p>
        <button onclick="selectProvider(${provider.provider_id})">Select</button>
      </div>
    `;
    
    container.innerHTML += html;
  });
}

// Load queue on page load
document.addEventListener('DOMContentLoaded', loadPriorityQueue);
```

---

## 4. Testing

### Run Tests

```bash
cd Django
python manage.py test requests.test_urgent_distance_architecture
```

### Specific Test Classes

```bash
# Test Haversine formula
python manage.py test requests.test_urgent_distance_architecture.HaversineFormulaTests

# Test distance calculations
python manage.py test requests.test_urgent_distance_architecture.DistanceCalculationTests

# Test priority scoring
python manage.py test requests.test_urgent_distance_architecture.PriorityScoreCalculationTests

# Test API endpoints
python manage.py test requests.test_urgent_distance_architecture.APIEndpointTests
```

### Manual Testing with curl

```bash
# Get provider's pending requests (requires authentication)
curl -b cookies.txt http://localhost:8000/api/requests/provider/pending/

# Get nearby providers
curl "http://localhost:8000/api/requests/providers-nearby/?latitude=3.8667&longitude=11.5167&max_distance_km=50"

# Get priority details for specific request
curl -b cookies.txt http://localhost:8000/api/requests/1/priority-details/
```

---

## 5. Configuration

Add to `Django/locapro_project/settings.py`:

```python
# Geolocation and Distance Calculation Settings
GEOLOCATION_SETTINGS = {
    'ENABLE_HIGH_ACCURACY': True,
    'MAX_LOCATION_AGE_SECONDS': 0,
    'LOCATION_TIMEOUT_SECONDS': 10,
    'MAX_SEARCH_RADIUS_KM': 50.0,
    'DISTANCE_ROUNDING_PLACES': 1,
}

# Priority Score Weights
PRIORITY_SCORE_SETTINGS = {
    'URGENT_BOOST': 100,
    'DISTANCE_MAX_POINTS': 50,
    'TIME_MAX_POINTS': 30,
    'TIME_POINTS_PER_HOUR': 2,
}

# Logging for monitoring
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'logs/distance_calculations.log',
        },
    },
    'loggers': {
        'requests.priority_queue_api': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

---

## 6. Performance Optimization Tips

### 1. Query Optimization
Use `select_related()` and `prefetch_related()`:

```python
requests = ServiceRequest.objects.filter(
    status='pending'
).select_related(
    'user',
    'user__user_profile',
    'price_range'
).prefetch_related('photos')[:50]
```

### 2. Caching Priority Scores
```python
from django.views.decorators.cache import cache_page

@cache_page(60)  # Cache for 60 seconds
@login_required
def api_provider_pending_requests(request):
    # ... implementation
```

### 3. Batch Distance Calculations
```python
# Calculate distances in batch instead of per-request
providers_with_distance = [
    (provider, haversine_distance(
        request_lat, request_lon,
        float(provider.latitude), float(provider.longitude)
    ))
    for provider in providers
]
```

### 4. Database Indexes
The migration automatically creates optimal indexes:
```sql
CREATE INDEX provider_location_idx ON accounts_providerprofile(latitude, longitude);
CREATE INDEX provider_search_idx ON accounts_providerprofile(service_type, is_verified, latitude);
```

---

## 7. Troubleshooting

### Issue: "Provider location not set"
**Solution**: Update provider profile with latitude/longitude
```bash
python manage.py shell
>>> from accounts.models import ProviderProfile
>>> provider = ProviderProfile.objects.first()
>>> provider.latitude = 3.8667
>>> provider.longitude = 11.5167
>>> provider.save()
```

### Issue: Distance calculations showing None
**Solution**: Verify both request and provider have coordinates
```bash
python manage.py shell
>>> from requests.models import ServiceRequest
>>> req = ServiceRequest.objects.get(id=1)
>>> req.has_location()  # Should return True
True
```

### Issue: Priority queue API returning 403
**Solution**: Ensure user is logged in as provider
```bash
# Login first
curl -c cookies.txt -d "username=provider&password=pass" \
  http://localhost:8000/accounts/login/

# Then use cookies
curl -b cookies.txt http://localhost:8000/api/requests/provider/pending/
```

---

## 8. Next Steps

1. **Deploy Database Migration**
   ```bash
   python manage.py migrate accounts
   ```

2. **Update Frontend Templates**
   - Add urgent checkbox to request creation form
   - Display priority badges in request lists
   - Show distance on provider profiles

3. **Test End-to-End**
   - Create urgent request
   - Verify it appears higher in provider queue
   - Check priority score calculation

4. **Monitor Performance**
   - Log distance calculations
   - Track API response times
   - Monitor database query performance

5. **Gather User Feedback**
   - Are urgent requests getting faster responses?
   - Is distance calculation accurate?
   - Are providers satisfied with priority ordering?

---

## 9. Support & Documentation

- **Architecture Doc**: `URGENT_REQUEST_DISTANCE_ARCHITECTURE.md`
- **Distance Utils**: `distance_utils.py` 
- **Priority Queue API**: `priority_queue_api.py`
- **Tests**: `test_urgent_distance_architecture.py`

---

**Version**: 1.0  
**Last Updated**: 2025-02-07


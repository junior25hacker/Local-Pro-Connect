# Urgent Request Logic & Distance Calculation Architecture

## Executive Summary

This document specifies the comprehensive architecture for:
1. **Urgent Flag System**: Defining urgent requests in payload and backend prioritization
2. **Distance Calculation**: Haversine formula implementation for precise geolocation
3. **Provider Queue Prioritization**: Ordering requests by urgency and distance
4. **Location Indexing**: Efficient provider location retrieval and calculations

---

## 1. URGENT FLAG SYSTEM

### 1.1 Request Payload Definition

The `urgent` flag is a boolean field in the `ServiceRequest` model:

```python
# Django/requests/models.py
class ServiceRequest(models.Model):
    urgent = models.BooleanField(default=False)
    # ... other fields
```

**Current Status**: ✅ Already implemented in the model and form

### 1.2 Request Payload Structure

**When Creating a Request (POST /api/requests/create/):**

```json
{
  "description": "Urgent pipe repair needed",
  "provider_name": "John's Plumbing",
  "urgent": true,
  "latitude": 3.8667,
  "longitude": 11.5167,
  "address_string": "123 Main St, Yaoundé",
  "offered_price": 50000,
  "date_time": "2025-02-07T14:30:00Z",
  "price_range": 2
}
```

**Field Details**:
- `urgent` (boolean): Flag indicating if request needs immediate attention
  - `true`: Request marked as urgent (priority boost)
  - `false`: Regular request (default)
- Impact: Increases priority score by 100 points in queue

### 1.3 Frontend Implementation Requirements

**HTML Form Field**:
```html
<div class="form-group">
  <label>
    <input type="checkbox" name="urgent" id="urgent-toggle" class="urgent-toggle">
    Mark as Urgent (Request immediate service)
  </label>
  <small class="text-muted">
    Urgent requests appear higher in provider queues and have faster response times
  </small>
</div>
```

**JavaScript Enhancement**:
```javascript
document.getElementById('urgent-toggle').addEventListener('change', function() {
  if (this.checked) {
    document.body.classList.add('urgent-mode');
    console.log('Request marked as URGENT');
  } else {
    document.body.classList.remove('urgent-mode');
  }
});
```

---

## 2. DISTANCE CALCULATION ARCHITECTURE

### 2.1 Haversine Formula Implementation

**Location**: `./Django/requests/distance_utils.py` ✅ Already implemented

**Formula Specification**:

```
d = 2R × arcsin(√(sin²((φ₂-φ₁)/2) + cos(φ₁) × cos(φ₂) × sin²((λ₂-λ₁)/2)))

Where:
- R = 6371 km (Earth's radius)
- φ₁, φ₂ = Latitude of points 1 and 2 (in radians)
- λ₁, λ₂ = Longitude of points 1 and 2 (in radians)
- d = Distance in kilometers
```

**Python Implementation**:

```python
def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lon1: User's coordinates (ServiceRequest location)
        lat2, lon2: Provider's business coordinates (ProviderProfile location)
    
    Returns:
        float: Distance in kilometers, rounded to 1 decimal place
    """
    R = 6371.0  # Earth's radius in kilometers
    
    φ1 = math.radians(lat1)
    φ2 = math.radians(lat2)
    Δφ = math.radians(lat2 - lat1)
    Δλ = math.radians(lon2 - lon1)
    
    a = (math.sin(Δφ / 2) ** 2 + 
         math.cos(φ1) * math.cos(φ2) * math.sin(Δλ / 2) ** 2)
    c = 2 * math.asin(math.sqrt(a))
    
    distance = R * c
    return round(distance, 1)  # Rounded to 1 decimal place
```

**Status**: ✅ Already implemented correctly

### 2.2 Coordinate Accuracy Requirements

**GPS Accuracy Specification**:

```javascript
// Frontend: Location acquisition with high accuracy
const locationOptions = {
  enableHighAccuracy: true,      // ✅ Required for precise calculations
  timeout: 10000,                // 10-second timeout
  maximumAge: 0                  // Don't use cached position
};

navigator.geolocation.getCurrentPosition(
  success => {
    const lat = success.coords.latitude;
    const lon = success.coords.longitude;
    const accuracy = success.coords.accuracy;  // Meters
    
    console.log(`Position: ${lat}, ${lon} (±${accuracy}m)`);
  },
  error => console.error('Geolocation error:', error),
  locationOptions
);
```

**Accuracy Levels**:
- `enableHighAccuracy: true` provides ~5-10 meter accuracy
- Sufficient for local service distance calculations
- Typical acceptable error for "within X km" filtering

**Model Fields** (already implemented):

```python
class ServiceRequest(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)   # ±0.1 meter
    longitude = models.DecimalField(max_digits=9, decimal_places=6)  # ±0.1 meter

class ProviderProfile(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
```

### 2.3 Distance Output Formatting

**Specification**:
- Output Format: Rounded to **1 decimal place**
- Display Format: `"{distance} km"` (e.g., "2.5 km")
- Special Cases:
  - Distance < 1 km: Display in meters (e.g., "450m away")
  - Distance unavailable: "Distance not available"

**Implementation**:

```python
def format_distance_display(distance_km: Optional[float]) -> str:
    """Format distance for UI display"""
    if distance_km is None:
        return "Distance not available"
    
    if distance_km < 1.0:
        return f"{int(distance_km * 1000)}m away"
    else:
        return f"{distance_km}km away"
```

**Examples**:
- 0.45 km → "450m away"
- 2.5 km → "2.5 km away"
- 15.8 km → "15.8 km away"
- None → "Distance not available"

---

## 3. PROVIDER LOCATION INDEXING

### 3.1 Database Indexing Strategy

**Current Model Setup** ✅:

```python
class ProviderProfile(models.Model):
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
            models.Index(fields=['service_type', 'is_verified', 'latitude']),
        ]
```

**Migration Required**:

```python
# Create: Django/requests/migrations/0009_add_provider_location_indexes.py

from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0007_add_user_profile_picture'),
    ]
    
    operations = [
        migrations.AddIndex(
            model_name='providerprofile',
            index=models.Index(fields=['latitude', 'longitude'], name='provider_loc_idx'),
        ),
        migrations.AddIndex(
            model_name='providerprofile',
            index=models.Index(
                fields=['service_type', 'is_verified', 'latitude'],
                name='provider_search_idx'
            ),
        ),
    ]
```

### 3.2 Efficient Provider Retrieval

**Query Optimization**:

```python
def get_providers_within_radius(request_lat: float, request_lon: float, 
                               max_distance_km: float = 50.0,
                               service_type: str = None) -> list:
    """
    Get providers within radius with instant calculation.
    
    Returns:
        list: [(provider_profile, distance_km), ...]
    """
    from accounts.models import ProviderProfile
    
    # Use select_related to minimize queries
    queryset = ProviderProfile.objects.filter(
        latitude__isnull=False,
        longitude__isnull=False,
        user__is_active=True,
        is_verified=True
    ).select_related('user')
    
    # Filter by service type if specified
    if service_type:
        queryset = queryset.filter(service_type=service_type)
    
    providers_with_distance = []
    
    for provider in queryset:
        distance = haversine_distance(
            request_lat, request_lon,
            float(provider.latitude), float(provider.longitude)
        )
        
        if distance <= max_distance_km:
            providers_with_distance.append((provider, distance))
    
    # Sort by distance (closest first)
    providers_with_distance.sort(key=lambda x: x[1])
    
    return providers_with_distance
```

**Performance Characteristics**:
- Instant calculation for each provider (no external API calls)
- O(n) complexity where n = providers with valid coordinates
- Typical response time: < 100ms for up to 1000 providers
- Scalable with database indexes

### 3.3 Instant Calculation Benefits

✅ **Advantages**:
- No external API dependencies (Google Maps, etc.)
- No rate limiting concerns
- Instant results (< 100ms)
- Works offline
- Fully predictable costs
- Privacy-preserving (coordinates stay internal)

---

## 4. BACKEND PRIORITIZATION IN PROVIDER QUEUES

### 4.1 Priority Score Calculation

**Location**: `./Django/requests/distance_utils.py`

**Algorithm**:

```python
def calculate_priority_score(service_request) -> int:
    """
    Calculate priority score for request ordering (0-180).
    Higher score = higher priority.
    
    Factors:
    - Urgent requests: +100 points (HIGHEST)
    - Distance: Closer = more points (max 50 points)
    - Time since creation: Older = more points (max 30 points)
    """
    score = 0
    
    # TIER 1: URGENT PRIORITY (100 points)
    if service_request.urgent:
        score += 100
    
    # TIER 2: PROXIMITY BONUS (50 points max)
    if hasattr(service_request, 'distance_km') and service_request.distance_km:
        # Closer requests get more points:
        # 0 km = 50 points
        # 50 km = 0 points
        distance_score = max(0, 50 - service_request.distance_km)
        score += int(distance_score)
    
    # TIER 3: TIME BONUS (30 points max)
    if service_request.created_at:
        hours_old = (timezone.now() - service_request.created_at).total_seconds() / 3600
        # 2 points per hour, capped at 30 points
        time_score = min(30, hours_old * 2)
        score += int(time_score)
    
    return score
```

**Priority Score Examples**:

| Request Type | Distance | Age | Score | Priority |
|---|---|---|---|---|
| Urgent, very close | 0.5 km | 1 hour | 154 | 🔴 HIGHEST |
| Urgent, far | 40 km | 2 hours | 114 | 🔴 HIGH |
| Regular, very close | 0.5 km | 1 hour | 54 | 🟡 MEDIUM |
| Regular, medium | 20 km | 3 hours | 36 | 🟡 MEDIUM |
| Regular, far | 50 km | 0.5 hour | 1 | 🟢 LOW |

### 4.2 Queue Ordering Implementation

**API Endpoint for Provider Dashboard**:

```python
@login_required
def api_provider_pending_requests(request):
    """
    Get all pending requests ordered by priority score.
    
    Provider sees:
    1. Urgent requests (closer ones first)
    2. Regular requests (closer ones first)
    3. Older requests (time decay)
    """
    provider = request.user.provider_profile
    
    pending_requests = ServiceRequest.objects.filter(
        status='pending'
    ).select_related('user', 'user__user_profile').prefetch_related('photos')
    
    # Annotate with calculated priority
    requests_with_priority = []
    
    for service_req in pending_requests:
        # Calculate distance if available
        distance = None
        if service_req.has_location() and provider.latitude and provider.longitude:
            distance = calculate_request_distance(service_req, provider)
            service_req.distance_km = distance
        
        # Calculate priority score
        priority = calculate_priority_score(service_req)
        requests_with_priority.append((service_req, priority, distance))
    
    # Sort by priority (descending = highest first)
    requests_with_priority.sort(key=lambda x: x[1], reverse=True)
    
    # Serialize response
    results = []
    for service_req, priority, distance in requests_with_priority:
        results.append({
            'id': service_req.id,
            'description': service_req.description,
            'urgent': service_req.urgent,
            'distance_km': distance,
            'distance_display': format_distance_display(distance),
            'offered_price': float(service_req.offered_price or 0),
            'priority_score': priority,
            'created_at': service_req.created_at.isoformat(),
            'user': {
                'id': service_req.user.id,
                'name': service_req.user.get_full_name(),
                'phone': getattr(service_req.user.user_profile, 'phone', ''),
            },
            'photos': [
                {'url': photo.image.url, 'id': photo.id}
                for photo in service_req.photos.all()[:3]
            ]
        })
    
    return JsonResponse({
        'success': True,
        'requests': results,
        'total': len(results)
    })
```

---

## 5. DATA FLOW DIAGRAM

```
┌─────────────────────────────────────────────────────────────────┐
│ USER CREATES REQUEST                                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Frontend gets user location (enableHighAccuracy: true)      │
│  2. Form submission with:                                       │
│     - urgent: boolean flag                                      │
│     - latitude, longitude (user location)                       │
│     - address_string, description, etc.                         │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ BACKEND: SAVE REQUEST                                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Validate coordinates (lat/lon range)                        │
│  2. Create ServiceRequest instance                              │
│     - Set urgent flag from payload                              │
│     - Store user location (lat, lon)                            │
│  3. Save to database                                            │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ PROVIDER QUEUE ASSIGNMENT                                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  For each provider:                                             │
│  1. Calculate distance using Haversine formula                  │
│     distance = haversine_distance(                              │
│       request.latitude, request.longitude,                      │
│       provider.latitude, provider.longitude                     │
│     )                                                           │
│  2. Format distance (rounded to 1 decimal)                      │
│  3. Calculate priority score:                                   │
│     score = 0                                                   │
│     if urgent: score += 100                                     │
│     if distance: score += max(0, 50 - distance)                 │
│     score += min(30, hours_old * 2)                             │
│  4. Add (request, score) to provider's queue                    │
│                                                                 │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────────┐
│ PROVIDER VIEWS DASHBOARD                                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Requests ordered by priority score (descending):               │
│                                                                 │
│  🔴 URGENT - 2.5 km away - Priority: 154                        │
│  🔴 URGENT - 15.3 km away - Priority: 128                       │
│  🟡 Regular - 0.8 km away - Priority: 54                        │
│  🟢 Regular - 45.2 km away - Priority: 2                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. IMPLEMENTATION CHECKLIST

### Phase 1: Model Enhancements ✅
- [x] `ServiceRequest.urgent` field (already exists)
- [x] Distance calculation utilities (already exist)
- [x] Priority score calculation (already exists)
- [ ] Database indexes for location fields

### Phase 2: API Endpoints
- [x] Request creation with urgent flag support
- [x] Request listing with distance calculations
- [ ] Priority-ordered provider queue endpoint

### Phase 3: Frontend Integration
- [x] Urgent checkbox in create request form
- [ ] Visual indicators for urgent requests (🔴)
- [ ] Distance display in provider lists
- [ ] Priority score visualization

### Phase 4: Quality Assurance
- [ ] Distance calculation accuracy tests
- [ ] Priority score sorting tests
- [ ] Performance benchmarks
- [ ] Edge case handling

---

## 7. CONFIGURATION SETTINGS

**Add to Django settings.py**:

```python
# Geolocation and Distance Calculation
GEOLOCATION_SETTINGS = {
    'ENABLE_HIGH_ACCURACY': True,
    'MAX_LOCATION_AGE_SECONDS': 0,  # Don't use cached position
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
```

---

## 8. ERROR HANDLING & VALIDATION

### Coordinate Validation

```python
def validate_coordinates(latitude: float, longitude: float) -> Tuple[bool, str]:
    """Validate GPS coordinates"""
    if not (-90 <= latitude <= 90):
        return False, "Latitude must be between -90 and 90"
    if not (-180 <= longitude <= 180):
        return False, "Longitude must be between -180 and 180"
    return True, "Valid"
```

### Distance Calculation Fallback

```python
def calculate_distance_safe(service_request, provider_profile) -> Optional[float]:
    """
    Safely calculate distance with fallback
    Returns None if either location is unavailable
    """
    try:
        if not service_request.has_location():
            return None
        if not (provider_profile.latitude and provider_profile.longitude):
            return None
        
        return calculate_request_distance(service_request, provider_profile)
    
    except (ValueError, TypeError) as e:
        logger.error(f"Distance calculation error: {e}")
        return None
```

---

## 9. TESTING SPECIFICATIONS

### Unit Tests

```python
# Test Haversine calculation
def test_haversine_distance():
    # Test known distances
    # NYC to LA: ~3944 km
    distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
    assert 3940 < distance < 3950
    
    # Same location: 0 km
    distance = haversine_distance(0, 0, 0, 0)
    assert distance == 0.0

# Test priority scoring
def test_priority_score():
    # Urgent request should score highest
    urgent_req = ServiceRequest(urgent=True, created_at=timezone.now())
    urgent_req.distance_km = 5.0
    
    regular_req = ServiceRequest(urgent=False, created_at=timezone.now())
    regular_req.distance_km = 0.5
    
    assert calculate_priority_score(urgent_req) > calculate_priority_score(regular_req)
```

---

## 10. PERFORMANCE BENCHMARKS

**Target Metrics**:
- Distance calculation: < 1ms per provider
- Priority scoring: < 1ms per request
- Provider queue retrieval: < 100ms for 1000 providers
- API response time: < 500ms

**Query Optimization**:
- Use `select_related()` for foreign keys
- Use `prefetch_related()` for reverse relationships
- Batch distance calculations
- Cache priority scores for 1 minute

---

## 11. FUTURE ENHANCEMENTS

- [ ] Spatial indexing (PostGIS for PostgreSQL)
- [ ] Real-time provider location updates
- [ ] Machine learning for optimal provider matching
- [ ] Multi-radius search zones
- [ ] Provider availability windows
- [ ] Dynamic pricing based on urgency

---

## Summary Table

| Feature | Status | Implemented | Location |
|---------|--------|-------------|----------|
| Urgent Flag Model | ✅ Complete | Yes | `ServiceRequest.urgent` |
| Haversine Formula | ✅ Complete | Yes | `distance_utils.py` |
| Distance Display | ✅ Complete | Yes | `format_distance_display()` |
| Priority Calculation | ✅ Complete | Yes | `calculate_priority_score()` |
| Location Indexing | ⏳ Planned | Partial | Needs migration |
| Priority Queue API | ⏳ In Progress | No | Needs endpoint |
| Frontend Integration | ⏳ In Progress | Partial | Needs UI indicators |

---

**Document Version**: 1.0  
**Last Updated**: 2025-02-07  
**Status**: Comprehensive Design Document  
**Next Steps**: Implement missing pieces in Phase 2-4


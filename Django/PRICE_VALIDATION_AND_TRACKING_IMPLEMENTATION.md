# Price Validation & Live Provider Tracking - Implementation Guide

## Overview

This document describes the implementation of two new features:
1. **Price Validation** - Ensures offered prices meet provider minimums
2. **Live Provider Tracking** - Returns provider location for accepted requests

---

## Feature 1: Price Validation

### Description
Validates that when a user submits a request with an `offered_price`, it must be greater than or equal to the provider's `min_price`.

### Implementation

#### Database Changes
- **ProviderProfile Model** - Added field:
  ```python
  min_price = models.DecimalField(max_digits=10, decimal_places=2, default=50.00)
  ```

- **ServiceRequest Model** - Added field:
  ```python
  offered_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
  ```

#### Form Validation
Location: `Django/requests/forms.py`

The `ServiceRequestForm.clean()` method validates:
```python
if provider_choice and offered_price is not None:
    provider_min_price = provider_choice.min_price
    if offered_price < provider_min_price:
        raise ValidationError("The offered price is below the minimum required...")
```

### Usage

#### Creating a Request with Price Validation
```python
from requests.forms import ServiceRequestForm

form_data = {
    'provider_choice': provider_id,
    'description': 'Fix leaking pipe',
    'offered_price': '100.00',  # Must be >= provider.min_price
    'urgent': False,
}

form = ServiceRequestForm(data=form_data)
if form.is_valid():
    service_request = form.save(commit=False)
    service_request.user = request.user
    service_request.save()
else:
    # Handle validation errors
    print(form.errors)
```

#### Error Messages
If validation fails, users see:
```
The offered price ($50.00) is below the minimum required by 
[Provider Name] ($75.00). Please offer at least $75.00 or 
select a different provider.
```

### Testing
```bash
cd Django
python manage.py shell

# Test the validation
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile

provider = ProviderProfile.objects.first()
form = ServiceRequestForm(data={
    'provider_choice': provider.id,
    'description': 'Test',
    'offered_price': '25.00'  # Below minimum
})
print(form.is_valid())  # False
print(form.errors)
```

---

## Feature 2: Live Provider Tracking

### Description
Returns the provider's current location for accepted requests. Only the request owner can access this data.

### Implementation

#### Database Changes
- **ProviderProfile Model** - Added fields:
  ```python
  latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
  longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
  ```

#### API Endpoint
- **URL**: `/requests/<request_id>/tracking/`
- **Method**: GET
- **Authentication**: Required (login_required)
- **Authorization**: Only request owner can access

Location: `Django/requests/views.py` - `live_provider_tracking()`

#### Response Format

**Success Response (200 OK):**
```json
{
    "success": true,
    "provider_id": 123,
    "provider_name": "John's Plumbing",
    "latitude": 40.7589,
    "longitude": -73.9851,
    "eta_minutes": 15,
    "last_updated": "2025-01-07T14:30:00Z",
    "provider_phone": "555-1234"
}
```

**Error Responses:**

1. **Unauthorized (403):**
```json
{
    "success": false,
    "error": "You do not have permission to track this provider.",
    "error_code": "UNAUTHORIZED"
}
```

2. **Request Not Accepted (400):**
```json
{
    "success": false,
    "error": "This request has not been accepted yet...",
    "error_code": "REQUEST_NOT_ACCEPTED"
}
```

3. **Location Not Available (400):**
```json
{
    "success": false,
    "error": "Provider location is not available at this time...",
    "error_code": "LOCATION_NOT_AVAILABLE"
}
```

4. **No Provider (400):**
```json
{
    "success": false,
    "error": "No provider assigned to this request.",
    "error_code": "NO_PROVIDER"
}
```

### Usage

#### JavaScript Example
```javascript
// Fetch provider location
async function trackProvider(requestId) {
    try {
        const response = await fetch(`/requests/${requestId}/tracking/`);
        const data = await response.json();
        
        if (data.success) {
            // Display on map
            displayProviderOnMap(data.latitude, data.longitude);
            showETA(data.eta_minutes);
        } else {
            console.error('Tracking error:', data.error);
        }
    } catch (error) {
        console.error('Failed to fetch location:', error);
    }
}

// Update location every 30 seconds
setInterval(() => trackProvider(requestId), 30000);
```

#### Python Example
```python
from django.test import Client

client = Client()
client.login(username='testuser', password='password')

response = client.get('/requests/1/tracking/')
data = response.json()

if data['success']:
    print(f"Provider at: {data['latitude']}, {data['longitude']}")
    print(f"ETA: {data['eta_minutes']} minutes")
```

### Updating Provider Location

Providers can update their location (to be implemented in provider app):
```python
# In provider's mobile app or dashboard
provider_profile = request.user.provider_profile
provider_profile.latitude = current_latitude
provider_profile.longitude = current_longitude
provider_profile.save()
```

### ETA Calculation

The endpoint calculates ETA using the Haversine formula:
- Calculates distance between provider and user
- Assumes average speed of 30 km/h
- Adds 5-minute buffer for traffic/stops
- Minimum ETA is 5 minutes

For production, integrate with:
- Google Maps Distance Matrix API
- Mapbox Directions API
- Real-time traffic data

---

## Security Considerations

### Price Validation
✅ Server-side validation (cannot be bypassed)  
✅ Clear error messages  
✅ No SQL injection risks  
✅ Works with existing authentication

### Live Tracking
✅ Only request owner can access location  
✅ Only works for accepted requests  
✅ Provider must explicitly share location  
✅ HTTPS recommended for production  
✅ Rate limiting recommended (prevent abuse)

---

## Database Migrations

Migrations created:
- `accounts/migrations/0005_providerprofile_latitude_providerprofile_longitude_and_more.py`
- `requests/migrations/0004_servicerequest_offered_price.py`

To apply:
```bash
cd Django
python manage.py migrate
```

---

## Testing

### Manual Testing

1. **Test Price Validation:**
```bash
# Django admin or create request form
# Try submitting with price < provider min_price
# Verify error message appears
```

2. **Test Live Tracking:**
```bash
# Create accepted request
# Set provider location in admin
# Access: http://127.0.0.1:8000/requests/<id>/tracking/
# Verify JSON response
```

### Automated Testing
Both features have been tested with comprehensive test scripts:
- All validation scenarios tested
- Authorization tested
- Error handling verified
- Edge cases covered

---

## API Routes Summary

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/requests/create/` | POST | Yes | Create request (includes price validation) |
| `/requests/<id>/tracking/` | GET | Yes | Get provider live location |

---

## Future Enhancements

### Price Validation
- [ ] Dynamic pricing based on time of day
- [ ] Price negotiation workflow
- [ ] Price history tracking
- [ ] Discount codes support

### Live Tracking
- [ ] Real-time websocket updates
- [ ] Route display on map
- [ ] Traffic-aware ETA
- [ ] Push notifications when provider nearby
- [ ] Location history/breadcrumbs
- [ ] Geofencing alerts

---

## Support

For issues or questions:
1. Check this documentation
2. Review test scripts in Django directory
3. Check error codes in API responses
4. Verify database migrations applied

---

**Implementation Date:** January 7, 2026  
**Version:** 1.0  
**Status:** ✅ Production Ready

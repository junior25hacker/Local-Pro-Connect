# Quick Start Guide: Price Validation & Live Tracking

## 🚀 Quick Setup (Already Complete!)

Both features are **fully implemented and tested**. Here's what you need to know:

---

## 💰 Feature 1: Price Validation

### What It Does
Prevents users from submitting requests with prices below the provider's minimum.

### How to Use

**1. Set Provider's Minimum Price (Admin/Dashboard):**
```python
provider_profile.min_price = 75.00
provider_profile.save()
```

**2. User Creates Request:**
- Form automatically validates offered_price >= provider.min_price
- If validation fails: Clear error message shown
- If validation passes: Request is created

**3. Test It:**
```bash
# Access Django admin
http://127.0.0.1:8000/admin/accounts/providerprofile/
# Set min_price for any provider

# Create a request
http://127.0.0.1:8000/requests/create/
# Select provider, enter price below minimum
# See validation error
```

---

## 📍 Feature 2: Live Provider Tracking

### What It Does
Returns provider's real-time location for accepted service requests.

### How to Use

**1. Provider Updates Location:**
```python
# In provider's app/dashboard
provider_profile.latitude = 40.7589
provider_profile.longitude = -73.9851
provider_profile.save()
```

**2. User Tracks Provider (for accepted requests):**
```javascript
// GET /requests/<request_id>/tracking/
fetch('/requests/1/tracking/')
  .then(res => res.json())
  .then(data => {
    console.log(data.latitude, data.longitude);
    console.log(`ETA: ${data.eta_minutes} minutes`);
  });
```

**3. Test It:**
```bash
# Set provider location in admin
http://127.0.0.1:8000/admin/accounts/providerprofile/

# Access tracking endpoint (must be logged in as request owner)
http://127.0.0.1:8000/requests/1/tracking/
```

---

## 📋 API Endpoint Reference

### Live Provider Tracking
```
GET /requests/<request_id>/tracking/
```

**Requirements:**
- User must be logged in
- User must own the request
- Request must be accepted
- Provider must have location data

**Response:**
```json
{
  "success": true,
  "provider_id": 123,
  "provider_name": "John's Plumbing",
  "latitude": 40.7589,
  "longitude": -73.9851,
  "eta_minutes": 15,
  "provider_phone": "555-1234"
}
```

---

## ✅ Verification Checklist

- [x] Database migrations applied
- [x] Price validation working in forms
- [x] Tracking endpoint returns correct data
- [x] Authorization working (403 for unauthorized)
- [x] Error handling for edge cases
- [x] All tests passing

---

## 🔧 Common Tasks

### Update Provider Minimum Price
```python
from accounts.models import ProviderProfile

provider = ProviderProfile.objects.get(id=1)
provider.min_price = 100.00
provider.save()
```

### Set Provider Location
```python
from accounts.models import ProviderProfile
from decimal import Decimal

provider = ProviderProfile.objects.get(id=1)
provider.latitude = Decimal('40.7589')
provider.longitude = Decimal('-73.9851')
provider.save()
```

### Check Request Can Be Tracked
```python
from requests.models import ServiceRequest

request = ServiceRequest.objects.get(id=1)
print(f"Status: {request.status}")  # Must be 'accepted'
print(f"Owner: {request.user}")
print(f"Provider: {request.provider}")
```

---

## 🐛 Troubleshooting

### Price Validation Not Working
- Check if migrations applied: `python manage.py migrate`
- Verify provider has min_price set
- Check form is using ServiceRequestForm

### Tracking Returns 403 (Forbidden)
- Ensure user is logged in
- Verify user owns the request (request.user == logged_in_user)

### Tracking Returns 400 (Bad Request)
- Check request status is 'accepted'
- Verify provider has latitude/longitude set
- Check provider is assigned to request

### Tracking Returns "Location Not Available"
- Provider's latitude or longitude is NULL
- Set location in admin or via API

---

## 📱 Integration Examples

### React/Vue Frontend
```javascript
// Tracking component
async function fetchProviderLocation(requestId) {
  const response = await fetch(`/requests/${requestId}/tracking/`);
  const data = await response.json();
  
  if (data.success) {
    updateMap(data.latitude, data.longitude);
    showETA(data.eta_minutes);
  } else {
    showError(data.error);
  }
}

// Poll every 30 seconds
setInterval(() => fetchProviderLocation(requestId), 30000);
```

### Google Maps Integration
```javascript
function displayProviderOnMap(lat, lng, providerName) {
  const map = new google.maps.Map(document.getElementById('map'), {
    center: {lat, lng},
    zoom: 14
  });
  
  new google.maps.Marker({
    position: {lat, lng},
    map: map,
    title: providerName,
    icon: 'provider-icon.png'
  });
}
```

---

## 📊 Testing Commands

```bash
# Run Django shell
cd Django
python manage.py shell

# Test price validation
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile

provider = ProviderProfile.objects.first()
form = ServiceRequestForm(data={
    'provider_choice': provider.id,
    'description': 'Test service',
    'offered_price': '25.00'  # Below minimum
})
print(form.is_valid())  # Should be False
print(form.errors)

# Test tracking endpoint
from django.test import Client
client = Client()
client.login(username='user', password='pass')
response = client.get('/requests/1/tracking/')
print(response.json())
```

---

## 🎯 What's Next?

Now that both features are working, you can:

1. **Frontend Integration**: Build UI for tracking map
2. **Real-time Updates**: Add WebSocket support for live updates
3. **Mobile App**: Integrate tracking in mobile app
4. **Analytics**: Track provider response times and ETAs
5. **Notifications**: Alert users when provider is nearby

---

## 📞 Support

If you encounter issues:
1. Check migrations: `python manage.py showmigrations`
2. Review full documentation: `PRICE_VALIDATION_AND_TRACKING_IMPLEMENTATION.md`
3. Check Django logs for errors
4. Verify database has required fields

---

**Status:** ✅ **READY TO USE**  
**Last Updated:** January 7, 2026

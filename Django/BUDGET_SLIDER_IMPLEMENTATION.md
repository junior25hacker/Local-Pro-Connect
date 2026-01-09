# Budget Slider Component - Backend Implementation

## Overview
This document describes the complete backend implementation for the Budget Slider component that allows users to specify a budget when creating service requests and validates it against provider pricing constraints.

## Implementation Summary

### 1. Model Enhancements

#### ProviderProfile Model Updates
**File:** `accounts/models.py`

Added three new fields to store provider pricing information:
- `max_price`: DecimalField - Maximum service price (optional, for display range)
- `service_rate`: CharField - How provider charges (hourly/fixed/custom)

```python
max_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                                help_text="Maximum service price (for display range)")
service_rate = models.CharField(max_length=20, choices=SERVICE_RATE_CHOICES, default='fixed',
                                help_text="How this provider charges for services")
```

#### Migration Created
- `accounts/migrations/0006_providerprofile_max_price_and_more.py` - Adds max_price and service_rate fields

### 2. API Endpoint Enhancement

#### Enhanced `api_provider_min_price()` Endpoint
**File:** `requests/views.py` (lines 899-941)

**Endpoint:** `GET /requests/api/provider/<provider_id>/min-price/`

**Response includes:**
```json
{
  "success": true,
  "provider_id": 88,
  "min_price": 50.0,
  "max_price": 500.0,
  "avg_price": 275.0,
  "service_rate": "custom",
  "currency": "USD",
  "company_name": "Handy Expert Services"
}
```

**Features:**
- Returns comprehensive pricing information
- Calculates average price from min/max
- Includes service rate type
- Error handling for invalid provider IDs
- Type error handling for malformed pricing data

### 3. Form Validation

#### Enhanced `ServiceRequestForm` Validation
**File:** `requests/forms.py` (lines 98-141)

**Validation Rules:**
1. **Minimum Price Check:** Ensures offered_price >= provider's min_price
2. **Maximum Price Check:** Ensures offered_price <= provider's max_price (if set)
3. **Sanity Check:** Rejects prices > $50,000 to catch data entry errors
4. **Zero/Negative Check:** Prevents non-positive budget values
5. **Provider Requirement:** At least provider_choice or provider_name must be provided

**Error Messages:**
- Below minimum: "The offered price ($X.XX) is below the minimum required by [Provider] ($Y.YY)..."
- Above maximum: "The offered price ($X.XX) exceeds the maximum rate for [Provider] ($Y.YY)..."
- Unreasonable: "The offered price ($X.XX) seems unreasonably high..."
- Zero/Negative: "Budget amount must be greater than zero."

### 4. Request Submission Logic

#### Enhanced `create_request()` View
**File:** `requests/views.py` (lines 82-127)

**Features:**
- Validates budget against provider's minimum price via form validation
- Stores budget value in `offered_price` field
- Logs budget information for reporting and auditing
- Includes budget validation details in logs
- Maintains all existing functionality (photos, provider selection, etc.)

**Logging:**
```python
logger.info(f"Service request #{request.id} created with budget ${offered_price:.2f} for provider {provider_name} by user {username}")
logger.info(f"Budget ${offered_price:.2f} validated against provider minimum ${min_price:.2f}")
```

### 5. Email Notifications

#### Updated Email Templates

**`request_to_provider_email.txt`:**
- Added "Offered Budget" line showing the user's budget offer
- Distinguishes between "Budget Category" (price range) and "Offered Budget" (specific amount)

**`request_to_provider_email.html`:**
- Styled "Offered Budget" in green and bold for emphasis
- Professional formatting with color highlighting

**`request_confirmation_email.txt`:**
- Shows user the budget they submitted in confirmation email

#### Context Variables
All templates receive:
- `offered_price`: The exact budget amount submitted by user
- `price_range`: Optional category (if selected)
- Both are conditionally displayed in templates

### 6. Provider Seeding

#### Updated Seed Script
**File:** `requests/management/commands/seed_providers.py`

All 24 providers now include realistic pricing:

**Pricing by Service Type:**
- **Plumbing:** $75-$400 (fixed)
- **Electrical:** $100-$500 (hourly)
- **Carpentry:** $85-$450 (fixed)
- **Cleaning:** $50-$200 (hourly)
- **Tutoring:** $40-$150 (hourly)
- **HVAC:** $120-$600 (fixed)
- **Roofing:** $150-$1000 (fixed)
- **Landscaping:** $60-$300 (fixed)
- **Painting:** $70-$350 (fixed)
- **Other:** $50-$500 (custom)

**Provider Distribution:**
- 24 total providers
- Distributed across 10 service types
- Realistic pricing ranges for each service
- Service rates: fixed, hourly, and custom options

### 7. Error Handling

#### Edge Cases Handled

1. **Provider without pricing info:**
   - Returns 404 with "Provider not found" error
   - Gracefully handles missing provider profiles

2. **Invalid provider ID:**
   - Returns 404 status with appropriate error message
   - Safe handling of non-existent providers

3. **Negative/Zero budget values:**
   - Form validation rejects immediately
   - User receives clear error message

4. **Extremely high budget values:**
   - Sanity check rejects prices > $50,000
   - Prevents accidental data entry errors

5. **Type errors in pricing data:**
   - API endpoint catches ValueError/TypeError
   - Returns 400 Bad Request with error message

6. **Missing max_price field:**
   - API safely handles null max_price
   - Returns null in response rather than failing

### 8. Integration Testing

#### Verified Functionality

**API Endpoint:**
```bash
# Test API response
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/requests/api/provider/88/min-price/
```

**Database Verification:**
```python
# All providers have pricing set
from accounts.models import ProviderProfile
providers = ProviderProfile.objects.all()
for p in providers:
    assert p.min_price > 0
    assert p.max_price >= p.min_price
    assert p.service_rate in ['hourly', 'fixed', 'custom']
```

**Form Validation:**
- Minimum price validation: ✓
- Maximum price validation: ✓
- Sanity check validation: ✓
- Zero/negative check: ✓
- Error messages display correctly: ✓

## Files Modified

1. **Django/accounts/models.py** - Added max_price and service_rate fields
2. **Django/requests/views.py** - Enhanced API endpoint and logging
3. **Django/requests/forms.py** - Enhanced form validation
4. **Django/requests/management/commands/seed_providers.py** - Added pricing data
5. **Django/requests/templates/emails/request_to_provider_email.txt** - Added budget display
6. **Django/requests/templates/emails/request_to_provider_email.html** - Added styled budget display
7. **Django/requests/templates/emails/request_confirmation_email.txt** - Added budget confirmation

## Files Created

1. **Django/accounts/migrations/0006_providerprofile_max_price_and_more.py** - Migration for new fields

## Database Changes

```sql
-- Added columns to accounts_providerprofile table
ALTER TABLE accounts_providerprofile ADD COLUMN max_price DECIMAL(10, 2) NULL;
ALTER TABLE accounts_providerprofile ADD COLUMN service_rate VARCHAR(20) DEFAULT 'fixed' NOT NULL;
```

## Usage Examples

### Creating a Service Request with Budget

```python
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile

# User selects a provider with min_price=$75 and enters budget=$100
form_data = {
    'provider_choice': ProviderProfile.objects.first().id,
    'description': 'Fix my pipes',
    'offered_price': 100.00,  # Budget within provider's range
}

form = ServiceRequestForm(data=form_data)
if form.is_valid():
    request = form.save(commit=False)
    request.user = user
    request.save()
    # Budget is validated and stored
```

### Checking Provider Pricing via API

```javascript
// Frontend JavaScript
fetch(`/requests/api/provider/${providerId}/min-price/`, {
    headers: {'Authorization': 'Bearer ' + token}
})
.then(r => r.json())
.then(data => {
    console.log(`Min: $${data.min_price}, Max: $${data.max_price}`);
    console.log(`Service rate: ${data.service_rate}`);
    // Update UI with pricing constraints
});
```

## Testing Checklist

- [x] Migration applies without errors
- [x] All 24 providers seeded with realistic pricing
- [x] API endpoint returns comprehensive pricing info
- [x] Form validation enforces minimum price
- [x] Form validation enforces maximum price
- [x] Form validation catches unreasonable amounts
- [x] Budget appears in provider email notifications
- [x] Budget appears in user confirmation emails
- [x] Logging captures budget information
- [x] Error handling for invalid providers
- [x] Error handling for missing pricing fields

## Performance Considerations

1. **Database Queries:** API endpoint performs single query per provider
2. **Caching:** Currently no caching; can be added with Django cache framework
3. **Decimal Precision:** Using DecimalField for accurate currency representation
4. **Validation:** Form validation happens on submit; no real-time validation overhead

## Future Enhancements

1. Add caching with Django's cache framework for API endpoint
2. Implement real-time validation on frontend using Slider component
3. Add currency selection per provider
4. Implement dynamic pricing based on service complexity
5. Add time-based pricing (rush hour surcharge)
6. Provider pricing history and analytics

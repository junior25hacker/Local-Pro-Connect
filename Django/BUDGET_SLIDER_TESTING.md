# Budget Slider Component - Testing Guide

## Quick Test Steps

### 1. Verify Database Migration

```bash
cd Django
python manage.py migrate accounts
```

Expected output: `Applying accounts.0006_providerprofile_max_price_and_more... OK`

### 2. Verify Provider Seeding

```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile

# Check all providers have pricing
providers = ProviderProfile.objects.all()
print(f"Total providers: {providers.count()}")

# Sample provider
p = providers.first()
print(f"\n{p.company_name}:")
print(f"  Min: ${p.min_price:.2f}")
print(f"  Max: ${p.max_price:.2f}")
print(f"  Rate: {p.service_rate}")

# Check all have pricing
missing = providers.filter(min_price__isnull=True) | providers.filter(max_price__isnull=True)
print(f"\nProviders missing pricing: {missing.count()}")
EOF
```

### 3. Test API Endpoint

```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile
from django.test import Client
from django.contrib.auth.models import User
import json

# Setup
provider = ProviderProfile.objects.first()
user = User.objects.create_user('apitest', 'test@example.com', 'pass')
client = Client()
client.login(username='apitest', password='pass')

# Test API
response = client.get(f'/requests/api/provider/{provider.id}/min-price/')
print(f"Status: {response.status_code}")
print(f"Response:\n{json.dumps(response.json(), indent=2)}")

# Verify response has all fields
data = response.json()
required_fields = ['min_price', 'max_price', 'avg_price', 'service_rate', 'currency', 'company_name']
missing = [f for f in required_fields if f not in data]
if missing:
    print(f"\nMISSING FIELDS: {missing}")
else:
    print("\n✓ All required fields present")
EOF
```

### 4. Test Form Validation

```bash
cd Django
python manage.py shell << 'EOF'
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile
from django.contrib.auth.models import User

# Setup
provider = ProviderProfile.objects.first()
user = User.objects.create_user('formtest', 'test@example.com', 'pass')
print(f"Testing with provider: {provider.company_name}")
print(f"Min price: ${provider.min_price:.2f}")
print(f"Max price: ${provider.max_price:.2f}")

# Test 1: Valid budget (within range)
print("\n--- Test 1: Valid budget ---")
form_data = {
    'provider_choice': provider.id,
    'description': 'Test request',
    'offered_price': float(provider.min_price) + 10,
}
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors}")

# Test 2: Budget below minimum
print("\n--- Test 2: Budget below minimum ---")
form_data['offered_price'] = float(provider.min_price) - 1
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors['__all__']}")

# Test 3: Budget above maximum
print("\n--- Test 3: Budget above maximum ---")
form_data['offered_price'] = float(provider.max_price) + 1
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors['__all__']}")

# Test 4: Unreasonably high budget
print("\n--- Test 4: Unreasonably high budget ---")
form_data['offered_price'] = 60000
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors['__all__']}")

# Test 5: Zero budget
print("\n--- Test 5: Zero budget ---")
form_data['offered_price'] = 0
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors['__all__']}")

# Test 6: Negative budget
print("\n--- Test 6: Negative budget ---")
form_data['offered_price'] = -50
form = ServiceRequestForm(data=form_data)
print(f"Valid: {form.is_valid()}")
if not form.is_valid():
    print(f"Errors: {form.errors}")
EOF
```

### 5. Test Request Creation with Budget Logging

```bash
cd Django
python manage.py shell << 'EOF'
from requests.models import ServiceRequest
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile, UserProfile
from django.contrib.auth.models import User
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Setup
provider = ProviderProfile.objects.first()
user = User.objects.create_user('creationtest', 'test@example.com', 'pass')
UserProfile.objects.create(user=user)

# Create request with budget
form_data = {
    'provider_choice': provider.id,
    'description': 'Test plumbing repair',
    'offered_price': 150.00,
}

form = ServiceRequestForm(data=form_data)
if form.is_valid():
    request = form.save(commit=False)
    request.user = user
    request.save()
    print(f"✓ Request created: #{request.id}")
    print(f"  Budget: ${request.offered_price:.2f}")
    print(f"  Provider: {request.provider_name}")
else:
    print(f"Form errors: {form.errors}")
EOF
```

### 6. Test Email Template Variables

```bash
cd Django
python manage.py shell << 'EOF'
from requests.models import ServiceRequest
from requests.forms import ServiceRequestForm
from accounts.models import ProviderProfile, UserProfile
from django.contrib.auth.models import User
from django.template.loader import render_to_string

# Setup
provider = ProviderProfile.objects.first()
user = User.objects.create_user('emailtest', 'test@example.com', 'pass')
UserProfile.objects.create(user=user)

# Create request
form_data = {
    'provider_choice': provider.id,
    'description': 'Test request',
    'offered_price': 150.00,
}
form = ServiceRequestForm(data=form_data)
if form.is_valid():
    req = form.save(commit=False)
    req.user = user
    req.save()
    
    # Check email context
    context = {
        'request_id': req.id,
        'provider_name': provider.company_name,
        'description': req.description,
        'offered_price': req.offered_price,
        'price_range': req.price_range,
        'date_time': req.date_time,
        'urgent': req.urgent,
        'status': req.status,
    }
    
    # Test text template
    text = render_to_string('emails/request_to_provider_email.txt', context)
    print("=== Text Email Output ===")
    print(text)
    
    # Verify offered_price appears
    if 'Offered Budget' in text and '150.00' in text:
        print("\n✓ Budget appears in text email")
    else:
        print("\n✗ Budget missing from text email")
EOF
```

### 7. Test Pricing by Service Type

```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile

print("Pricing by Service Type:")
print("=" * 70)

service_types = set(ProviderProfile.objects.values_list('service_type', flat=True))
for service in sorted(service_types):
    providers = ProviderProfile.objects.filter(service_type=service)
    if providers:
        p = providers.first()
        count = providers.count()
        print(f"{service:15} | Min: ${p.min_price:7.2f} | Max: ${p.max_price:7.2f} | Rate: {p.service_rate:8} | Count: {count}")
EOF
```

### 8. Test API Error Handling

```bash
cd Django
python manage.py shell << 'EOF'
from django.test import Client
from django.contrib.auth.models import User
import json

client = Client()
user = User.objects.create_user('errortest', 'test@example.com', 'pass')
client.login(username='errortest', password='pass')

# Test 1: Invalid provider ID
print("--- Test 1: Invalid provider ID ---")
response = client.get('/requests/api/provider/99999/min-price/')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

# Test 2: Valid provider
print("\n--- Test 2: Valid provider ID ---")
from accounts.models import ProviderProfile
provider = ProviderProfile.objects.first()
response = client.get(f'/requests/api/provider/{provider.id}/min-price/')
print(f"Status: {response.status_code}")
data = response.json()
print(f"Fields: {', '.join(data.keys())}")
EOF
```

## Manual UI Testing

### Test Request Creation Form

1. Navigate to create request page
2. Select a provider (e.g., "AquaFlow Plumbing Solutions" - min $75)
3. Enter budget:
   - **Test Case 1:** $50 (below minimum) → Should show error
   - **Test Case 2:** $75 (at minimum) → Should accept
   - **Test Case 3:** $200 (middle range) → Should accept
   - **Test Case 4:** $400 (at maximum) → Should accept
   - **Test Case 5:** $401 (above maximum) → Should show error
   - **Test Case 6:** $60000 (unreasonable) → Should show error

### Test Email Notifications

1. Create a service request with budget $150
2. Check provider's email inbox:
   - Should show "Offered Budget: $150.00"
   - Should distinguish from "Budget Category" if price range selected
3. Check user's confirmation email:
   - Should show the budget in request summary

### Test API Endpoint

1. Authenticate and make request to `/requests/api/provider/<id>/min-price/`
2. Verify response includes:
   - min_price
   - max_price
   - avg_price
   - service_rate
   - currency
   - company_name

## Debugging

### View Request with Budget
```bash
cd Django
python manage.py shell << 'EOF'
from requests.models import ServiceRequest
latest = ServiceRequest.objects.latest('created_at')
print(f"Request #{latest.id}:")
print(f"  Budget: ${latest.offered_price}")
print(f"  Provider: {latest.provider_name}")
print(f"  Status: {latest.status}")
EOF
```

### View Provider Pricing
```bash
cd Django
python manage.py shell << 'EOF'
from accounts.models import ProviderProfile
p = ProviderProfile.objects.get(company_name='AquaFlow Plumbing Solutions')
print(f"{p.company_name}:")
print(f"  Min: ${p.min_price:.2f}")
print(f"  Max: ${p.max_price:.2f}")
print(f"  Rate: {p.service_rate}")
EOF
```

### Check Logs
```bash
tail -f Django/django_runtime.log
# or
grep "budget\|price" Django/django_runtime.log
```

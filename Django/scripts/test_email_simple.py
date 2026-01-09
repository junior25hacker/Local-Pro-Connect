#!/usr/bin/env python
"""
Simple Email Workflow Test Script

Tests the email system with console backend (prints emails to console).

Usage:
    cd Django && python manage.py shell
    >>> exec(open('../scripts/test_email_simple.py').read())
"""

import os
os.environ['EMAIL_BACKEND'] = 'django.core.mail.backends.console.EmailBackend'

from datetime import timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

from requests.models import ServiceRequest, PriceRange
from requests.email_service import get_email_configuration_info
from accounts.models import ProviderProfile, UserProfile

print("\n" + "=" * 80)
print("SIMPLE EMAIL WORKFLOW TEST")
print("=" * 80 + "\n")

# Show config
config = get_email_configuration_info()
print("[CONFIG]")
for key, value in config.items():
    print(f"  {key}: {value}")
print()

# Create test users
print("[USERS]")
customer, _ = User.objects.get_or_create(
    username="test_cust_simple",
    defaults={"email": "cust@test.local", "first_name": "Test", "last_name": "Cust"}
)
print(f"  Customer: {customer.username} ({customer.email})")

provider, _ = User.objects.get_or_create(
    username="test_prov_simple",
    defaults={"email": "prov@test.local", "first_name": "Test", "last_name": "Prov"}
)
print(f"  Provider: {provider.username} ({provider.email})")

# Create profiles
UserProfile.objects.get_or_create(user=customer, defaults={"city": "NYC", "state": "NY", "zip_code": "10001"})
provider_profile, _ = ProviderProfile.objects.get_or_create(
    user=provider,
    defaults={"company_name": "Test Services", "service_type": "plumbing", "city": "NYC", "state": "NY", "zip_code": "10002"}
)
print(f"  Provider Profile: {provider_profile.company_name}")
print()

# Create price range
price_range, _ = PriceRange.objects.get_or_create(
    label="$100-$200",
    defaults={"min_price": 100, "max_price": 200}
)
print(f"[PRICE RANGE] {price_range.label}\n")

# Create request (triggers signals)
print("[CREATING REQUEST]")
request = ServiceRequest.objects.create(
    user=customer,
    provider_name=provider_profile.company_name,
    description="Test service request",
    price_range=price_range,
    date_time=timezone.now() + timedelta(days=3),
)
print(f"  ✓ Request #{request.id} created")
print(f"    Status: {request.status}")
print(f"    Email sent to provider: {request.email_sent_to_provider}")
print(f"    Email sent to user: {request.email_sent_to_user}\n")

print("[ACCEPTING REQUEST]")
request.accept(provider)
request.refresh_from_db()
print(f"  ✓ Request #{request.id} accepted")
print(f"    Status: {request.status}")
print(f"    Provider: {request.provider.username}\n")

print("[CREATING DECLINE REQUEST]")
request2 = ServiceRequest.objects.create(
    user=customer,
    provider_name=provider_profile.company_name,
    description="Another test request",
    price_range=price_range,
)
print(f"  ✓ Request #{request2.id} created\n")

print("[DECLINING REQUEST]")
request2.decline('price', 'Price too low')
request2.refresh_from_db()
print(f"  ✓ Request #{request2.id} declined")
print(f"    Status: {request2.status}")
print(f"    Reason: {request2.decline_reason}\n")

print("=" * 80)
print("✓ TEST COMPLETE - Check console output above for emails")
print("=" * 80 + "\n")

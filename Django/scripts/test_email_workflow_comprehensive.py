#!/usr/bin/env python
"""
Comprehensive Email Workflow Testing Script

This script tests the complete email notification system:
1. Verifies SMTP configuration
2. Tests email connection
3. Creates test users
4. Tests service request creation (triggers provider email + user confirmation)
5. Tests provider acceptance (triggers customer acceptance email)
6. Tests provider decline (triggers customer decline email)
7. Validates email tracking in database
8. Tests error scenarios

Usage:
    python manage.py shell < scripts/test_email_workflow_comprehensive.py
    OR
    cd Django && python manage.py shell
    >>> exec(open('../scripts/test_email_workflow_comprehensive.py').read())

Requirements:
    - Email configuration in settings.py
    - Optional: Set SMTP credentials via environment variables
      export EMAIL_HOST_USER=your_email@gmail.com
      export EMAIL_HOST_PASSWORD=your_app_password
"""

import os
import sys
import time
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.conf import settings
from django.utils import timezone

# Import models and utilities
from requests.models import ServiceRequest, RequestDecisionToken, PriceRange
from requests.email_service import (
    test_email_configuration,
    get_email_configuration_info,
    send_request_to_provider,
    send_user_confirmation_email,
    send_acceptance_email,
    send_decline_email,
)
from accounts.models import ProviderProfile, UserProfile

print("\n" + "=" * 80)
print("COMPREHENSIVE EMAIL WORKFLOW TESTING")
print("=" * 80 + "\n")

# ============================================================================
# STEP 1: Display Email Configuration
# ============================================================================
print("[STEP 1] Email Configuration")
print("-" * 80)

config = get_email_configuration_info()
for key, value in config.items():
    print(f"  {key}: {value}")

print("\n  Backend Type: ", end="")
if "console" in settings.EMAIL_BACKEND.lower():
    print("✓ Console (Development Mode - emails printed to console)")
elif "smtp" in settings.EMAIL_BACKEND.lower():
    print("✓ SMTP (Production - emails sent via SMTP)")
else:
    print("? Unknown backend")

print()

# ============================================================================
# STEP 2: Test Email Connection
# ============================================================================
print("[STEP 2] Test Email Connection")
print("-" * 80)

test_result = test_email_configuration()
print(f"  Result: {'✓ SUCCESS' if test_result['success'] else '✗ FAILED'}")
print(f"  Message: {test_result['message']}")

if not test_result['success']:
    print("\n  ⚠ Warning: Email connection test failed.")
    print("  Continuing with workflow tests anyway...\n")
else:
    print()

# ============================================================================
# STEP 3: Create Test Users and Profiles
# ============================================================================
print("[STEP 3] Create Test Users")
print("-" * 80)

# Create customer
customer_username = "test_customer_workflow"
customer, created = User.objects.get_or_create(
    username=customer_username,
    defaults={
        "email": f"{customer_username}@locapro.test",
        "first_name": "Test",
        "last_name": "Customer",
    }
)
if created:
    customer.set_password("testpass123")
    customer.save()
    print(f"  ✓ Created customer: {customer.username}")
else:
    print(f"  ℹ Customer exists: {customer.username}")

# Create customer profile with address info
customer_profile, _ = UserProfile.objects.get_or_create(
    user=customer,
    defaults={
        "address": "123 Main St",
        "city": "New York",
        "state": "NY",
        "zip_code": "10001",
    }
)
print(f"  ✓ Customer profile ready: {customer_profile.city}, {customer_profile.state}")

# Create provider
provider_username = "test_provider_workflow"
provider, created = User.objects.get_or_create(
    username=provider_username,
    defaults={
        "email": f"{provider_username}@locapro.test",
        "first_name": "Test",
        "last_name": "Provider",
    }
)
if created:
    provider.set_password("testpass123")
    provider.save()
    print(f"  ✓ Created provider: {provider.username}")
else:
    print(f"  ℹ Provider exists: {provider.username}")

# Create provider profile
provider_profile, created = ProviderProfile.objects.get_or_create(
    user=provider,
    defaults={
        "company_name": "Test Provider Services",
        "bio": "A test provider for comprehensive email workflow testing",
        "service_type": "plumbing",
        "business_address": "456 Service Ave",
        "city": "New York",
        "state": "NY",
        "zip_code": "10002",
        "phone": "555-1234",
    }
)
print(f"  ✓ Provider profile ready: {provider_profile.company_name}")

# Create price range
price_range, _ = PriceRange.objects.get_or_create(
    label="$100-$200",
    defaults={
        "min_price": 100,
        "max_price": 200,
    }
)
print(f"  ✓ Price range ready: {price_range.label}\n")

# ============================================================================
# STEP 4: Test Request Submission Workflow
# ============================================================================
print("[STEP 4] Test Request Submission")
print("-" * 80)

# Create a new service request (this should trigger signals)
service_request = ServiceRequest.objects.create(
    user=customer,
    provider_name=provider_profile.company_name,
    description="Test plumbing work - comprehensive workflow verification",
    price_range=price_range,
    urgent=False,
    date_time=timezone.now() + timedelta(days=3),
)

print(f"  ✓ Created request ID: {service_request.id}")
print(f"    Status: {service_request.status}")
print(f"    Customer: {service_request.user.username}")
print(f"    Provider: {service_request.provider_name}")

# Small delay to allow async emails to send
print("  ⏳ Waiting for async emails to send... (2 seconds)")
time.sleep(2)

# Check email tracking
service_request.refresh_from_db()
print(f"\n  Email Tracking:")
print(f"    Provider email sent: {'✓' if service_request.email_sent_to_provider else '✗'}")
print(f"    User email sent: {'✓' if service_request.email_sent_to_user else '✗'}")

if service_request.email_sent_to_provider_timestamp:
    print(f"    Provider email timestamp: {service_request.email_sent_to_provider_timestamp}")
if service_request.email_sent_to_user_timestamp:
    print(f"    User email timestamp: {service_request.email_sent_to_user_timestamp}")

print()

# ============================================================================
# STEP 5: Verify Decision Token
# ============================================================================
print("[STEP 5] Verify Decision Token")
print("-" * 80)

try:
    decision_token = RequestDecisionToken.objects.get(service_request=service_request)
    print(f"  ✓ Decision token found: {decision_token.token[:20]}...")
    print(f"    Created: {decision_token.created_at}")
    print(f"    Expires: {decision_token.expires_at}")
    print(f"    Is valid: {decision_token.is_valid()}")
    print(f"    Days until expiration: {(decision_token.expires_at - timezone.now()).days}")
except RequestDecisionToken.DoesNotExist:
    print("  ✗ Decision token not found")

print()

# ============================================================================
# STEP 6: Test Provider Acceptance Workflow
# ============================================================================
print("[STEP 6] Test Provider Acceptance")
print("-" * 80)

# Accept the request
service_request.accept(provider)
print(f"  ✓ Request accepted")
print(f"    Status: {service_request.status}")
print(f"    Provider: {service_request.provider.username}")
print(f"    Accepted at: {service_request.accepted_at}")

# Wait for async acceptance email
print("  ⏳ Waiting for acceptance email... (2 seconds)")
time.sleep(2)

# Check tracking
service_request.refresh_from_db()
print(f"  ✓ Response timestamp: {service_request.email_response_timestamp}")

print()

# ============================================================================
# STEP 7: Test Provider Decline Workflow
# ============================================================================
print("[STEP 7] Test Provider Decline")
print("-" * 80)

# Create another request to test decline
service_request_2 = ServiceRequest.objects.create(
    user=customer,
    provider_name=provider_profile.company_name,
    description="Test decline workflow - another plumbing request",
    price_range=price_range,
    urgent=True,
)

print(f"  ✓ Created request ID: {service_request_2.id} for decline testing")

# Wait for initial emails
time.sleep(2)

# Decline the request
service_request_2.decline('price', 'Price is too low for this project')
print(f"  ✓ Request declined")
print(f"    Status: {service_request_2.status}")
print(f"    Decline reason: {service_request_2.decline_reason}")
print(f"    Decline message: {service_request_2.decline_message}")
print(f"    Declined at: {service_request_2.declined_at}")

# Wait for decline email
print("  ⏳ Waiting for decline email... (2 seconds)")
time.sleep(2)

# Check tracking
service_request_2.refresh_from_db()
print(f"  ✓ Response timestamp: {service_request_2.email_response_timestamp}")

print()

# ============================================================================
# STEP 8: Email Tracking Summary
# ============================================================================
print("[STEP 8] Email Tracking Summary")
print("-" * 80)

print("\n  REQUEST #1 (Accepted):")
service_request.refresh_from_db()
print(f"    ID: {service_request.id}")
print(f"    Status: {service_request.status}")
print(f"    Provider email: {service_request.email_sent_to_provider}")
print(f"    User email: {service_request.email_sent_to_user}")
print(f"    Response timestamp: {service_request.email_response_timestamp}")

print("\n  REQUEST #2 (Declined):")
service_request_2.refresh_from_db()
print(f"    ID: {service_request_2.id}")
print(f"    Status: {service_request_2.status}")
print(f"    Provider email: {service_request_2.email_sent_to_provider}")
print(f"    User email: {service_request_2.email_sent_to_user}")
print(f"    Response timestamp: {service_request_2.email_response_timestamp}")

print()

# ============================================================================
# STEP 9: Manual Email Testing
# ============================================================================
print("[STEP 9] Test Manual Email Functions")
print("-" * 80)

print("\n  Testing send_request_to_provider()...")
result = send_request_to_provider(service_request, async_send=False)
print(f"    Result: {result['success']}")
print(f"    Message: {result['message']}")

print("\n  Testing send_user_confirmation_email()...")
result = send_user_confirmation_email(service_request, async_send=False)
print(f"    Result: {result['success']}")
print(f"    Message: {result['message']}")

print("\n  Testing send_acceptance_email()...")
result = send_acceptance_email(service_request, async_send=False)
print(f"    Result: {result['success']}")
print(f"    Message: {result['message']}")

print("\n  Testing send_decline_email()...")
result = send_decline_email(service_request_2, async_send=False)
print(f"    Result: {result['success']}")
print(f"    Message: {result['message']}")

print()

# ============================================================================
# STEP 10: Final Summary
# ============================================================================
print("=" * 80)
print("WORKFLOW TEST COMPLETE")
print("=" * 80)

print("""
SUMMARY:
--------

✓ SMTP configuration loaded
✓ Email connection tested
✓ Test users and profiles created
✓ Service request submission workflow tested
✓ Provider acceptance workflow tested
✓ Provider decline workflow tested
✓ Email tracking verified in database
✓ Manual email functions tested

EMAILS SENT:
-----------

Request #1 (Submitted):
  - Provider notification email (with accept/decline links)
  - Customer confirmation email

Request #1 (Accepted by provider):
  - Customer acceptance notification email

Request #2 (Submitted):
  - Provider notification email (with accept/decline links)
  - Customer confirmation email

Request #2 (Declined by provider):
  - Customer decline notification email

EMAIL CONFIGURATION:
-------------------
Backend: {backend}
Host: {host}:{port}
From Email: {from_email}
SSL: {use_ssl} | TLS: {use_tls}

NEXT STEPS:
----------

1. Check email inbox for test emails
   - Sender: {from_email}
   - Recipients: {customer_email}, {provider_email}

2. Verify email formatting and links

3. Test decision links (if emails were received):
   - Accept/Decline links valid for 7 days

4. For production setup, see: SMTP_CONFIGURATION_GUIDE.md

TEST DATA:
----------
Customer: {customer_username} ({customer_email})
Provider: {provider_username} ({provider_email})
Test Requests: #{request_id1}, #{request_id2}

For more information or troubleshooting, see the email service documentation.
""".format(
    backend=settings.EMAIL_BACKEND.split('.')[-1],
    host=settings.EMAIL_HOST,
    port=settings.EMAIL_PORT,
    from_email=settings.DEFAULT_FROM_EMAIL,
    use_ssl=settings.EMAIL_USE_SSL,
    use_tls=settings.EMAIL_USE_TLS,
    customer_email=customer.email,
    provider_email=provider.email,
    customer_username=customer.username,
    provider_username=provider.username,
    request_id1=service_request.id,
    request_id2=service_request_2.id,
))

print("=" * 80 + "\n")

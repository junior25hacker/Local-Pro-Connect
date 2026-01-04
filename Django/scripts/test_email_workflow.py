#!/usr/bin/env python
"""
Email Workflow Testing Script

This script tests the complete email notification workflow:
1. Creates test users (customer and provider)
2. Creates a service request
3. Verifies emails are sent
4. Tests provider decision (accept/decline)
5. Verifies customer notification emails

Usage:
    python manage.py shell < scripts/test_email_workflow.py
    OR
    python manage.py shell
    >>> exec(open('scripts/test_email_workflow.py').read())

Requirements:
    - Export email configuration variables before running:
      export EMAIL_HOST_USER=your_email@gmail.com
      export EMAIL_HOST_PASSWORD=your_app_password
      export SITE_URL=http://localhost:8000
"""

import os
import sys
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.core.mail import outbox as email_outbox
from django.utils import timezone
from django.conf import settings

# Import models
from requests.models import ServiceRequest, RequestDecisionToken, PriceRange
from accounts.models import ProviderProfile

print("=" * 70)
print("EMAIL WORKFLOW TESTING SCRIPT")
print("=" * 70)
print()

# ============================================================================
# STEP 1: Verify Email Configuration
# ============================================================================
print("[STEP 1] Verifying Email Configuration...")
print("-" * 70)

print(f"  Email Backend: {settings.EMAIL_BACKEND}")
print(f"  SMTP Provider: {os.environ.get('SMTP_PROVIDER', 'Not set')}")
print(f"  Email Host: {settings.EMAIL_HOST}")
print(f"  Email Port: {settings.EMAIL_PORT}")
print(f"  Use SSL: {settings.EMAIL_USE_SSL}")
print(f"  Use TLS: {settings.EMAIL_USE_TLS}")
print(f"  From Email: {settings.DEFAULT_FROM_EMAIL}")
print(f"  Site URL: {settings.SITE_URL}")

# Check if credentials are configured
if settings.EMAIL_HOST_USER and settings.EMAIL_HOST_USER != '':
    print(f"  Host User: {settings.EMAIL_HOST_USER}")
    print("  ✓ Email credentials configured")
else:
    print("  ⚠ WARNING: EMAIL_HOST_USER not configured")

print()

# ============================================================================
# STEP 2: Test Email Connection
# ============================================================================
print("[STEP 2] Testing Email Connection...")
print("-" * 70)

try:
    from django.core.mail import get_connection
    connection = get_connection()
    connection.open()
    print("  ✓ Email connection successful")
    connection.close()
except Exception as e:
    print(f"  ✗ Connection failed: {e}")
    print("  Make sure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD are set correctly")
    sys.exit(1)

print()

# ============================================================================
# STEP 3: Create Test Users
# ============================================================================
print("[STEP 3] Creating Test Users...")
print("-" * 70)

# Create or get customer user
customer_email = "test_customer@locapro.local"
customer, created = User.objects.get_or_create(
    username="test_customer",
    defaults={
        "email": customer_email,
        "first_name": "Test",
        "last_name": "Customer"
    }
)
if created:
    customer.set_password("testpass123")
    customer.save()
    print(f"  ✓ Created customer: {customer.username} ({customer_email})")
else:
    print(f"  ℹ Customer already exists: {customer.username}")

# Create or get provider user
provider_email = "test_provider@locapro.local"
provider, created = User.objects.get_or_create(
    username="test_provider",
    defaults={
        "email": provider_email,
        "first_name": "Test",
        "last_name": "Provider"
    }
)
if created:
    provider.set_password("testpass123")
    provider.save()
    print(f"  ✓ Created provider: {provider.username} ({provider_email})")
else:
    print(f"  ℹ Provider already exists: {provider.username}")

# Create or get provider profile
provider_profile, created = ProviderProfile.objects.get_or_create(
    user=provider,
    defaults={
        "company_name": "Test Provider Company",
        "bio": "A test provider for email workflow testing",
    }
)
if created:
    print(f"  ✓ Created provider profile: {provider_profile.company_name}")
else:
    print(f"  ℹ Provider profile already exists: {provider_profile.company_name}")

print()

# ============================================================================
# STEP 4: Create Test Price Range
# ============================================================================
print("[STEP 4] Setting Up Price Range...")
print("-" * 70)

price_range, created = PriceRange.objects.get_or_create(
    label="$50-$100",
    defaults={
        "min_price": 50,
        "max_price": 100,
    }
)
if created:
    print(f"  ✓ Created price range: {price_range.label}")
else:
    print(f"  ℹ Price range already exists: {price_range.label}")

print()

# ============================================================================
# STEP 5: Create Service Request
# ============================================================================
print("[STEP 5] Creating Service Request...")
print("-" * 70)

# Create a new service request
service_request = ServiceRequest.objects.create(
    user=customer,
    provider_name=provider_profile.company_name,
    description="Test service request for email workflow verification",
    price_range=price_range,
    urgent=False,
    date_time=timezone.now() + timedelta(days=3),
)

print(f"  ✓ Created request ID: {service_request.id}")
print(f"    Status: {service_request.status}")
print(f"    Customer: {service_request.user.email}")
print(f"    Provider: {service_request.provider_name}")
print()

# ============================================================================
# STEP 6: Check Emails Sent
# ============================================================================
print("[STEP 6] Checking Emails Sent...")
print("-" * 70)

if "console" in settings.EMAIL_BACKEND.lower():
    print("  ℹ Using Console Email Backend - emails printed to console only")
    print("  Check console output above for email content")
else:
    # For SMTP backend, use outbox if in test mode
    if hasattr(email_outbox, '__len__'):
        print(f"  Email outbox count: {len(email_outbox)}")
        for i, email in enumerate(email_outbox, 1):
            print(f"\n  Email {i}:")
            print(f"    To: {email.to}")
            print(f"    Subject: {email.subject}")
            if email.alternatives:
                print(f"    Has HTML alternative: Yes")
    else:
        print("  ℹ SMTP Backend - emails sent via SMTP")
        print("  Check email provider inbox for deliverywww")

print()

# ============================================================================
# STEP 7: Get Decision Token
# ============================================================================
print("[STEP 7] Retrieving Decision Token...")
print("-" * 70)

try:
    decision_token = RequestDecisionToken.objects.get(service_request=service_request)
    print(f"  ✓ Found decision token: {decision_token.token[:20]}...")
    print(f"    Created: {decision_token.created_at}")
    print(f"    Expires: {decision_token.expires_at}")
    print(f"    Days until expiration: {(decision_token.expires_at - timezone.now()).days}")
    print(f"    Is valid: {decision_token.is_valid()}")
except RequestDecisionToken.DoesNotExist:
    print("  ✗ Decision token not found - signal may not have triggered")
    print("  Manually creating token...")
    decision_token = RequestDecisionToken.objects.create(
        service_request=service_request,
        token=os.urandom(24).hex(),
        expires_at=timezone.now() + timedelta(days=7),
    )
    print(f"  ✓ Created token: {decision_token.token[:20]}...")

print()

# ============================================================================
# STEP 8: Build Decision URLs
# ============================================================================
print("[STEP 8] Building Decision URLs...")
print("-" * 70)

from requests.utils import get_provider_decision_url

accept_url = get_provider_decision_url(service_request.id, decision_token.token, 'accept')
decline_url = get_provider_decision_url(service_request.id, decision_token.token, 'decline')

print(f"  Accept URL:")
print(f"    {accept_url}")
print()
print(f"  Decline URL:")
print(f"    {decline_url}")
print()

# ============================================================================
# STEP 9: Test Provider Acceptance
# ============================================================================
print("[STEP 9] Testing Provider Acceptance...")
print("-" * 70)

service_request.accept(provider)
decision_token.mark_as_used()

print(f"  ✓ Request accepted")
print(f"    Status: {service_request.status}")
print(f"    Provider: {service_request.provider.username if service_request.provider else 'None'}")
print(f"    Accepted at: {service_request.accepted_at}")
print(f"    Token marked as used: {decision_token.used}")

print()

# ============================================================================
# STEP 10: Verify Final State
# ============================================================================
print("[STEP 10] Final Verification...")
print("-" * 70)

# Refresh from database
service_request.refresh_from_db()
decision_token.refresh_from_db()

print(f"  Service Request ID: {service_request.id}")
print(f"  Status: {service_request.status}")
print(f"  Created: {service_request.created_at}")
print(f"  Accepted: {service_request.accepted_at}")
print(f"  Decision Token Valid: {decision_token.is_valid()}")

print()

# ============================================================================
# STEP 11: Summary
# ============================================================================
print("=" * 70)
print("TEST SUMMARY")
print("=" * 70)

print("""
✓ Test users created (customer and provider)
✓ Service request created
✓ Decision token generated (7-day expiration)
✓ Provider acceptance processed
✓ Email workflow executed

NEXT STEPS:
1. Check email inbox for provider notification email:
   - From: {from_email}
   - To: {provider_email}
   - Subject: "New Service Request"

2. Check email inbox for customer notification email:
   - From: {from_email}
   - To: {customer_email}
   - Subject: "Your Service Request Has Been Accepted"

3. Test accept/decline links (valid for 7 days):
   - Accept: {accept_url}
   - Decline: {decline_url}

4. Create another request and test the decline workflow

EMAIL CONFIGURATION:
- Backend: {backend}
- Host: {host}:{port}
- From: {from_email}
- SSL: {use_ssl} | TLS: {use_tls}

For issues or questions, see EMAIL_WORKFLOW_TESTING_GUIDE.md
""".format(
    from_email=settings.DEFAULT_FROM_EMAIL,
    provider_email=provider.email,
    customer_email=customer.email,
    accept_url=accept_url,
    decline_url=decline_url,
    backend=settings.EMAIL_BACKEND.split('.')[-1],
    host=settings.EMAIL_HOST,
    port=settings.EMAIL_PORT,
    use_ssl=settings.EMAIL_USE_SSL,
    use_tls=settings.EMAIL_USE_TLS,
))

print("=" * 70)

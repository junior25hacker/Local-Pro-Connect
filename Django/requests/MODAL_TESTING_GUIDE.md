# Modal Backend Testing Guide

## Overview

This guide provides comprehensive testing procedures for the modal API endpoints and backend logic.

## Setup

### 1. Create Test Data

```bash
# Run from Django directory
python manage.py create_test_data  # If available
# Or manually create test objects in Django shell
python manage.py shell
```

```python
from django.contrib.auth.models import User
from accounts.models import ProviderProfile
from requests.models import ServiceRequest

# Create test users
user = User.objects.create_user('testuser', 'user@test.com', 'password123')
provider = User.objects.create_user('testprovider', 'provider@test.com', 'password123')

# Create provider profile
profile = ProviderProfile.objects.create(
    user=provider,
    company_name='Test Provider',
    service_type='plumbing',
    min_price=50,
    latitude='40.7128',
    longitude='-74.0060'
)

# Create service request
request_obj = ServiceRequest.objects.create(
    user=user,
    provider=provider,
    description='Broken pipe',
    provider_name='Test Provider',
    status='pending'
)
```

### 2. Enable Debug Mode

```python
# Django settings for testing
DEBUG = True
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

## Test Cases

### 1. DECLINE ENDPOINT TESTS

#### Test 1.1: Valid Decline Submission

**Scenario**: Provider declines request with valid reason

**Setup**:
- Create pending request with provider assigned
- Authenticate as provider

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d '{
    "reason": "price",
    "message": "Price is too high for my budget"
  }' \
  -b "sessionid=YOUR_SESSION_ID"
```

**Expected Response** (200 OK):
```json
{
    "status": "success",
    "message": "Request has been declined successfully.",
    "request_id": 1,
    "new_status": "declined"
}
```

**Verification**:
- Response status is 200
- Response contains success status
- Database shows status as 'declined'
- `declined_at` timestamp is set
- `decline_reason` is 'price'
- `decline_message` is stored

#### Test 1.2: Decline Without Message

**Scenario**: Provider declines with reason only (message optional)

**Request**:
```json
{
    "reason": "distance"
}
```

**Expected Response** (200 OK): Success

**Verification**:
- Message field can be empty
- Decline is recorded correctly

#### Test 1.3: Decline With "Other" Reason

**Scenario**: Provider uses "other" reason (should require message in form validation)

**Request**:
```json
{
    "reason": "other",
    "message": "Custom reason here"
}
```

**Expected Response** (200 OK): Success

#### Test 1.4: Authorization Failed - Wrong Provider

**Scenario**: User who is NOT the assigned provider tries to decline

**Setup**:
- Create request with provider A
- Authenticate as provider B (different user)

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -d '{"reason": "price"}' \
  -b "sessionid=PROVIDER_B_SESSION"
```

**Expected Response** (403 Forbidden):
```json
{
    "status": "error",
    "message": "You do not have permission to decline this request.",
    "error_code": "FORBIDDEN"
}
```

#### Test 1.5: Unauthenticated Request

**Scenario**: Anonymous user tries to decline

**Request**: No authentication

**Expected Response** (302 Redirect): Redirected to login

#### Test 1.6: Request Not Found

**Scenario**: Request ID doesn't exist

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/99999/decline/
```

**Expected Response** (404 Not Found):
```json
{
    "status": "error",
    "message": "Service request not found.",
    "error_code": "NOT_FOUND"
}
```

#### Test 1.7: Already Declined

**Scenario**: Request is already declined, try to decline again

**Setup**:
- Create request with status='declined'

**Expected Response** (409 Conflict):
```json
{
    "status": "error",
    "message": "This request has already been declined.",
    "error_code": "CONFLICT"
}
```

#### Test 1.8: Invalid Reason

**Scenario**: Provide invalid reason value

**Request**:
```json
{
    "reason": "invalid_reason",
    "message": "Test"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "status": "error",
    "message": "Validation failed.",
    "error_code": "BAD_REQUEST",
    "errors": {
        "reason": "Select a valid choice. invalid_reason is not one of the available choices."
    }
}
```

#### Test 1.9: Message Exceeds Max Length

**Scenario**: Message longer than 500 characters

**Request**:
```json
{
    "reason": "price",
    "message": "Lorem ipsum dolor sit amet... [>500 chars]"
}
```

**Expected Response** (400 Bad Request):
```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": {
        "message": "Message must not exceed 500 characters."
    }
}
```

#### Test 1.10: Invalid JSON

**Scenario**: Malformed JSON in request body

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -d '{invalid json}'
```

**Expected Response** (400 Bad Request):
```json
{
    "status": "error",
    "message": "Invalid JSON payload.",
    "error_code": "BAD_REQUEST"
}
```

#### Test 1.11: Email Notification Sent

**Scenario**: Verify email is sent to user when request is declined

**Verification**:
- Check Django email console/logs
- Verify recipient is service request creator
- Verify subject contains "Request Update"
- Verify decline reason is in email body
- Verify custom message is in email body

#### Test 1.12: State Database Update

**Scenario**: Verify database state is correct after decline

**Database Checks**:
```python
request = ServiceRequest.objects.get(id=1)
assert request.status == 'declined'
assert request.decline_reason == 'price'
assert request.decline_message == 'Price is too high'
assert request.declined_at is not None
assert request.email_response_timestamp is not None
```

### 2. ACCEPT ENDPOINT TESTS

#### Test 2.1: Valid Accept Submission

**Scenario**: Provider accepts request

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/accept/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -d '{}' \
  -b "sessionid=SESSION"
```

**Expected Response** (200 OK):
```json
{
    "status": "success",
    "message": "Request has been accepted successfully.",
    "request_id": 1,
    "new_status": "accepted"
}
```

#### Test 2.2: Accept With Optional Notes

**Scenario**: Provider accepts with optional notes

**Request**:
```json
{
    "notes": "I can start tomorrow morning"
}
```

**Expected Response** (200 OK): Success

#### Test 2.3: Already Accepted

**Scenario**: Request already accepted, try again

**Expected Response** (409 Conflict):
```json
{
    "status": "error",
    "message": "This request has already been accepted.",
    "error_code": "CONFLICT"
}
```

#### Test 2.4: Cannot Accept Declined Request

**Scenario**: Request is declined, try to accept

**Expected Response** (409 Conflict):
```json
{
    "status": "error",
    "message": "Cannot accept a declined request.",
    "error_code": "CONFLICT"
}
```

#### Test 2.5: Email Notification on Accept

**Verification**:
- Email sent to user
- Subject: "Service Request Accepted"
- Contains provider contact information
- Contains next steps

### 3. EDIT ENDPOINT TESTS

#### Test 3.1: Valid Request Edit

**Scenario**: User edits their pending request

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/edit/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -d '{
    "description": "Updated description",
    "offered_price": 200.00
  }' \
  -b "sessionid=SESSION"
```

**Expected Response** (200 OK):
```json
{
    "status": "success",
    "message": "Request has been updated successfully.",
    "request_id": 1
}
```

#### Test 3.2: Edit Only Description

**Scenario**: Update only description field

**Request**:
```json
{
    "description": "New description"
}
```

**Expected Response** (200 OK): Success

#### Test 3.3: Edit Only Price

**Scenario**: Update only price

**Request**:
```json
{
    "offered_price": 250.00
}
```

**Expected Response** (200 OK): Success

#### Test 3.4: Cannot Edit Accepted Request

**Scenario**: Request is accepted, try to edit

**Expected Response** (409 Conflict):
```json
{
    "status": "error",
    "message": "Cannot edit a accepted request.",
    "error_code": "CONFLICT"
}
```

#### Test 3.5: Cannot Edit Declined Request

**Scenario**: Request is declined, try to edit

**Expected Response** (409 Conflict):
```json
{
    "status": "error",
    "message": "Cannot edit a declined request.",
    "error_code": "CONFLICT"
}
```

#### Test 3.6: Unauthorized Edit - Not Creator

**Scenario**: User who didn't create request tries to edit

**Setup**:
- User A creates request
- Authenticate as User B
- Try to edit User A's request

**Expected Response** (403 Forbidden):
```json
{
    "status": "error",
    "message": "You do not have permission to edit this request.",
    "error_code": "FORBIDDEN"
}
```

#### Test 3.7: Invalid Price

**Scenario**: Edit with invalid (negative) price

**Request**:
```json
{
    "offered_price": -50
}
```

**Expected Response** (400 Bad Request):
```json
{
    "status": "error",
    "message": "Validation failed.",
    "errors": {
        "offered_price": "Ensure this value is greater than or equal to 0."
    }
}
```

### 4. CSRF PROTECTION TESTS

#### Test 4.1: Missing CSRF Token

**Scenario**: POST without CSRF token

**Request**:
```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -d '{"reason": "price"}' \
  -b "sessionid=SESSION"
```

**Expected Response** (403 Forbidden): CSRF verification failed

#### Test 4.2: Invalid CSRF Token

**Scenario**: POST with invalid CSRF token

**Expected Response** (403 Forbidden): CSRF verification failed

### 5. LOGGING TESTS

#### Test 5.1: Successful Operation Logging

**Action**: Perform successful decline

**Expected Logs**:
```
INFO: Request #1 declined by provider testprovider (reason: price)
```

#### Test 5.2: Authorization Failure Logging

**Action**: Attempt unauthorized decline

**Expected Logs**:
```
WARNING: Unauthorized decline attempt for request #1 by user wronguser
```

#### Test 5.3: Error Logging

**Action**: Trigger server error (e.g., corrupt data)

**Expected Logs**:
```
ERROR: Error processing decline for request #1: [error details]
```

## Automated Test Suite

### Python Unit Tests

Create `tests.py`:

```python
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import json
from .models import ServiceRequest
from accounts.models import ProviderProfile

class DeclineAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('user', 'user@test.com', 'pass')
        self.provider = User.objects.create_user('provider', 'provider@test.com', 'pass')
        
        ProviderProfile.objects.create(
            user=self.provider,
            company_name='Test Provider',
            service_type='plumbing',
            min_price=50
        )
        
        self.request_obj = ServiceRequest.objects.create(
            user=self.user,
            provider=self.provider,
            description='Test',
            provider_name='Test Provider',
            status='pending'
        )

    def test_valid_decline(self):
        self.client.login(username='provider', password='pass')
        response = self.client.post(
            f'/requests/api/{self.request_obj.id}/decline/',
            json.dumps({'reason': 'price', 'message': 'Too high'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        
        self.request_obj.refresh_from_db()
        self.assertEqual(self.request_obj.status, 'declined')
        self.assertEqual(self.request_obj.decline_reason, 'price')

    def test_unauthorized_decline(self):
        self.client.login(username='user', password='pass')
        response = self.client.post(
            f'/requests/api/{self.request_obj.id}/decline/',
            json.dumps({'reason': 'price'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 403)
        data = json.loads(response.content)
        self.assertEqual(data['error_code'], 'FORBIDDEN')
```

Run tests:
```bash
python manage.py test requests.tests.DeclineAPITestCase -v 2
```

## Manual Testing Checklist

- [ ] Decline with valid reason
- [ ] Decline with custom message
- [ ] Decline without message
- [ ] Unauthorized decline attempt
- [ ] Decline already declined request
- [ ] Decline accepted request
- [ ] Invalid request ID
- [ ] Malformed JSON
- [ ] Missing CSRF token
- [ ] Email notification sent
- [ ] Accept request
- [ ] Accept with notes
- [ ] Cannot accept declined request
- [ ] Edit pending request
- [ ] Edit only description
- [ ] Edit only price
- [ ] Cannot edit accepted request
- [ ] Unauthorized edit attempt
- [ ] Modal form submits via AJAX
- [ ] Modal shows success message
- [ ] Modal shows error message
- [ ] Modal closes on success
- [ ] Page refreshes after modal close

## Performance Testing

### Load Test - Decline Endpoint

```bash
# Using Apache Bench
ab -n 100 -c 10 -p payload.json -T application/json \
  http://localhost:8000/requests/api/1/decline/

# Expected: Requests/sec > 50
```

### Database Query Test

```python
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import CaptureQueriesContext

with CaptureQueriesContext(connection) as ctx:
    response = client.post('/requests/api/1/decline/', {...})
    print(f"Queries executed: {len(ctx.captured_queries)}")
    # Should be < 5 queries
```

## Browser Testing

### Chrome DevTools

1. Open Network tab
2. Submit decline modal
3. Verify:
   - Request URL is `/requests/api/X/decline/`
   - Request method is POST
   - Status code is 200
   - Response contains success message
   - No JS errors in console

### Firefox

Same steps as Chrome using Firefox Developer Tools

## Troubleshooting Failed Tests

### "CSRF token missing"

**Solution**:
- Ensure Django is not in DEBUG=False with CSRF middleware
- Add CSRF token to request headers

### "Forbidden (403)"

**Solution**:
- Verify user is authenticated
- Verify user is the correct provider/owner
- Check CSRF protection

### "Not Found (404)"

**Solution**:
- Verify request ID exists
- Verify URL routing is correct
- Check that URL pattern matches

### Email Not Sent

**Solution**:
- Check EMAIL_BACKEND setting
- Verify SMTP configuration
- Check email logs

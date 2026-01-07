# Rejection Modal Integration - Test Checklist

## Pre-Testing Setup

- [ ] Run migration: `python manage.py migrate requests`
- [ ] Ensure all static files are loaded
- [ ] Test environment is running locally or on test server

## Unit Tests - Models

```python
# Test ServiceRequest decline method
from requests.models import ServiceRequest

# Create test request
request = ServiceRequest.objects.create(
    user=requester_user,
    provider_name="Plumber",
    description="Fix leaking pipe",
    status='pending'
)

# Test decline with new reasons
request.decline('price', 'Budget too low')
assert request.status == 'declined'
assert request.decline_reason == 'price'
assert request.decline_message == 'Budget too low'

request.decline('distance', '')
assert request.decline_reason == 'distance'

request.decline('time', 'Cannot fit in schedule')
assert request.decline_reason == 'time'

request.decline('other', 'Personal reasons')
assert request.decline_reason == 'other'
```

## Unit Tests - Views

```python
# Test provider_decision view with decline action
from django.test import Client, TestCase
from django.utils import timezone
from requests.models import ServiceRequest, RequestDecisionToken
import secrets

client = Client()

# Create test data
request_obj = ServiceRequest.objects.create(
    user=customer,
    provider_name="Electrician",
    description="Install light fixtures",
)

# Create token
token_obj = RequestDecisionToken.objects.create(
    service_request=request_obj,
    token=secrets.token_urlsafe(32),
    expires_at=timezone.now() + timezone.timedelta(hours=24)
)

# Test decline with rejection_reason
response = client.post(
    f'/requests/decision/{request_obj.id}/decline/{token_obj.token}/',
    {
        'rejection_reason': 'price',
        'rejection_description': 'Out of budget'
    }
)

assert response.status_code == 200
request_obj.refresh_from_db()
assert request_obj.status == 'declined'
assert request_obj.decline_reason == 'price'
assert request_obj.decline_message == 'Out of budget'

# Test backward compatibility with decline_reason
response = client.post(
    f'/requests/decision/{request_obj.id}/decline/{token_obj.token}/',
    {
        'decline_reason': 'distance',
        'decline_message': 'Too far away'
    }
)

# Test invalid reason defaults to 'other'
response = client.post(
    f'/requests/decision/{request_obj.id}/decline/{token_obj.token}/',
    {
        'rejection_reason': 'invalid_reason',
        'rejection_description': 'Test'
    }
)
request_obj.refresh_from_db()
assert request_obj.decline_reason == 'other'
```

## Integration Tests - Email

```python
# Test email sending with rejection reason
from django.test import TestCase
from django.core import mail

# Create and decline request
request_obj = ServiceRequest.objects.create(
    user=customer,
    provider_name="Plumber",
    description="Fix pipe",
)

# Call provider_decision
# ...decline logic...

# Check email was sent
assert len(mail.outbox) == 1
email = mail.outbox[0]

# Verify reason is in email
assert 'Price' in email.body or 'Distance' in email.body
assert 'Reason Category:' in email.body

# Check HTML version
assert 'decline_reason_display' substituted with actual reason
```

## Manual Testing - UI/UX

### Test 1: Modal Display
1. Navigate to confirm_decline.html
2. Request details should display
3. Click "Decline Request" button
4. ✓ Modal should appear with fade-in animation
5. ✓ Modal title shows "Reject Service Request"
6. ✓ Four reason options visible: Distance, Price, Time, Other
7. ✓ Description field hidden initially
8. ✓ Submit button disabled

### Test 2: Reason Selection
1. Click on "Distance" option
2. ✓ Card highlights in green
3. ✓ Checkmark appears
4. ✓ "Selected reason" display appears
5. ✓ Description section becomes visible
6. ✓ Submit button becomes enabled

### Test 3: Description Field
1. Click in description textarea
2. Type some text
3. ✓ Character counter updates (0/500)
4. ✓ Counter color remains gray while under 90%
5. Type until ~450 characters
6. ✓ Counter turns red and bold
7. Type beyond 500 characters
8. ✓ Text is cut off at 500 characters (maxlength)

### Test 4: Form Submission
1. Select any reason
2. Enter description text (or leave blank)
3. Click "Submit Rejection"
4. ✓ Button shows loading state: "⟳ Submitting..."
5. ✓ Success notification appears in top right
6. ✓ After ~2 seconds, form submits to Django
7. ✓ Page redirects to decision_success.html

### Test 5: Modal Close - Escape Key
1. Open modal by clicking "Decline Request"
2. Select a reason (populate form)
3. Press Escape key
4. ✓ Confirmation dialog appears
5. Click Cancel on confirmation
6. ✓ Modal stays open
7. Press Escape again
8. Click OK on confirmation
9. ✓ Modal closes

### Test 6: Modal Close - Cancel Button
1. Open modal
2. Select a reason
3. Click "Cancel" button
4. ✓ Confirmation dialog appears with message
5. Click OK
6. ✓ Modal closes
7. ✓ Returned to confirm_decline.html

### Test 7: Modal Close - X Button
1. Open modal
2. Click X button in top right
3. ✓ Confirmation dialog appears
4. Click OK
5. ✓ Modal closes

### Test 8: Modal Close - Overlay Click
1. Open modal
2. Click on gray overlay background
3. ✓ Confirmation dialog appears
4. Click OK
5. ✓ Modal closes

### Test 9: Go Back Button
1. From confirm_decline.html
2. Click "Go Back" button
3. ✓ Redirects to home page (/)

### Test 10: Validation Error
1. Open modal (don't select a reason)
2. Try to click Submit without selecting reason
3. ✓ Submit button should be disabled (can't click)
4. ✓ OR if somehow clicked, error message appears below reason options
5. ✓ Error message: "Please select a rejection reason before continuing."

### Test 11: Responsive - Tablet (768px)
1. Resize browser to tablet width
2. ✓ Modal adjusts width to 95%
3. ✓ Buttons stack vertically (flex-direction: column-reverse)
4. ✓ Reason cards still visible and selectable
5. ✓ All text readable

### Test 12: Responsive - Mobile (480px)
1. Resize browser to mobile width
2. ✓ Modal fits on screen
3. ✓ Scrollable if content exceeds viewport
4. ✓ Custom scrollbar visible
5. ✓ Buttons remain functional
6. ✓ Text sizes adjusted appropriately

## Email Testing

### Test 1: Email Contains All Data
Trigger decline with:
- Reason: "Price"
- Description: "Budget too low"

Check email contains:
- ✓ Customer's name
- ✓ Provider name
- ✓ Request ID
- ✓ Original request description
- ✓ Requested date/time (if set)
- ✓ Price range (if set)
- ✓ Reason Category: "Price"
- ✓ Additional Details: "Budget too low"
- ✓ "What's Next?" section with suggestions
- ✓ Dashboard link
- ✓ Footer: "This is an automated email from LocaPro"

### Test 2: Email Without Description
Trigger decline with:
- Reason: "Time"
- Description: (empty)

Check email:
- ✓ Reason Category: "Time" still appears
- ✓ Additional Details section doesn't appear (if statement)
- ✓ Email still valid and formatted correctly

### Test 3: Email HTML Rendering
1. Send decline email
2. Check inbox with HTML preview
3. ✓ Red "REQUEST DECLINED" badge visible
4. ✓ Request details in gray box
5. ✓ Reason box with light red background
6. ✓ Blue suggestions box
7. ✓ All colors and styling render correctly

### Test 4: Email Text Version
1. Send decline email
2. View as plain text
3. ✓ All information still readable
4. ✓ Section headers clear (REQUEST DETAILS, REASON FOR DECLINING, etc.)
5. ✓ No HTML artifacts visible

## Database Testing

### Test 1: Decline Reason Choices
```python
from requests.models import ServiceRequest

# Verify choices exist
choices = dict(ServiceRequest.DECLINE_REASON_CHOICES)
assert 'price' in choices
assert 'distance' in choices
assert 'time' in choices
assert 'other' in choices
assert 'no_reason' not in choices  # removed

# Verify labels
assert choices['price'] == 'Price'
assert choices['distance'] == 'Distance'
assert choices['time'] == 'Time'
assert choices['other'] == 'Other'
```

### Test 2: Decline Message Storage
```python
# Create request and decline it
request_obj = ServiceRequest.objects.create(
    user=customer,
    provider_name="Service",
    description="Test"
)

long_message = "A" * 500  # Max reasonable length
request_obj.decline('price', long_message)

# Verify stored correctly
request_obj.refresh_from_db()
assert request_obj.decline_message == long_message
assert len(request_obj.decline_message) == 500
```

### Test 3: Migration Compatibility
```python
# After running migration
from requests.models import ServiceRequest

# Create instance with new choices
request_obj = ServiceRequest.objects.create(
    user=customer,
    provider_name="Service",
    description="Test",
    decline_reason='time'
)

# Verify saves correctly
assert request_obj.decline_reason == 'time'
request_obj.save()
request_obj.refresh_from_db()
assert request_obj.decline_reason == 'time'
```

## Security Testing

### Test 1: Token Validation
1. Get valid decline link
2. Modify token in URL
3. ✓ Should get "Invalid or expired token" error
4. ✓ Request should NOT be declined

### Test 2: Token Expiry
1. Create token with past expiry time
2. Try to use it
3. ✓ Should get "token has expired" error

### Test 3: Token Reuse Prevention
1. Use valid token once (decline request)
2. Try to use same token again
3. ✓ Should get "already been used" error

### Test 4: CSRF Protection
1. Get form from confirm_decline.html
2. Submit without CSRF token
3. ✓ Should get 403 Forbidden error

### Test 5: Correct User Verification
1. Different user should not be able to use provider's token
2. Only way is via email link (token is secure)
3. ✓ Each provider gets unique token per request

## Performance Testing

- [ ] Modal loads without performance issues
- [ ] Modal animations smooth (60 fps)
- [ ] Form submission completes within 2 seconds
- [ ] Email sends without delay
- [ ] Page responds within normal latency

## Browser Compatibility

- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Accessibility Testing

- [ ] Can tab through all form elements
- [ ] Tab order logical (reason options → description → buttons)
- [ ] Submit button disabled state recognizable
- [ ] Keyboard focus visible on all interactive elements
- [ ] Error messages announced to screen readers
- [ ] Modal labeled with aria-label
- [ ] Colors have sufficient contrast
- [ ] Text sizes readable

## Edge Cases

### Test 1: Very Long Description
- Paste 500 characters of text
- ✓ Field accepts all characters
- ✓ Doesn't allow more than 500

### Test 2: Special Characters
- Description with emojis, unicode, HTML entities
- ✓ All saved correctly to database
- ✓ All rendered correctly in email

### Test 3: Rapid Form Submission
- Fill form and click submit multiple times quickly
- ✓ Only processes once
- ✓ Doesn't create duplicate decline records

### Test 4: Network Interruption
- Start submit, disconnect network mid-request
- ✓ User sees error or retry option
- ✓ Request not partially processed

### Test 5: Multiple Tabs
- Open confirm_decline in multiple tabs with same token
- First tab: decline the request
- Second tab: try to decline same request
- ✓ Gets "token already used" error

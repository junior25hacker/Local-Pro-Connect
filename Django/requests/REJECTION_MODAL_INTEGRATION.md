# Rejection Modal Integration Guide

## Overview

The rejection modal has been successfully integrated into the service request workflow. This document outlines all changes made and how the system now works.

## What Changed

### 1. Database Model Updates (`Django/requests/models.py`)

**Updated DECLINE_REASON_CHOICES:**
- Changed from: `('price', 'Price too low')`, `('distance', 'Too far away')`, `('other', 'Other reason')`, `('no_reason', 'No reason provided')`
- Changed to: `('price', 'Price')`, `('distance', 'Distance')`, `('time', 'Time')`, `('other', 'Other')`

This aligns the database choices with the modal options and removes the legacy 'no_reason' option.

**Migration Created:**
- File: `Django/requests/migrations/0003_update_decline_reason_choices.py`
- Run with: `python manage.py migrate requests`

### 2. Views Update (`Django/requests/views.py`)

**Enhanced `provider_decision` view:**

The decline action handler now:
- Accepts both `rejection_reason` and `rejection_description` (from modal) OR legacy `decline_reason` and `decline_message` fields
- Maps modal field names to database field names
- Validates the reason against available choices (defaults to 'other' if invalid)
- Builds a comprehensive email context with:
  - `customer_name`: Full name or username of requester
  - `provider_name`: Name of service being requested
  - `request_id`: ID of the service request
  - `decline_reason`: Stored reason (price, distance, time, other)
  - `decline_reason_display`: Human-readable reason
  - `decline_message`: Additional details provided by provider
  - `declined_at`: Timestamp of decline
  - `dashboard_link`: Link to customer's dashboard

### 3. Template Integration (`Django/requests/templates/requests/confirm_decline.html`)

**Major Changes:**

1. **Button Replacement:**
   - Old: Direct form submission with dropdown
   - New: "Decline Request" button that triggers the modal

2. **Modal Integration:**
   - Full rejection modal embedded in the template
   - Modal displays when "Decline Request" button is clicked
   - Four reason options: Distance, Price, Time, Other
   - Optional description/details field (500 character limit)
   - Character counter for the description field

3. **Form Handling:**
   - Modal form submits via POST to the same provider_decision endpoint
   - Form validates that a reason is selected
   - Loading state shown during submission
   - Form action URL includes request_id, action, and token for security

4. **JavaScript Integration:**
   - Custom initialization script handles modal visibility
   - Integrates with rejection_modal.js for form handling
   - Proper focus management and keyboard support
   - Escape key and overlay click to close modal

### 4. Email Templates Updates

**HTML Template (`Django/requests/templates/emails/request_declined_email.html`):**
- Updated section header: "Reason Category" (instead of just "Reason")
- Styled additional details in a light gray box
- Better visual distinction between reason and details

**Text Template (`Django/requests/templates/emails/request_declined_email.txt`):**
- Updated labels to match HTML template
- Additional Details section for the provider's description
- Improved readability in plain text format

### 5. Rejection Modal Files (Existing)

**CSS (`Django/static/css/rejection_modal.css`):**
- Already included in confirm_decline.html via `{% block extra_css %}`
- No changes needed

**JavaScript (`Django/static/js/rejection_modal.js`):**
- Updated form submission to actually submit to Django (was simulating)
- Shows success message before form submission
- Form submits after 800ms to allow user to see success notification

## Workflow

### For Providers:

1. **View Request:** Provider receives email with request details and decision link
2. **Click Decline Link:** Navigates to confirm_decline.html page showing request details
3. **Click "Decline Request" Button:** Modal appears with reason options
4. **Select Reason:** Provider chooses from Distance, Price, Time, or Other
5. **Add Details (Optional):** Provider can add up to 500 characters of explanation
6. **Submit:** Provider clicks "Submit Rejection" button
7. **Confirmation:** Success message shows briefly, then form submits
8. **Redirect:** Provider sees decision_success.html confirmation page

### For Customers:

1. **Receive Email:** Customer notified that request was declined
2. **View Reason:** Email includes:
   - Reason category (Distance, Price, Time, Other)
   - Provider's additional details if provided
3. **Next Steps:** Suggestions to try other providers or adjust request

## Database Fields

The ServiceRequest model uses:
- `decline_reason` (CharField): Stores the selected reason (price, distance, time, other)
- `decline_message` (TextField): Stores the provider's additional details/description

## Validation

**In Views:**
- Validates that decline_reason is in DECLINE_REASON_CHOICES
- Defaults to 'other' if invalid choice provided
- No validation on decline_message (can be empty)

**In Modal:**
- JavaScript validates that a reason is selected before enabling submit button
- Shows error message if form attempted without selecting reason
- Disabled submit button until reason is selected

**In Form:**
- HTML5 required attribute on radio buttons
- CSRF token protection on form submission

## Token Security

The form action URL includes:
```
{% url 'requests:provider_decision' service_request.id 'decline' token %}
```

This ensures:
- Only the provider with the valid token can decline
- Token is tied to specific request
- Token expires after use or at configured time
- Invalid/expired tokens are rejected by the view

## File Structure

```
Django/
├── requests/
│   ├── models.py (updated DECLINE_REASON_CHOICES)
│   ├── views.py (updated provider_decision view)
│   ├── urls.py (unchanged - already has correct routing)
│   ├── migrations/
│   │   └── 0003_update_decline_reason_choices.py (new)
│   └── templates/
│       ├── requests/
│       │   └── confirm_decline.html (updated with modal)
│       └── emails/
│           ├── request_declined_email.html (updated)
│           └── request_declined_email.txt (updated)
├── static/
│   ├── css/
│   │   └── rejection_modal.css (unchanged)
│   └── js/
│       └── rejection_modal.js (updated form submission)
```

## Migration Instructions

1. **Run Migration:**
   ```bash
   python manage.py migrate requests
   ```

2. **Collect Static Files (if needed):**
   ```bash
   python manage.py collectstatic
   ```

3. **Test the Flow:**
   - Create a service request
   - Send provider decision link to email
   - Click decline link
   - Verify modal appears
   - Select reason and add details
   - Submit and verify email is sent with reason

## Backward Compatibility

The system maintains backward compatibility:
- Old decline_reason/decline_message field names still work
- New rejection_reason/rejection_description names are mapped to same fields
- Existing declined requests continue to work
- Default choice changed from 'no_reason' to 'other' (invalid reason defaults to 'other')

## Testing Checklist

- [ ] Migration runs successfully
- [ ] Modal appears when "Decline Request" button clicked
- [ ] All four reason options selectable
- [ ] Character counter works (0-500)
- [ ] Submit button disabled until reason selected
- [ ] Submit button shows loading state
- [ ] Form submits with correct data
- [ ] Rejection email received by customer
- [ ] Email includes reason category and details
- [ ] Provider redirected to success page
- [ ] Token marked as used after decline
- [ ] Escape key closes modal
- [ ] Overlay click closes modal (with confirmation)
- [ ] Modal responsive on mobile

## Future Enhancements

Potential improvements:
- Analytics/tracking on rejection reasons
- Reason-specific follow-up actions
- Provider ratings/history by rejection reason
- Automated matching algorithm adjustments based on reasons
- Customer re-engagement flow based on decline reason

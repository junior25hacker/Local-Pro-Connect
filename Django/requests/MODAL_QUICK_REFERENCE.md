# Modal Backend - Quick Reference

## API Endpoints Summary

### Decline Request
```
POST /requests/api/{id}/decline/
Authorization: Required (provider only)
CSRF: Required

Request:
{
    "reason": "price|distance|time|other",
    "message": "Optional (max 500 chars)"
}

Response: 200 OK
{
    "status": "success",
    "message": "Request has been declined successfully.",
    "request_id": 1,
    "new_status": "declined"
}

Errors:
- 403: Not the assigned provider
- 404: Request not found
- 409: Already declined/accepted
- 400: Invalid payload
```

### Accept Request
```
POST /requests/api/{id}/accept/
Authorization: Required (provider only)
CSRF: Required

Request:
{
    "notes": "Optional (max 500 chars)"
}

Response: 200 OK
{
    "status": "success",
    "message": "Request has been accepted successfully.",
    "request_id": 1,
    "new_status": "accepted"
}

Errors:
- 403: Not the assigned provider
- 404: Request not found
- 409: Already accepted/declined
```

### Edit Request
```
POST /requests/api/{id}/edit/
Authorization: Required (creator only)
CSRF: Required

Request:
{
    "description": "Updated description",
    "date_time": "2024-01-20T10:30",
    "offered_price": 150.00
}

Response: 200 OK
{
    "status": "success",
    "message": "Request has been updated successfully.",
    "request_id": 1
}

Errors:
- 403: Not the request creator
- 404: Request not found
- 409: Can't edit accepted/declined requests
- 400: Invalid payload
```

## JavaScript Integration

### Get CSRF Token
```javascript
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
```

### Fetch Example
```javascript
fetch(`/requests/api/${requestId}/decline/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        reason: 'price',
        message: 'Too expensive'
    })
})
.then(r => r.json())
.then(data => {
    if (data.status === 'success') {
        console.log('Success!');
    } else {
        console.error(data.message);
    }
});
```

## Django Forms

### RejectionForm
```python
from requests.forms import RejectionForm

form = RejectionForm({
    'reason': 'price',
    'message': 'Custom message'
})

if form.is_valid():
    reason = form.cleaned_data['reason']
    message = form.cleaned_data['message']
```

### AcceptanceForm
```python
from requests.forms import AcceptanceForm

form = AcceptanceForm({
    'notes': 'Optional notes'
})
```

### RequestEditForm
```python
from requests.forms import RequestEditForm

form = RequestEditForm({
    'description': 'New description',
    'offered_price': 150.00
}, instance=request_obj, service_request=request_obj)
```

## Database Models

### ServiceRequest Fields
```python
# Status tracking
status = 'pending|accepted|declined'
created_at = DateTime

# Decline tracking
decline_reason = 'price|distance|time|other'
decline_message = TextField
declined_at = DateTime

# Accept tracking
accepted_at = DateTime

# Email tracking
email_sent_to_provider = Boolean
email_sent_to_user = Boolean
email_response_timestamp = DateTime
```

## State Transitions

### Valid Transitions
```
pending → accepted    (provider accepts)
pending → declined    (provider declines)
pending → pending     (user edits)
accepted → (terminal)
declined → (terminal)
```

### Check Transition
```python
from requests.modal_utils import ModalStateValidator

# Check if can decline
can_decline = ModalStateValidator.can_decline(request.status)

# Check if can accept
can_accept = ModalStateValidator.can_accept(request.status)

# Check if can edit
can_edit = ModalStateValidator.can_edit(request.status)
```

## Authorization Checks

### Decline/Accept
```python
if service_request.provider != user:
    return HttpResponse('Forbidden', status=403)
```

### Edit
```python
if service_request.user != user:
    return HttpResponse('Forbidden', status=403)
```

## Error Handling

### Standard Error Response
```json
{
    "status": "error",
    "message": "Human-readable message",
    "error_code": "ERROR_CODE",
    "errors": {}  // Optional: validation errors
}
```

### Error Codes Reference
```
FORBIDDEN - Permission denied
NOT_FOUND - Resource doesn't exist
CONFLICT - Invalid state transition
BAD_REQUEST - Invalid payload
VALIDATION_ERROR - Form validation failed
SERVER_ERROR - Internal server error
```

## Logging

### Import Logger
```python
import logging
logger = logging.getLogger(__name__)
```

### Log Operations
```python
# Success
logger.info(f"Request #{id} declined by {user.username} (reason: {reason})")

# Warning
logger.warning(f"Unauthorized decline attempt for request #{id}")

# Error
logger.error(f"Error processing decline: {error}", exc_info=True)
```

## Email Templates

### Available Templates
- `request_declined_email.html` - Sent to user on decline
- `request_accepted_email.html` - Sent to user on accept
- `request_confirmation_email.html` - Sent to user on creation

### Template Context
```python
context = {
    'customer_name': str,
    'provider_name': str,
    'request_id': int,
    'description': str,
    'decline_reason': str,
    'decline_message': str,
    'declined_at': datetime,
    'dashboard_link': str,
}
```

## Testing

### Test Decline
```bash
curl -X POST http://localhost:8000/requests/api/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -b "sessionid=SESSION_ID" \
  -d '{"reason": "price", "message": "Too high"}'
```

### Run Unit Tests
```bash
python manage.py test requests.tests -v 2
```

### Check Logs
```bash
tail -f django_runtime.log | grep "declined\|ERROR\|WARNING"
```

## Common Issues

### CSRF Token Missing
```
Error: "Forbidden (CSRF token missing)"
Fix: Add X-CSRFToken header to fetch request
```

### Permission Denied
```
Error: "403 Forbidden - You do not have permission"
Fix: Verify user is the provider/creator of the request
```

### Invalid State
```
Error: "409 Conflict - Request already declined"
Fix: Check request status before attempting operation
```

### Email Not Sent
```
Error: Email not appearing in inbox
Fix: Check EMAIL_BACKEND, SMTP settings, check logs
```

## File Locations

### Code Files
- Views: `Django/requests/views.py` (api_request_decline, api_request_accept, api_request_edit)
- Forms: `Django/requests/forms.py` (RejectionForm, AcceptanceForm, RequestEditForm)
- URLs: `Django/requests/urls.py` (API routes)
- Models: `Django/requests/models.py` (ServiceRequest)
- Utils: `Django/requests/modal_utils.py` (Helpers)

### Frontend Files
- JS: `Django/static/js/rejection_modal.js`
- CSS: `Django/static/css/rejection_modal.css`
- HTML: `Django/requests/templates/requests/rejection_modal.html`

### Email Templates
- Decline: `Django/requests/templates/emails/request_declined_email.html`
- Accept: `Django/requests/templates/emails/request_accepted_email.html`

## Development Workflow

1. **Make Changes**
   - Update views, forms, or models
   - Test locally with curl or browser

2. **Test AJAX**
   - Open browser DevTools
   - Check Network tab for requests
   - Verify JSON responses

3. **Check Logs**
   - Monitor django_runtime.log
   - Look for errors or warnings

4. **Verify Database**
   - Check request status updated
   - Verify timestamps set
   - Confirm decline reason stored

5. **Test Email**
   - Check email console/logs
   - Verify recipient and content
   - Test email links if included

## Performance Tips

1. Use `select_related()` for foreign keys
2. Use `prefetch_related()` for reverse relations
3. Send emails asynchronously
4. Cache frequently accessed data
5. Use database indexes on queried fields

## Security Checklist

- [x] CSRF protection enabled
- [x] Authentication required on all endpoints
- [x] Authorization checks before state changes
- [x] Input validation with Django forms
- [x] SQL injection prevention (Django ORM)
- [x] XSS prevention (template escaping)
- [x] Logging for audit trail
- [x] Error messages don't leak sensitive data

## Useful Commands

```bash
# Run server
python manage.py runserver

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Access Django shell
python manage.py shell

# Run tests
python manage.py test requests.tests

# Check migrations
python manage.py showmigrations

# Reset database (development only)
python manage.py flush

# Create test data
python manage.py shell < create_test_data.py
```

## Resources

- Modal Implementation Guide: `MODAL_IMPLEMENTATION_GUIDE.md`
- Testing Guide: `MODAL_TESTING_GUIDE.md`
- Django Documentation: https://docs.djangoproject.com/
- Django Forms: https://docs.djangoproject.com/en/stable/topics/forms/
- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/

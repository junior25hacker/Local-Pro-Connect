# Professional Backend Logic for Interactive Modals

## Overview

This document describes the professional backend implementation for interactive modals, particularly the Rejection Modal. The implementation includes:

- ✅ Decline API endpoint with AJAX integration
- ✅ Accept API endpoint for provider approval
- ✅ Edit API endpoint for user request modifications
- ✅ Comprehensive form validation
- ✅ RBAC (Role-Based Access Control)
- ✅ Error handling and logging
- ✅ CSRF protection
- ✅ Email notifications via signals
- ✅ State transition validation

## Architecture

### API Endpoints

All endpoints are designed to be RESTful and return JSON responses.

```
POST /api/requests/{id}/decline/    - Provider declines request
POST /api/requests/{id}/accept/     - Provider accepts request
POST /api/requests/{id}/edit/       - User edits their request
```

### Request/Response Format

#### Decline Endpoint

**Request:**
```json
{
    "reason": "price|distance|time|other",
    "message": "Optional custom message (max 500 chars)"
}
```

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Request has been declined successfully.",
    "request_id": 123,
    "new_status": "declined"
}
```

**Error Responses:**
- 400 Bad Request - Invalid payload
- 403 Forbidden - Not the assigned provider
- 404 Not Found - Request doesn't exist
- 409 Conflict - Request already declined/accepted
- 500 Server Error - Internal error

#### Accept Endpoint

**Request:**
```json
{
    "notes": "Optional acceptance notes (max 500 chars)"
}
```

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Request has been accepted successfully.",
    "request_id": 123,
    "new_status": "accepted"
}
```

#### Edit Endpoint

**Request:**
```json
{
    "description": "Updated description",
    "date_time": "2024-01-20T10:30",
    "offered_price": 150.00
}
```

**Success Response (200):**
```json
{
    "status": "success",
    "message": "Request has been updated successfully.",
    "request_id": 123
}
```

## Database Model Updates

The `ServiceRequest` model already includes necessary fields:

```python
# Decline tracking
decline_reason = CharField(choices=DECLINE_REASON_CHOICES)
decline_message = TextField()
declined_at = DateTimeField()

# Status tracking
status = CharField(choices=['pending', 'accepted', 'declined'])
accepted_at = DateTimeField()

# Email tracking
email_sent_to_provider = BooleanField()
email_sent_to_user = BooleanField()
email_response_timestamp = DateTimeField()
```

## Form Validation

### RejectionForm

Validates decline submission:
- `reason` (required): Must be one of ['price', 'distance', 'time', 'other']
- `message` (optional): Max 500 characters
- If reason is 'other', message becomes required

### AcceptanceForm

Validates acceptance submission:
- `notes` (optional): Max 500 characters

### RequestEditForm

Validates request editing:
- `description` (optional): Updated service description
- `date_time` (optional): Updated date/time
- `offered_price` (optional): Updated price offer
- Only allows editing pending requests

## RBAC (Role-Based Access Control)

### Decline/Accept Operations

Only the assigned provider can decline or accept:
```python
if service_request.provider != request.user:
    return 403 Forbidden
```

### Edit Operations

Only the request creator can edit:
```python
if service_request.user != request.user:
    return 403 Forbidden
```

## State Transitions

Valid state transitions:

```
pending → accepted    (provider accepts)
pending → declined    (provider declines)
pending → pending     (user edits)

accepted → (terminal)
declined → (terminal)
```

Invalid transitions return `409 Conflict`.

## Error Handling

### HTTP Status Codes

- **200 OK**: Operation successful
- **400 Bad Request**: Invalid payload or validation failed
- **403 Forbidden**: User lacks permission
- **404 Not Found**: Request doesn't exist
- **409 Conflict**: Invalid state transition
- **500 Internal Server Error**: Server-side error

### Error Response Format

```json
{
    "status": "error",
    "message": "Human-readable error message",
    "error_code": "ERROR_CODE",
    "errors": {}  // Optional: form validation errors
}
```

### Error Codes

- `FORBIDDEN` - User lacks permission
- `NOT_FOUND` - Resource doesn't exist
- `CONFLICT` - Invalid state or operation
- `BAD_REQUEST` - Invalid payload
- `VALIDATION_ERROR` - Form validation failed
- `SERVER_ERROR` - Internal server error

## Email Notifications

Notifications are sent automatically via signals:

### On Decline
- Recipient: Service request creator (user)
- Template: `request_declined_email.html`
- Includes: Reason, custom message, next steps

### On Accept
- Recipient: Service request creator (user)
- Template: `request_accepted_email.html`
- Includes: Provider details, next steps

### On Confirmation
- Recipient: Service request creator (user)
- Template: `request_confirmation_email.html`
- Sent when request is first created

## CSRF Protection

All AJAX requests must include CSRF token:

```javascript
const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
fetch('/api/...', {
    method: 'POST',
    headers: {
        'X-CSRFToken': csrfToken
    }
});
```

## Logging

All operations are logged with appropriate context:

```python
logger.info(f"Request #{request_id} declined by provider {user.username} (reason: {reason})")
logger.warning(f"Unauthorized decline attempt for request #{request_id} by user {user.username}")
logger.error(f"Error processing decline for request #{request_id}: {str(e)}", exc_info=True)
```

## JavaScript Integration

### AJAX Modal Submission

The rejection modal uses native Fetch API for AJAX submission:

```javascript
fetch(`/requests/api/${requestId}/decline/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ reason, message })
})
```

### Error Handling

Modal displays user-friendly error messages for:
- Network errors
- Validation errors
- Permission errors
- State conflicts
- Server errors

### Success Flow

1. Form validation (client-side)
2. AJAX submission
3. Server validation and processing
4. Success notification
5. Modal closes
6. Optional page refresh

## Testing

### Valid Decline Submission

```bash
curl -X POST /api/requests/1/decline/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: TOKEN" \
  -d '{
    "reason": "price",
    "message": "Price too high for my budget"
  }'
```

### Permission Denied

```bash
# User is not the assigned provider
Response: 403 Forbidden
{
    "status": "error",
    "message": "You do not have permission to decline this request.",
    "error_code": "FORBIDDEN"
}
```

### Already Declined

```bash
# Request status is already 'declined'
Response: 409 Conflict
{
    "status": "error",
    "message": "This request has already been declined.",
    "error_code": "CONFLICT"
}
```

### Validation Error

```bash
# Invalid reason provided
Response: 400 Bad Request
{
    "status": "error",
    "message": "Validation failed.",
    "error_code": "BAD_REQUEST",
    "errors": {
        "reason": "Select a valid choice. invalid is not one of the available choices."
    }
}
```

## File Reference

### Backend Files

- **views.py**: API endpoints (`api_request_decline`, `api_request_accept`, `api_request_edit`)
- **forms.py**: Form validation (`RejectionForm`, `AcceptanceForm`, `RequestEditForm`)
- **models.py**: ServiceRequest model with decline fields
- **urls.py**: URL routing for modal endpoints
- **signals.py**: Auto-email sending on state changes
- **email_service.py**: Email composition and delivery
- **modal_utils.py**: Utility functions for modal operations

### Frontend Files

- **static/js/rejection_modal.js**: Modal interactivity and AJAX
- **static/css/rejection_modal.css**: Modal styling
- **templates/requests/rejection_modal.html**: Modal HTML structure

### Email Templates

- **templates/emails/request_declined_email.html**: Decline notification
- **templates/emails/request_accepted_email.html**: Accept notification
- **templates/emails/request_confirmation_email.html**: Confirmation email

## Security Considerations

1. **CSRF Protection**: All POST endpoints require CSRF token
2. **Authentication**: All endpoints require `@login_required`
3. **Authorization**: Verified ownership before state changes
4. **Input Validation**: All inputs validated with Django forms
5. **SQL Injection Prevention**: Using Django ORM
6. **XSS Prevention**: Template auto-escaping enabled
7. **Logging**: Security events logged for audit trail

## Performance Considerations

1. **Async Email**: Emails sent asynchronously via threading
2. **Database Queries**: Using `select_related` and `prefetch_related`
3. **JSON Response**: Minimal payload size
4. **AJAX**: Non-blocking client-side updates
5. **Caching**: Can be implemented for frequently accessed data

## Future Enhancements

1. **Webhooks**: External service integration for state changes
2. **Notifications**: Real-time notifications via WebSocket
3. **Analytics**: Track decline reasons for insights
4. **Bulk Operations**: Decline/accept multiple requests
5. **Scheduling**: Schedule operations for later execution
6. **Audit Trail**: Detailed history of all state changes
7. **A/B Testing**: Test different decline message templates

## Troubleshooting

### CSRF Token Missing

**Issue**: "Forbidden (CSRF token missing)"

**Solution**: Ensure form includes `{% csrf_token %}` and AJAX passes token:
```javascript
headers: { 'X-CSRFToken': csrfToken }
```

### Request Not Found

**Issue**: "Service request not found"

**Solution**: Verify request ID is correct and user has access to the request

### Validation Failed

**Issue**: Form validation errors returned

**Solution**: Check error messages in response and validate input format

### Email Not Sent

**Issue**: Email tracking shows email not sent

**Solution**: 
1. Check email configuration in settings.py
2. Check Django logs for email errors
3. Verify SMTP credentials

## Support

For issues or questions, refer to:
- Django documentation: https://docs.djangoproject.com/
- Django Forms: https://docs.djangoproject.com/en/stable/topics/forms/
- Django Signals: https://docs.djangoproject.com/en/stable/topics/signals/

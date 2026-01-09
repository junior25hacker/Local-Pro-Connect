# Service Request Workflow Implementation

## Overview

This document describes the complete backend implementation for the service request workflow in LocaPro. The system handles the complete lifecycle of service requests from creation through provider acceptance or decline, with automatic email notifications at each step.

## System Architecture

### Database Models

#### 1. **ServiceRequest Model** (Updated)
- **Fields:**
  - `user` (ForeignKey): The user requesting the service
  - `provider` (ForeignKey, optional): The assigned provider
  - `provider_name` (CharField): Name of the requested provider/service
  - `description` (TextField): Description of the requested service
  - `date_time` (DateTimeField, optional): Requested service date/time
  - `price_range` (ForeignKey, optional): Budget range for the service
  - `urgent` (BooleanField): Whether the request is urgent
  - `status` (CharField): One of 'pending', 'accepted', 'declined'
  - `decline_reason` (CharField, optional): Why provider declined
  - `decline_message` (TextField, optional): Additional decline notes
  - `created_at` (DateTimeField): When request was created
  - `accepted_at` (DateTimeField, optional): When provider accepted
  - `declined_at` (DateTimeField, optional): When provider declined

- **Helper Methods:**
  - `accept(provider)`: Mark request as accepted
  - `decline(reason, message)`: Mark request as declined

#### 2. **RequestDecisionToken Model** (New)
Stores secure tokens for provider decision links:
- `service_request` (OneToOneField): Associated service request
- `token` (CharField, unique): The secure token
- `created_at` (DateTimeField): Creation timestamp
- `expires_at` (DateTimeField): When token expires (7 days)
- `used` (BooleanField): Whether token has been used
- `used_at` (DateTimeField, optional): When token was used

- **Helper Methods:**
  - `is_expired()`: Check if token has expired
  - `is_valid()`: Check if token can still be used
  - `mark_as_used()`: Mark token as consumed

## Email Workflow

### Email Templates

All email templates are in `requests/templates/emails/`:

1. **request_to_provider_email** (HTML & TXT) - Sent when request is created
2. **request_accepted_email** (HTML & TXT) - Sent to customer when provider accepts
3. **request_declined_email** (HTML & TXT) - Sent to customer when provider declines

### Signal Handlers

Three automatic signal handlers in `requests/signals.py`:
- Send provider email with decision links
- Send customer acceptance notification
- Send customer decline notification

## API Endpoints

1. **POST /requests/create/** - Create new service request
2. **GET /requests/decision/<request_id>/<action>/<token>/** - Show decision page
3. **POST /requests/decision/<request_id>/<action>/<token>/** - Process decision

## Email Configuration

Set in `Django/locapro_project/settings.py`:
- Development: Console backend (prints to stdout)
- Production: SMTP backend with credentials

## Files Created/Modified

### New Files
- `Django/requests/signals.py`
- `Django/requests/utils.py`
- `Django/requests/migrations/0002_service_request_workflow.py`
- Email templates (6 files)
- Template views (5 files)

### Modified Files
- `Django/requests/models.py`
- `Django/requests/forms.py`
- `Django/requests/views.py`
- `Django/requests/urls.py`
- `Django/requests/admin.py`
- `Django/requests/apps.py`
- `Django/locapro_project/settings.py`

For detailed documentation, see this file.

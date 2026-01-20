# Enhanced Backend API Documentation

This document describes the enhanced backend API endpoints implemented for secure photo storage, request status management, user rating persistence, and filtered request fetching.

## Overview

The enhanced backend provides the following key features:

1. **Secure Photo Storage** with comprehensive file validation (size, type, content)
2. **Request Status Management** following a proper state machine
3. **User Rating Persistence** with detailed feedback tracking
4. **Filtered Request Fetching** by user ID and status
5. **Accept Completion Action** that transitions requests to "Done" status with rating

## Status State Machine

The service request follows this state machine:

```
pending → accepted → completed → done
    ↓
 declined
```

**Valid Transitions:**
- `pending` → `accepted` (Provider action)
- `pending` → `declined` (Provider action)
- `accepted` → `completed` (Provider action)
- `completed` → `done` (User action after rating)

## API Endpoints

### 1. Secure Photo Upload

**Endpoint:** `POST /requests/api/{request_id}/upload-photo/`

**Description:** Upload photos for service requests with comprehensive security validation.

**Authentication:** Required (Request owner only)

**Request:**
```
Content-Type: multipart/form-data

photo: [Image File]
```

**File Validation:**
- **File Types:** JPG, JPEG, PNG, GIF, WEBP
- **Max Size:** 5MB for images
- **Max Dimensions:** 4096x4096 pixels
- **Min Dimensions:** 100x100 pixels
- **Content Validation:** PIL-based image verification

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Photo uploaded successfully.",
  "photo": {
    "id": 123,
    "url": "/media/request_photos/request_photo_1234567890_abcd1234.jpg",
    "file_size": 524288,
    "original_filename": "my_photo.jpg",
    "created_at": "2025-01-12T10:30:00Z"
  }
}
```

**Error Responses:**
- `400` - File validation failed, no file provided
- `403` - Not the request owner
- `404` - Request not found

### 2. Request Status Updates

**Endpoint:** `POST /requests/api/{request_id}/update-status/`

**Description:** Update request status following the state machine rules.

**Authentication:** Required (Role-based permissions)

**Request:**
```json
{
  "status": "accepted|declined|completed|done",
  "reason": "price|distance|time|other",  // For decline only
  "message": "Optional decline message"    // For decline only
}
```

**Permissions:**
- `pending` → `accepted/declined`: Provider only
- `accepted` → `completed`: Provider only  
- `completed` → `done`: User only

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Request status updated to accepted.",
  "status": "accepted",
  "updated_at": "2025-01-12T10:30:00Z"
}
```

**Error Responses:**
- `400` - Invalid status transition, invalid status value
- `403` - Insufficient permissions for transition
- `404` - Request not found

### 3. Filtered Request Fetching

**Endpoint:** `GET /requests/api/filtered/`

**Description:** Fetch service requests with comprehensive filtering options.

**Authentication:** Required

**Query Parameters:**
- `user_id` (optional): Filter by user ID (admin only for other users)
- `status` (optional): Filter by status (pending, accepted, declined, completed, done)
- `role` (required): User's role - "requester" or "provider"
- `limit` (optional): Number of results (default: 50, max: 100)
- `offset` (optional): Offset for pagination (default: 0)

**Examples:**
```
GET /requests/api/filtered/?role=requester&status=accepted&limit=20
GET /requests/api/filtered/?role=provider&status=completed
GET /requests/api/filtered/?role=requester&user_id=123&offset=50
```

**Response (200 OK):**
```json
{
  "success": true,
  "results": [
    {
      "id": 123,
      "description": "Plumbing repair needed",
      "provider_name": "Best Plumbers Inc",
      "offered_price": 150.00,
      "date_time": "2025-01-15T14:00:00Z",
      "urgent": false,
      "status": "accepted",
      "created_at": "2025-01-12T10:00:00Z",
      "accepted_at": "2025-01-12T11:00:00Z",
      "declined_at": null,
      "decline_reason": null,
      "decline_message": null,
      "is_completed": false,
      "is_rated": false,
      "user": {
        "id": 456,
        "name": "John Doe"
      },
      "provider": {
        "id": 789,
        "name": "Best Plumbers Inc",
        "phone": "555-0123",
        "service_type": "Plumbing",
        "rating": 4.5
      },
      "photos": [
        {
          "id": 101,
          "url": "/media/request_photos/photo123.jpg",
          "file_size": 524288,
          "created_at": "2025-01-12T10:05:00Z"
        }
      ],
      "price_range": {
        "id": 1,
        "label": "$100-$200",
        "min_price": 100,
        "max_price": 200
      }
    }
  ],
  "total": 15,
  "count": 10,
  "offset": 0,
  "limit": 50,
  "has_more": true
}
```

**Error Responses:**
- `400` - Invalid parameters
- `403` - Insufficient permissions

### 4. Accept Completion

**Endpoint:** `POST /requests/api/{request_id}/accept-completion/`

**Description:** Accept job completion, change status to "done", and submit rating.

**Authentication:** Required (Request owner only)

**Request:**
```json
{
  "rating": {
    "stars": 5,
    "feedback": "Excellent service! Very professional and timely.",
    "quality_rating": 5,        // Optional (1-5)
    "timeliness_rating": 5,     // Optional (1-5) 
    "communication_rating": 4,  // Optional (1-5)
    "professionalism_rating": 5, // Optional (1-5)
    "would_recommend": true,
    "would_hire_again": true
  }
}
```

**Prerequisites:**
- Request must be in "completed" status
- JobCompletion record must exist
- No existing rating for this request

**Response (200 OK):**
```json
{
  "success": true,
  "message": "Job completion accepted and rating submitted successfully.",
  "status": "done",
  "rating": {
    "id": 456,
    "stars": 5,
    "feedback": "Excellent service! Very professional and timely.",
    "submitted_at": "2025-01-12T10:30:00Z"
  },
  "updated_at": "2025-01-12T10:30:00Z"
}
```

**Side Effects:**
- Request status changes to "done"
- ServiceRating record created
- Provider's overall rating updated automatically

**Error Responses:**
- `400` - Invalid rating data, request not completed, already rated
- `403` - Not the request owner
- `404` - Request not found

## Enhanced Models

### RequestPhoto Model

Enhanced with secure file handling:

```python
class RequestPhoto(models.Model):
    service_request = models.ForeignKey(ServiceRequest, ...)
    image = models.ImageField(
        upload_to=secure_photo_upload_path,
        validators=[validate_request_photo],
        help_text="Upload request photo (JPG, PNG, GIF, WEBP). Max size: 5MB"
    )
    file_size = models.PositiveIntegerField(...)
    original_filename = models.CharField(max_length=255, ...)
    created_at = models.DateTimeField(auto_now_add=True)
```

### ServiceRequest Status Choices

Extended to include new statuses:

```python
STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('declined', 'Declined'),
    ('completed', 'Completed'),  # New
    ('done', 'Done'),            # New
]
```

## File Security Features

### Upload Path Security
- Secure filename generation with timestamps and UUIDs
- Path traversal protection
- Organized storage in `media/request_photos/`

### File Validation
- **Size limits:** 5MB for images, 10MB general
- **Type validation:** MIME type and extension checking
- **Content validation:** PIL-based image verification
- **Dimension limits:** Min 100x100, Max 4096x4096 pixels

### Example Secure Filename Generation
```
Original: "my photo file.jpg"
Secure:   "request_photo_1705123456_a1b2c3d4.jpg"
```

## Error Handling

All endpoints provide consistent error responses:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE"
}
```

**Common Error Codes:**
- `BAD_REQUEST` - Invalid request data
- `FORBIDDEN` - Insufficient permissions
- `VALIDATION_FAILED` - File validation failed
- `INVALID_TRANSITION` - Invalid status transition
- `SERVER_ERROR` - Internal server error

## Testing

Run the comprehensive test suite:

```bash
cd Django
source ../tmp_rovodev_env/bin/activate
python tmp_rovodev_test_enhanced_api.py
```

Tests cover:
- Secure photo upload with various file types and sizes
- Status transitions with proper permissions
- Filtered request fetching with different parameters
- Accept completion workflow with rating submission

## Usage Examples

### Complete Workflow Example

1. **Create service request** (existing functionality)
2. **Upload photos:**
   ```bash
   curl -X POST http://localhost:8000/requests/api/123/upload-photo/ \
        -H "Authorization: Bearer {token}" \
        -F "photo=@repair_photo.jpg"
   ```

3. **Provider accepts request:**
   ```bash
   curl -X POST http://localhost:8000/requests/api/123/update-status/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer {token}" \
        -d '{"status": "accepted"}'
   ```

4. **Provider completes work:**
   ```bash
   curl -X POST http://localhost:8000/requests/api/123/update-status/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer {token}" \
        -d '{"status": "completed"}'
   ```

5. **User accepts completion with rating:**
   ```bash
   curl -X POST http://localhost:8000/requests/api/123/accept-completion/ \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer {token}" \
        -d '{
          "rating": {
            "stars": 5,
            "feedback": "Great work!",
            "would_recommend": true
          }
        }'
   ```

6. **Fetch completed requests:**
   ```bash
   curl "http://localhost:8000/requests/api/filtered/?role=requester&status=done" \
        -H "Authorization: Bearer {token}"
   ```

This enhanced backend provides a robust, secure foundation for the service request management system with comprehensive validation, proper state management, and detailed tracking capabilities.
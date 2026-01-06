# Service Request Export Feature Guide

## Overview
The export functionality allows users to export their service requests to CSV and PDF formats with optional filtering capabilities.

## Features

### CSV Export
- **URL**: `/requests/export/csv/`
- **Method**: GET
- **Authentication**: Required (login_required)
- **Content Type**: `text/csv`
- **Filename Format**: `service_requests_YYYY-MM-DD.csv`

#### Supported Columns
1. Request ID
2. Service Type
3. User Name
4. Provider Name
5. Status
6. Date Created
7. Distance (miles)
8. Price Range
9. Urgent
10. Description (first 200 characters)

### PDF Export
- **URL**: `/requests/export/pdf/`
- **Method**: GET
- **Authentication**: Required (login_required)
- **Content Type**: `application/pdf`
- **Filename Format**: `service_requests_YYYY-MM-DD.pdf`

#### PDF Features
- Professional header with title and generation timestamp
- Summary statistics table showing:
  - Total number of requests
  - Breakdown by status (Pending, Accepted, Declined)
- Detailed requests table with all key information
- Color-coded status badges:
  - Pending: Yellow (#fff3cd)
  - Accepted: Green (#d4edda)
  - Declined: Red (#f8d7da)
- Urgent flag highlighting in red
- Footer with export information

## Query Parameters for Filtering

All export endpoints support the following optional query parameters:

### `status`
Filter by request status
- Values: `pending`, `accepted`, `declined`
- Example: `?status=pending`

### `service_type`
Filter by service type (provider name)
- Values: Any partial string to match
- Example: `?service_type=plumbing`

### `urgent`
Filter by urgency
- Values: `true`, `1`, `yes` (case-insensitive)
- Example: `?urgent=true`

### `date_from`
Filter requests created on or after this date
- Format: ISO date format (YYYY-MM-DD) or ISO datetime format (YYYY-MM-DDTHH:MM:SS)
- Example: `?date_from=2024-01-01`

### `date_to`
Filter requests created on or before this date
- Format: ISO date format (YYYY-MM-DD) or ISO datetime format (YYYY-MM-DDTHH:MM:SS)
- Example: `?date_to=2024-12-31`

## Usage Examples

### Basic CSV Export
```
GET /requests/export/csv/
```

### CSV Export with Filters
```
GET /requests/export/csv/?status=pending&service_type=plumbing&urgent=true
```

### CSV Export with Date Range
```
GET /requests/export/csv/?date_from=2024-01-01&date_to=2024-12-31
```

### Basic PDF Export
```
GET /requests/export/pdf/
```

### PDF Export with Multiple Filters
```
GET /requests/export/pdf/?status=accepted&date_from=2024-06-01&date_to=2024-12-31
```

### Complex Multi-Filter Export
```
GET /requests/export/csv/?status=pending&service_type=electrical&urgent=true&date_from=2024-11-01
```

## Security

### Access Control
- Both endpoints require user authentication (`@login_required`)
- Users can only export their own requests
- Staff users (is_staff=True) can export all requests
- Providers can export requests directed to them

### Data Validation
- Filter parameters are validated and sanitized
- Invalid date formats are silently ignored
- Unknown statuses are skipped
- Maximum of 1,000 records per export to prevent performance issues

## Error Handling

### Empty Results (204 No Content)
When no requests match the filters:
```
Status: 204 No Content
Body: "No requests found matching the selected filters."
```

### Server Errors (500 Internal Server Error)
When an error occurs during export:
```
Status: 500
Body: Error message with details
```

### Missing Libraries
If PDF generation libraries are not installed:
```
Status: 500
Body: "PDF generation libraries not installed. Please install reportlab or weasyprint."
```

## Requirements

### CSV Export
- No additional dependencies (uses Python's built-in `csv` module)

### PDF Export
- Either ReportLab (`reportlab>=4.0.0`) or WeasyPrint (`weasyprint>=60.0`)
- The system automatically tries WeasyPrint first for better styling
- Falls back to ReportLab if WeasyPrint is unavailable
- Falls back to error if both are unavailable

## Installation

### Add to requirements.txt
```
reportlab>=4.0.0
weasyprint>=60.0
```

### Install packages
```bash
pip install -r requirements.txt
```

## Performance Considerations

1. **Record Limit**: Maximum 1,000 records per export
2. **Date Filtering**: Highly recommended for large datasets
3. **Caching**: Export views are not cached (appropriate for dynamic data)

## Implementation Details

### Helper Functions (export_utils.py)

#### `get_filtered_requests(user, filters, is_provider)`
Applies filters to the queryset based on parameters
- Returns a QuerySet limited to 1,000 records

#### `format_request_for_export(service_request)`
Formats a single request for export
- Returns a dictionary with formatted data
- Handles NULL values gracefully

#### `generate_csv_export(requests_list)`
Generates CSV content from a list of requests
- Returns io.StringIO object with CSV data

#### `generate_pdf_export_html(requests_list, export_timestamp)`
Generates HTML content for PDF conversion
- Includes summary statistics
- Includes detailed request table
- Uses professional styling and brand colors

#### `get_export_filename(format_type, timestamp)`
Generates appropriate filename with current date
- Format: `service_requests_YYYY-MM-DD.{csv|pdf}`

## Troubleshooting

### Issue: "No requests found matching the selected filters"
**Solution**: Verify that:
1. You have created service requests
2. Your filter parameters are correct
3. Date filters include the requests you're looking for

### Issue: PDF Generation Fails
**Solution**:
1. Check that reportlab or weasyprint is installed: `pip list | grep -i reportlab` or `pip list | grep -i weasyprint`
2. Install missing dependencies: `pip install reportlab weasyprint`
3. For weasyprint, you may need additional system libraries (check the weasyprint documentation)

### Issue: CSV File Won't Open in Excel
**Solution**: This is usually due to character encoding. The CSV is UTF-8 encoded, which Excel may not automatically detect. Try:
1. In Excel, use "Data" > "From Text" and specify UTF-8 encoding
2. Or open with Google Sheets which handles UTF-8 automatically

### Issue: Filtering Doesn't Work
**Solution**: Ensure query parameters are properly URL-encoded:
1. Spaces should be `%20`
2. Special characters should be URL-encoded
3. Use the browser's native form encoding or `urllib.parse.urlencode()` in Python

## Django URL Configuration

The export endpoints are available at:
- `/requests/export/csv/` - Named route: `requests:export_requests_csv`
- `/requests/export/pdf/` - Named route: `requests:export_requests_pdf`

### Template Usage Example
```django
<!-- CSV Export Link -->
<a href="{% url 'requests:export_requests_csv' %}?status=pending">
    Export Pending as CSV
</a>

<!-- PDF Export Link with Filters -->
<a href="{% url 'requests:export_requests_pdf' %}?status=accepted&date_from=2024-01-01">
    Export Accepted (2024) as PDF
</a>
```

## Future Enhancements

Possible future improvements:
1. Excel (.xlsx) export format
2. JSON export format
3. Scheduled/recurring exports
4. Email delivery of exports
5. Export templates customization
6. Advanced filtering UI
7. Async exports for large datasets
8. Export history tracking

# Professional Filtering System Documentation

## Overview

The professional filtering system provides a comprehensive backend solution for filtering, sorting, and paginating professionals on the Find Service page. It includes:

- **Advanced Filtering** by location, service type, rating, experience, price, and verification status
- **Optimized Database Queries** using Django ORM best practices (select_related, prefetch_related)
- **Pagination** for efficient data loading
- **Flexible Sorting** by multiple criteria
- **Region-aware filtering** with fallback suggestions

## Architecture

### Components

1. **filter_utils.py** - Core filtering logic
   - `ProfessionalFilter` class for building complex queries
   - `serialize_professional()` for converting models to JSON
   - Helper functions for price ranges and region data

2. **views.py** - API endpoint
   - `api_professionals_list()` - Main filtering endpoint
   - Integrates with filter_utils for all filtering operations

3. **professionals_list.js** - Frontend integration
   - Handles user filter interactions
   - Calls backend API with filter parameters
   - Displays results with pagination

## API Endpoint

### Endpoint URL
```
GET /accounts/api/professionals/
GET /accounts/api/filter/  (alias)
```

### Query Parameters

#### Required Parameters
- `service` (string): Service type
  - Values: `all`, `plumbing`, `electrical`, `carpentry`, `cleaning`, `tutoring`, `hvac`, `roofing`, `landscaping`, `painting`, `other`

#### Location Filters (Optional)
- `city` (string): Filter by city (exact match, case-insensitive)
- `state` (string): Filter by state (exact match, case-insensitive)
- `region` (string): Filter by region - Cameroon regions
  - Values: `adamawa`, `centre`, `east`, `far_north`, `littoral`, `north`, `northwest`, `south`, `southwest`, `west`
  - Returns region message if no professionals found
- `location` (string): General location search (searches city, state, business address, company name)

#### Rating & Experience Filters (Optional)
- `min_rating` (float): Minimum rating (0-5)
  - Examples: `3.5`, `4.0`, `4.5`
- `min_experience` (integer): Minimum years of experience
  - Examples: `1`, `5`, `10`
- `min_reviews` (integer): Minimum number of reviews

#### Price Filters (Optional)
- `price_range` (string): Preset price range
  - Values: `budget` ($0-$50), `moderate` ($50-$150), `premium` ($150-$300), `luxury` ($300+)
- `min_price` (float): Minimum price (overrides price_range)
- `max_price` (float): Maximum price (overrides price_range)

#### Other Filters (Optional)
- `verified` (string): Filter verified professionals only
  - Values: `true`, `false` (default: `false`)

#### Sorting & Pagination (Optional)
- `sort` (string): Sort field (default: `rating`)
  - Values: `rating`, `reviews`, `price`, `experience`, `newest`, `name`
- `page` (integer): Page number (default: 1)
- `limit` (integer): Items per page (default: 20, max: 100)

### Example Requests

#### Basic - All plumbers
```
GET /accounts/api/professionals/?service=plumbing
```

#### Filter by location and rating
```
GET /accounts/api/professionals/?service=electrical&region=centre&min_rating=4.0
```

#### Advanced filtering with pagination
```
GET /accounts/api/professionals/?service=carpentry&city=Douala&min_rating=4.5&min_experience=5&sort=experience&page=2&limit=20
```

#### Price filter with sorting
```
GET /accounts/api/professionals/?service=plumbing&price_range=moderate&sort=price&limit=30
```

#### Verified professionals only
```
GET /accounts/api/professionals/?service=electrical&verified=true&min_rating=4.0
```

### Response Format

```json
{
  "success": true,
  "service": "plumbing",
  "professionals": [
    {
      "id": 1,
      "name": "John's Plumbing",
      "company": "John's Plumbing Co.",
      "avatar": "/media/profiles/john.jpg",
      "service": "Plumbing",
      "serviceType": "plumbing",
      "rating": 4.8,
      "reviews": 127,
      "verified": true,
      "experience": 12,
      "price_range": "$$",
      "min_price": 75.00,
      "location": "Douala, Littoral",
      "city": "Douala",
      "state": "Littoral",
      "region": "Littoral",
      "bio": "Professional plumbing services...",
      "phone": "+237123456789",
      "verified_badge": true
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "pages": 3,
    "has_next": true,
    "has_prev": false
  },
  "filters_applied": {
    "service_type": "plumbing",
    "min_rating": 4.0
  }
}
```

### Error Responses

```json
{
  "success": false,
  "error": "Invalid service type: xyz. Valid options are: all, plumbing, electrical, ..."
}
```

### Region Message (When no professionals in selected region)

```json
{
  "success": true,
  "service": "electrical",
  "professionals": [...],
  "pagination": {...},
  "region_message": "No professionals found in West. Showing professionals from other regions.",
  "available_regions": ["Adamawa", "Centre", "Littoral", "North"]
}
```

## Performance Notes

- Base queries: 2-3 per request
- Query time: <100ms typically
- Connection pooling recommended for production
- Default pagination: 20 items per page
- Maximum pagination: 100 items per page

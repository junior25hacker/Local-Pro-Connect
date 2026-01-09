# Professional Filtering System - Code Examples

## Backend Code Examples

### Example 1: Basic Filter Usage

```python
from accounts.filter_utils import ProfessionalFilter, serialize_professional

# Create a filter instance
pfilter = ProfessionalFilter()

# Apply a service filter
pfilter.apply_service_filter('plumbing')

# Get results
results = pfilter.paginate(page=1, limit=10)

# Render results
for professional in results['items']:
    data = serialize_professional(professional)
    print(f"{data['name']} - Rating: {data['rating']}")
```

### Example 2: Chainable Filtering

```python
from accounts.filter_utils import ProfessionalFilter

# Chain multiple filters
pfilter = ProfessionalFilter()
pfilter.apply_service_filter('electrical') \
       .apply_rating_filter(4.0) \
       .apply_verified_filter(True) \
       .apply_experience_filter(5) \
       .sort_by('experience')

# Check how many results
count = pfilter.count()
print(f"Found {count} verified electricians with 4.0+ rating and 5+ years experience")

# Paginate
results = pfilter.paginate(page=1, limit=20)
print(f"Showing {len(list(results['items']))} of {results['total']}")
```

### Example 3: Location-Based Filtering

```python
from accounts.filter_utils import ProfessionalFilter, serialize_professional

# Filter by region with fallback
pfilter = ProfessionalFilter()
pfilter.apply_service_filter('carpentry')
pfilter, region_message = pfilter.apply_location_filter(
    region='centre',
    state=None,
    city='Douala'
)

results = pfilter.paginate(page=1, limit=20)

# Handle no results scenario
if region_message:
    print(f"Message: {region_message}")
    print("Suggested alternatives available")
```

### Example 4: Price Range Filtering

```python
from accounts.filter_utils import ProfessionalFilter

# Preset price range
pfilter1 = ProfessionalFilter()
pfilter1.apply_service_filter('plumbing') \
        .apply_price_filter(price_range='moderate') \
        .sort_by('price')

# Custom price range
pfilter2 = ProfessionalFilter()
pfilter2.apply_service_filter('electrical') \
        .apply_price_filter(min_price=75, max_price=250)

# Mixed approach
pfilter3 = ProfessionalFilter()
pfilter3.apply_price_filter(price_range='budget') \
        .apply_price_filter(max_price=100)  # Override max
```

### Example 5: Complex Multi-Filter Query

```python
from accounts.filter_utils import ProfessionalFilter, serialize_professional

# Advanced filtering scenario
pfilter = ProfessionalFilter()

# Apply all filters
pfilter.apply_service_filter('electrical') \
       .apply_rating_filter(4.5) \
       .apply_experience_filter(10) \
       .apply_verified_filter(True) \
       .apply_review_count_filter(50) \
       .apply_price_filter(price_range='premium') \
       .sort_by('experience')

# Get pagination info
pagination = pfilter.paginate(page=1, limit=20)

# Get applied filters
filters_used = pfilter.get_filters_applied()
print(f"Filters applied: {filters_used}")

# Serialize results
professionals = [
    serialize_professional(p) for p in pagination['items']
]

# Return data
result = {
    'professionals': professionals,
    'pagination': pagination,
    'filters': filters_used
}
```

### Example 6: Building a Custom API Response

```python
from accounts.filter_utils import ProfessionalFilter, serialize_professional, get_region_alternatives

def custom_professionals_endpoint(request):
    """Custom endpoint using the filtering system"""
    
    # Get parameters
    service = request.GET.get('service', 'all')
    min_rating = request.GET.get('min_rating')
    region = request.GET.get('region')
    
    try:
        # Build filter
        pfilter = ProfessionalFilter()
        pfilter.apply_service_filter(service)
        
        if min_rating:
            pfilter.apply_rating_filter(min_rating)
        
        if region:
            pfilter, region_message = pfilter.apply_location_filter(region=region)
        
        pfilter.sort_by('rating')
        
        # Paginate
        page = int(request.GET.get('page', 1))
        pagination = pfilter.paginate(page=page, limit=20)
        
        # Serialize
        professionals = [
            serialize_professional(p) for p in pagination['items']
        ]
        
        # Response
        response = {
            'success': True,
            'professionals': professionals,
            'pagination': pagination,
            'filters': pfilter.get_filters_applied()
        }
        
        # Add region info if applicable
        if region:
            base_filter = ProfessionalFilter()
            base_filter.apply_service_filter(service)
            response['available_regions'] = get_region_alternatives(
                base_filter.get_queryset()
            )
        
        return JsonResponse(response)
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
```

---

## Frontend Code Examples

### Example 1: Basic API Call

```javascript
// Fetch professionals with filters
function fetchProfessionals(service) {
    const params = new URLSearchParams({
        service: service,
        min_rating: 4.0,
        sort: 'rating',
        limit: 20
    });
    
    fetch(`/accounts/api/professionals/?${params}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderResults(data.professionals);
                updatePagination(data.pagination);
            } else {
                showError(data.error);
            }
        })
        .catch(error => console.error('API Error:', error));
}
```

### Example 2: Filter Form with Real-Time Updates

```javascript
// HTML
<select id="serviceFilter">
    <option value="all">All Services</option>
    <option value="plumbing">Plumbing</option>
    <option value="electrical">Electrical</option>
</select>

<select id="ratingFilter">
    <option value="">Any Rating</option>
    <option value="4">4+ Stars</option>
    <option value="4.5">4.5+ Stars</option>
</select>

<select id="sortFilter">
    <option value="rating">Highest Rated</option>
    <option value="experience">Most Experience</option>
    <option value="price">Price: Low to High</option>
</select>

// JavaScript
document.getElementById('serviceFilter').addEventListener('change', applyFilters);
document.getElementById('ratingFilter').addEventListener('change', applyFilters);
document.getElementById('sortFilter').addEventListener('change', applyFilters);

function applyFilters() {
    const service = document.getElementById('serviceFilter').value;
    const minRating = document.getElementById('ratingFilter').value;
    const sort = document.getElementById('sortFilter').value;
    
    const params = new URLSearchParams({
        service: service,
        min_rating: minRating || '',
        sort: sort
    });
    
    fetch(`/accounts/api/professionals/?${params}`)
        .then(response => response.json())
        .then(data => renderResults(data.professionals));
}
```

### Example 3: Pagination Implementation

```javascript
let currentPage = 1;
const itemsPerPage = 20;

function loadPage(pageNumber) {
    const service = 'plumbing';
    const params = new URLSearchParams({
        service: service,
        page: pageNumber,
        limit: itemsPerPage
    });
    
    fetch(`/accounts/api/professionals/?${params}`)
        .then(response => response.json())
        .then(data => {
            renderResults(data.professionals);
            updatePaginationControls(data.pagination);
            currentPage = pageNumber;
        });
}

function updatePaginationControls(pagination) {
    const prevBtn = document.getElementById('prevBtn');
    const nextBtn = document.getElementById('nextBtn');
    const pageInfo = document.getElementById('pageInfo');
    
    prevBtn.disabled = !pagination.has_prev;
    nextBtn.disabled = !pagination.has_next;
    
    pageInfo.textContent = `Page ${pagination.page} of ${pagination.pages}`;
    
    prevBtn.onclick = () => loadPage(pagination.page - 1);
    nextBtn.onclick = () => loadPage(pagination.page + 1);
}
```

### Example 4: Complex Filter Management

```javascript
class ProfessionalFilterManager {
    constructor() {
        this.filters = {
            service: 'all',
            minRating: null,
            minExperience: null,
            priceRange: null,
            verified: false,
            region: null,
            location: null,
            sort: 'rating',
            page: 1,
            limit: 20
        };
    }
    
    setFilter(name, value) {
        this.filters[name] = value;
        this.applyFilters();
    }
    
    clearFilters() {
        this.filters = {
            service: 'all',
            minRating: null,
            minExperience: null,
            priceRange: null,
            verified: false,
            region: null,
            location: null,
            sort: 'rating',
            page: 1,
            limit: 20
        };
        this.applyFilters();
    }
    
    applyFilters() {
        const params = new URLSearchParams();
        
        for (const [key, value] of Object.entries(this.filters)) {
            if (value && value !== 'all' && value !== false) {
                params.append(this.camelToSnake(key), value);
            } else if (value === true) {
                params.append(this.camelToSnake(key), 'true');
            }
        }
        
        this.fetchResults(params);
    }
    
    camelToSnake(str) {
        return str.replace(/[A-Z]/g, letter => `_${letter.toLowerCase()}`);
    }
    
    fetchResults(params) {
        fetch(`/accounts/api/professionals/?${params}`)
            .then(response => response.json())
            .then(data => {
                this.renderResults(data);
                this.logAppliedFilters(data.filters_applied);
            });
    }
    
    renderResults(data) {
        const container = document.getElementById('results');
        container.innerHTML = '';
        
        data.professionals.forEach(pro => {
            const card = this.createProfessionalCard(pro);
            container.appendChild(card);
        });
        
        document.getElementById('resultCount').textContent = 
            `${data.professionals.length} of ${data.pagination.total} professionals`;
    }
    
    createProfessionalCard(professional) {
        const div = document.createElement('div');
        div.className = 'professional-card';
        div.innerHTML = `
            <h3>${professional.name}</h3>
            <p>${professional.service}</p>
            <div class="rating">${professional.rating} ⭐ (${professional.reviews} reviews)</div>
            <p>${professional.location}</p>
            <p>${professional.experience} years experience</p>
            ${professional.verified ? '<span class="verified">✓ Verified</span>' : ''}
        `;
        return div;
    }
    
    logAppliedFilters(filters) {
        console.log('Filters applied:', filters);
    }
}

// Usage
const filterManager = new ProfessionalFilterManager();

document.getElementById('serviceFilter').addEventListener('change', (e) => {
    filterManager.setFilter('service', e.target.value);
});

document.getElementById('clearBtn').addEventListener('click', () => {
    filterManager.clearFilters();
});
```

### Example 5: Error Handling and Loading States

```javascript
class ProfessionalAPI {
    constructor() {
        this.loading = false;
        this.error = null;
    }
    
    async fetchProfessionals(params) {
        this.loading = true;
        this.error = null;
        this.showLoading();
        
        try {
            const response = await fetch(`/accounts/api/professionals/?${params}`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            
            if (!data.success) {
                throw new Error(data.error || 'Unknown error');
            }
            
            this.loading = false;
            this.hideLoading();
            return data;
            
        } catch (error) {
            this.loading = false;
            this.error = error.message;
            this.hideLoading();
            this.showError(error.message);
            throw error;
        }
    }
    
    showLoading() {
        document.getElementById('loading').style.display = 'flex';
        document.getElementById('results').style.display = 'none';
        document.getElementById('error').style.display = 'none';
    }
    
    hideLoading() {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('results').style.display = 'grid';
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error');
        errorDiv.textContent = `Error: ${message}`;
        errorDiv.style.display = 'block';
        document.getElementById('results').style.display = 'none';
    }
}

// Usage with error handling
const api = new ProfessionalAPI();

async function loadProfessionals(service) {
    try {
        const params = new URLSearchParams({ service });
        const data = await api.fetchProfessionals(params);
        renderResults(data.professionals);
    } catch (error) {
        console.error('Failed to load professionals:', error);
    }
}
```

### Example 6: Debounced Location Search

```javascript
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Apply debounce to location input
const locationInput = document.getElementById('locationInput');
const debouncedSearch = debounce((value) => {
    const params = new URLSearchParams({
        service: 'all',
        location: value
    });
    
    fetch(`/accounts/api/professionals/?${params}`)
        .then(response => response.json())
        .then(data => renderResults(data.professionals));
}, 500);  // Wait 500ms after user stops typing

locationInput.addEventListener('input', (e) => {
    debouncedSearch(e.target.value);
});
```

---

## Integration Examples

### Example 1: Django Template Integration

```html
<!-- professionals_list.html -->
<div id="filters">
    <select id="serviceFilter">
        <option value="all">All Services</option>
        {% for value, label in service_choices %}
            <option value="{{ value }}">{{ label }}</option>
        {% endfor %}
    </select>
    
    <input type="text" id="locationInput" placeholder="Enter city or region">
    
    <select id="ratingFilter">
        <option value="">Any Rating</option>
        <option value="3.5">3.5+ Stars</option>
        <option value="4.0">4.0+ Stars</option>
        <option value="4.5">4.5+ Stars</option>
    </select>
</div>

<div id="results"></div>

<script>
    const service = "{{ service_type }}";
    const apiUrl = `/accounts/api/professionals/?service=${service}`;
    
    function loadResults() {
        fetch(apiUrl)
            .then(r => r.json())
            .then(data => {
                document.getElementById('results').innerHTML = 
                    data.professionals.map(p => `
                        <div class="card">
                            <h3>${p.name}</h3>
                            <p>${p.service}</p>
                            <p>Rating: ${p.rating} ⭐</p>
                        </div>
                    `).join('');
            });
    }
    
    loadResults();
</script>
```

### Example 2: URL-Based Filter State

```javascript
// Preserve filters in URL for sharing
function updateFilterURL() {
    const params = new URLSearchParams({
        service: currentFilters.service,
        min_rating: currentFilters.minRating || '',
        region: currentFilters.region || '',
        sort: currentFilters.sort
    });
    
    window.history.replaceState(
        {},
        '',
        `/accounts/professionals/?${params}`
    );
}

// Load filters from URL on page load
function loadFiltersFromURL() {
    const params = new URLSearchParams(window.location.search);
    
    currentFilters.service = params.get('service') || 'all';
    currentFilters.minRating = params.get('min_rating') || '';
    currentFilters.region = params.get('region') || '';
    currentFilters.sort = params.get('sort') || 'rating';
    
    applyFilters();
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadFiltersFromURL);

// Call when filters change
document.addEventListener('filterChanged', updateFilterURL);
```

---

## Testing Examples

### Unit Test Example

```python
# tests.py
from django.test import TestCase
from accounts.filter_utils import ProfessionalFilter, serialize_professional
from accounts.models import ProviderProfile

class ProfessionalFilterTestCase(TestCase):
    
    def setUp(self):
        # Create test data
        self.provider = ProviderProfile.objects.create(
            user=User.objects.create_user('test', 'test@test.com', 'pass'),
            company_name='Test Plumbing',
            service_type='plumbing',
            rating=4.5,
            years_experience=5,
            is_verified=True
        )
    
    def test_service_filter(self):
        pf = ProfessionalFilter()
        pf.apply_service_filter('plumbing')
        self.assertGreater(pf.count(), 0)
    
    def test_rating_filter(self):
        pf = ProfessionalFilter()
        pf.apply_rating_filter(4.0)
        for p in pf.get_queryset():
            self.assertGreaterEqual(p.rating, 4.0)
    
    def test_chaining(self):
        pf = ProfessionalFilter()
        pf.apply_service_filter('plumbing').apply_rating_filter(4.0)
        self.assertGreater(pf.count(), 0)
    
    def test_pagination(self):
        pf = ProfessionalFilter()
        pf.apply_service_filter('all')
        results = pf.paginate(page=1, limit=5)
        self.assertEqual(results['page'], 1)
        self.assertEqual(results['limit'], 5)
    
    def test_serialization(self):
        data = serialize_professional(self.provider)
        self.assertEqual(data['name'], 'Test Plumbing')
        self.assertEqual(data['rating'], 4.5)
        self.assertTrue(data['verified'])
```

### API Test Example

```javascript
// API test with fetch
async function testAPI() {
    const tests = [
        {
            name: 'Basic service filter',
            url: '/accounts/api/professionals/?service=plumbing',
            expected: (data) => data.professionals.length > 0
        },
        {
            name: 'Rating filter',
            url: '/accounts/api/professionals/?service=electrical&min_rating=4.0',
            expected: (data) => data.professionals.every(p => p.rating >= 4.0)
        },
        {
            name: 'Pagination',
            url: '/accounts/api/professionals/?service=all&limit=5',
            expected: (data) => data.professionals.length <= 5
        }
    ];
    
    for (const test of tests) {
        const response = await fetch(test.url);
        const data = await response.json();
        
        if (test.expected(data)) {
            console.log(`✓ ${test.name}`);
        } else {
            console.log(`✗ ${test.name}`);
        }
    }
}

testAPI();
```

---

## Performance Optimization Examples

### Example 1: Caching Filter Results

```python
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# Cache for 5 minutes
@cache_page(60 * 5)
def api_professionals_list(request):
    # View code...
    pass

# Or manual caching
def get_professionals_with_cache(service, filters):
    cache_key = f"professionals_{service}_{hash(str(filters))}"
    
    cached = cache.get(cache_key)
    if cached:
        return cached
    
    # Fetch and cache
    pf = ProfessionalFilter()
    pf.apply_service_filter(service)
    # Apply other filters...
    
    results = pf.paginate(page=1, limit=20)
    cache.set(cache_key, results, 300)  # 5 minutes
    return results
```

### Example 2: Async API Calls

```javascript
// Async/await pattern for cleaner code
async function fetchProfessionalsAsync(service, filters = {}) {
    try {
        const params = new URLSearchParams({ service, ...filters });
        const response = await fetch(`/accounts/api/professionals/?${params}`);
        
        if (!response.ok) throw new Error('Network response error');
        
        const data = await response.json();
        if (!data.success) throw new Error(data.error);
        
        return data;
    } catch (error) {
        console.error('Error fetching professionals:', error);
        throw error;
    }
}

// Usage
const professionals = await fetchProfessionalsAsync('plumbing', {
    min_rating: 4.0,
    region: 'centre'
});
```

---

This comprehensive set of examples covers real-world usage patterns and integration scenarios.

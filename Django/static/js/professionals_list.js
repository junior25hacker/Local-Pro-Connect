/* ===========================
   LOCAL PRO CONNECT - PROFESSIONALS LIST JS
   Dynamic Filtering and Card Rendering
=========================== */

// Mock data for demonstration - Replace with actual API calls
const mockProfessionals = [
    {
        id: 1,
        name: "John Smith",
        company: "Smith Plumbing Co.",
        service: "Plumbing",
        rating: 4.8,
        reviews: 127,
        verified: true,
        experience: 12,
        priceRange: "$$",
        profilePicture: null,
        location: "New York, NY",
        availability: "weekdays"
    },
    {
        id: 2,
        name: "Sarah Johnson",
        company: "Johnson Electric Services",
        service: "Electrical",
        rating: 4.9,
        reviews: 203,
        verified: true,
        experience: 15,
        priceRange: "$$$",
        profilePicture: null,
        location: "Brooklyn, NY",
        availability: "24_7"
    },
    {
        id: 3,
        name: "Mike Davis",
        company: "Davis Carpentry",
        service: "Carpentry",
        rating: 4.6,
        reviews: 89,
        verified: false,
        experience: 8,
        priceRange: "$",
        profilePicture: null,
        location: "Queens, NY",
        availability: "weekends"
    },
    {
        id: 4,
        name: "Emily Rodriguez",
        company: "Clean Queen Services",
        service: "Cleaning",
        rating: 5.0,
        reviews: 156,
        verified: true,
        experience: 10,
        priceRange: "$$",
        profilePicture: null,
        location: "Manhattan, NY",
        availability: "weekdays"
    },
    {
        id: 5,
        name: "David Chen",
        company: "Chen HVAC Solutions",
        service: "HVAC",
        rating: 4.7,
        reviews: 94,
        verified: true,
        experience: 20,
        priceRange: "$$$",
        profilePicture: null,
        location: "Bronx, NY",
        availability: "24_7"
    }
];

// State Management
let allProfessionals = [];
let filteredProfessionals = [];
let currentFilters = {
    serviceType: '',
    price: '',
    rating: '',
    verified: false,
    availability: '',
    region: '',
    location: '',
    radius: 25
};

// DOM Elements
const professionalsGrid = document.getElementById('professionalsGrid');
const loadingState = document.getElementById('loadingState');
const emptyState = document.getElementById('emptyState');
const resultsCount = document.getElementById('resultsCount');
const clearFiltersBtn = document.getElementById('clearFilters');
const sortSelect = document.getElementById('sortBy');

// Filter Elements
const serviceTypeFilter = document.getElementById('serviceTypeFilter');
const priceFilter = document.getElementById('priceFilter');
const ratingFilters = document.querySelectorAll('input[name="rating"]');
const verifiedCheckbox = document.getElementById('verifiedOnly');
const availabilityFilter = document.getElementById('availabilityFilter');
const regionFilter = document.getElementById('regionFilter');
const locationFilter = document.getElementById('locationFilter');
const radiusFilter = document.getElementById('radiusFilter');

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    initializeFilters();
    loadProfessionals();
});

/* ===========================
   INITIALIZATION
=========================== */
function initializeFilters() {
    // Service Type Filter
    serviceTypeFilter.addEventListener('change', function() {
        currentFilters.serviceType = this.value;
        applyFilters();
    });

    // Price Filter
    priceFilter.addEventListener('change', function() {
        currentFilters.price = this.value;
        applyFilters();
    });

    // Rating Filters
    ratingFilters.forEach(radio => {
        radio.addEventListener('change', function() {
            currentFilters.rating = this.value;
            applyFilters();
        });
    });

    // Verified Checkbox
    verifiedCheckbox.addEventListener('change', function() {
        currentFilters.verified = this.checked;
        applyFilters();
    });

    // Availability Filter
    availabilityFilter.addEventListener('change', function() {
        currentFilters.availability = this.value;
        applyFilters();
    });

    // Region Filter
    regionFilter.addEventListener('change', function() {
        currentFilters.region = this.value;
        applyFilters();
    });

    // Location Filter
    locationFilter.addEventListener('input', debounce(function() {
        currentFilters.location = this.value;
        applyFilters();
    }, 500));

    // Radius Filter
    radiusFilter.addEventListener('change', function() {
        currentFilters.radius = this.value;
        applyFilters();
    });

    // Sort Select
    sortSelect.addEventListener('change', function() {
        sortProfessionals(this.value);
        renderProfessionals(filteredProfessionals);
    });

    // Clear Filters
    clearFiltersBtn.addEventListener('click', clearAllFilters);
}

/* ===========================
   DATA LOADING
=========================== */
function loadProfessionals() {
    showLoading();
    
    // Get service from URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    const service = urlParams.get('service') || 'all';
    
    console.log('Loading professionals for service:', service);
    
    // Check if API endpoint exists, otherwise use mock data
    const useAPI = typeof USE_REAL_API !== 'undefined' && USE_REAL_API;
    
    if (useAPI) {
        // Production: Use real API
        // Build query parameters
        const params = new URLSearchParams({
            service: service,
            sort: sortSelect.value || 'rating',
            page: 1,
            limit: 50
        });
        
        // Add optional filters if they're set
        if (currentFilters.rating) params.append('min_rating', currentFilters.rating);
        if (currentFilters.verified) params.append('verified', 'true');
        if (currentFilters.availability) params.append('availability', currentFilters.availability);
        if (currentFilters.region) params.append('region', currentFilters.region);
        if (currentFilters.location) params.append('location', currentFilters.location);
        
        const apiUrl = `/accounts/api/professionals/?${params.toString()}`;
        console.log('Fetching from API:', apiUrl);
        
        fetch(apiUrl)
            .then(response => {
                console.log('API Response status:', response.status);
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('API Response data:', data);
                if (!data.success) {
                    console.error('API Error:', data.error);
                    showEmptyWithMessage(data.error || 'Failed to load professionals');
                    hideLoading();
                    return;
                }
                allProfessionals = data.professionals || [];
                filteredProfessionals = [...allProfessionals];
                console.log(`Loaded ${allProfessionals.length} professionals`);
                
                // Display region message if provided
                if (data.region_message) {
                    displayRegionMessage(data.region_message, data.available_regions);
                } else {
                    hideRegionMessage();
                }
                
                renderProfessionals(filteredProfessionals);
                hideLoading();
            })
            .catch(error => {
                console.error('Error loading professionals:', error);
                showEmptyWithMessage('Unable to load professionals. Please try again later.');
                hideLoading();
            });
    } else {
        // Development: Use mock data
        console.log('Using mock data (USE_REAL_API is false)');
        loadMockData(service);
    }
}

function loadMockData(service) {
    setTimeout(() => {
        allProfessionals = service === 'all' ? mockProfessionals : 
            mockProfessionals.filter(p => p.service.toLowerCase() === service.toLowerCase());
        
        filteredProfessionals = [...allProfessionals];
        renderProfessionals(filteredProfessionals);
        hideLoading();
    }, 800);
}

/* ===========================
   FILTERING LOGIC
=========================== */
function applyFilters() {
    filteredProfessionals = allProfessionals.filter(professional => {
        // Service Type Filter
        if (currentFilters.serviceType) {
            // Check both 'service' and 'serviceType' properties for compatibility
            const professionalService = (professional.serviceType || professional.service || '').toLowerCase();
            if (professionalService !== currentFilters.serviceType.toLowerCase()) return false;
        }

        // Price Filter
        if (currentFilters.price) {
            const priceMap = { 'budget': '$', 'moderate': '$$', 'premium': '$$$', 'luxury': '$$$$' };
            if (professional.priceRange !== priceMap[currentFilters.price]) return false;
        }

        // Rating Filter
        if (currentFilters.rating) {
            if (professional.rating < parseFloat(currentFilters.rating)) return false;
        }

        // Verified Filter
        if (currentFilters.verified && !professional.verified) return false;

        // Availability Filter
        if (currentFilters.availability && professional.availability !== currentFilters.availability) return false;

        // Region Filter
        if (currentFilters.region) {
            const professionalRegion = (professional.region || professional.state || '').toLowerCase();
            if (professionalRegion !== currentFilters.region.toLowerCase()) return false;
        }

        // Location Filter (simple text match - in production use geolocation)
        if (currentFilters.location) {
            const locationLower = currentFilters.location.toLowerCase();
            const professionalLocation = (professional.location || professional.city || '').toLowerCase();
            if (!professionalLocation.includes(locationLower)) return false;
        }

        return true;
    });

    sortProfessionals(sortSelect.value);
    renderProfessionals(filteredProfessionals);
}

/* ===========================
   SORTING LOGIC
=========================== */
function sortProfessionals(sortBy) {
    switch(sortBy) {
        case 'rating':
            filteredProfessionals.sort((a, b) => b.rating - a.rating);
            break;
        case 'reviews':
            filteredProfessionals.sort((a, b) => b.reviews - a.reviews);
            break;
        case 'price_low':
            filteredProfessionals.sort((a, b) => a.priceRange.length - b.priceRange.length);
            break;
        case 'price_high':
            filteredProfessionals.sort((a, b) => b.priceRange.length - a.priceRange.length);
            break;
        case 'experience':
            filteredProfessionals.sort((a, b) => b.experience - a.experience);
            break;
        default:
            filteredProfessionals.sort((a, b) => b.rating - a.rating);
    }
}

/* ===========================
   RENDERING
=========================== */
function renderProfessionals(professionals) {
    if (professionals.length === 0) {
        showEmpty();
        return;
    }

    hideEmpty();
    professionalsGrid.innerHTML = '';
    resultsCount.textContent = professionals.length;

    professionals.forEach(professional => {
        const card = createProfessionalCard(professional);
        professionalsGrid.appendChild(card);
    });
}

function createProfessionalCard(professional) {
    const template = document.getElementById('professionalCardTemplate');
    const card = template.content.cloneNode(true);

    // Avatar - handle both 'avatar' and 'profilePicture' field names
    const avatarImg = card.querySelector('.avatar-img');
    const avatarPlaceholder = card.querySelector('.avatar-placeholder');
    const avatarUrl = professional.avatar || professional.profilePicture;
    
    if (avatarUrl) {
        avatarImg.src = avatarUrl;
        avatarImg.style.display = 'block';
        avatarPlaceholder.style.display = 'none';
    } else {
        avatarImg.style.display = 'none';
        avatarPlaceholder.style.display = 'flex';
    }

    // Verified Badge
    const verifiedBadge = card.querySelector('.verified-badge');
    if (professional.verified) {
        verifiedBadge.style.display = 'inline-flex';
    }

    // Professional Info
    card.querySelector('.professional-name').textContent = professional.name;
    // Handle both 'company' and direct data model where company_name is used as name
    const companyName = professional.company || '';
    card.querySelector('.professional-company').textContent = companyName;
    card.querySelector('.service-text').textContent = professional.service;

    // Rating
    const starsContainer = card.querySelector('.stars');
    starsContainer.innerHTML = generateStars(professional.rating);
    card.querySelector('.rating-number').textContent = professional.rating.toFixed(1);
    card.querySelector('.reviews-count').textContent = `(${professional.reviews} reviews)`;

    // Details
    card.querySelector('.experience-text').textContent = `${professional.experience} years exp.`;
    // Handle both 'price_range' and 'priceRange' field names
    const priceRange = professional.price_range || professional.priceRange || '$$';
    card.querySelector('.price-text').textContent = priceRange;

    // Action Buttons
    const requestBtn = card.querySelector('.request-btn');
    const viewProfileBtn = card.querySelector('.view-profile-btn');

    requestBtn.addEventListener('click', () => handleRequestService(professional));
    viewProfileBtn.addEventListener('click', () => handleViewProfile(professional));

    return card;
}

function generateStars(rating) {
    let starsHTML = '';
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;

    for (let i = 0; i < fullStars; i++) {
        starsHTML += '<i class="fas fa-star"></i>';
    }

    if (hasHalfStar) {
        starsHTML += '<i class="fas fa-star-half-alt"></i>';
    }

    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);
    for (let i = 0; i < emptyStars; i++) {
        starsHTML += '<i class="far fa-star"></i>';
    }

    return starsHTML;
}

/* ===========================
   ACTION HANDLERS
=========================== */
function handleRequestService(professional) {
    // Redirect to request form with professional pre-selected
    console.log('Request service from:', professional.name);
    window.location.href = `/requests/create/?provider=${professional.id}`;
}

function handleViewProfile(professional) {
    // Redirect to professional's profile page
    console.log('View profile:', professional.name);
    window.location.href = `/accounts/professionals/${professional.id}/`;
}

/* ===========================
   CLEAR FILTERS
=========================== */
function clearAllFilters() {
    // Reset all filter values
    currentFilters = {
        serviceType: '',
        price: '',
        rating: '',
        verified: false,
        availability: '',
        region: '',
        location: '',
        radius: 25
    };

    // Reset UI elements
    serviceTypeFilter.value = '';
    priceFilter.value = '';
    ratingFilters.forEach(radio => {
        radio.checked = radio.value === '';
    });
    verifiedCheckbox.checked = false;
    availabilityFilter.value = '';
    regionFilter.value = '';
    locationFilter.value = '';
    radiusFilter.value = '25';

    // Reapply filters (which will show all)
    applyFilters();
}

// Expose to global scope for inline onclick
window.clearAllFilters = clearAllFilters;

/* ===========================
   UI STATE MANAGEMENT
=========================== */
function showLoading() {
    loadingState.style.display = 'flex';
    professionalsGrid.style.display = 'none';
    emptyState.style.display = 'none';
}

function hideLoading() {
    loadingState.style.display = 'none';
    professionalsGrid.style.display = 'grid';
}

function showEmpty() {
    professionalsGrid.style.display = 'none';
    emptyState.style.display = 'flex';
    resultsCount.textContent = '0';
}

function showEmptyWithMessage(message) {
    professionalsGrid.style.display = 'none';
    emptyState.style.display = 'flex';
    resultsCount.textContent = '0';
    
    // Update empty state message if provided
    const emptyStateText = emptyState.querySelector('p');
    if (emptyStateText && message) {
        emptyStateText.textContent = message;
    }
}

function hideEmpty() {
    emptyState.style.display = 'none';
    professionalsGrid.style.display = 'grid';
}

/* ===========================
   REGION MESSAGE DISPLAY
=========================== */
function displayRegionMessage(message, availableRegions) {
    // Create or update region message banner
    let banner = document.getElementById('regionMessageBanner');
    
    if (!banner) {
        banner = document.createElement('div');
        banner.id = 'regionMessageBanner';
        banner.className = 'region-message-banner';
        
        // Insert before results header
        const resultsHeader = document.querySelector('.results-header');
        if (resultsHeader) {
            resultsHeader.parentNode.insertBefore(banner, resultsHeader);
        }
    }
    
    // Format available regions
    let regionsText = '';
    if (availableRegions && availableRegions.length > 0) {
        regionsText = `<br><strong>Available in:</strong> ${availableRegions.join(', ')}`;
    }
    
    banner.innerHTML = `
        <div class="region-message-content">
            <i class="fas fa-info-circle"></i>
            <div class="region-message-text">
                <p>${message}${regionsText}</p>
            </div>
            <button class="close-region-message" onclick="hideRegionMessage()">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    banner.style.display = 'block';
}

function hideRegionMessage() {
    const banner = document.getElementById('regionMessageBanner');
    if (banner) {
        banner.style.display = 'none';
    }
}

// Expose to global scope
window.hideRegionMessage = hideRegionMessage;

/* ===========================
   UTILITY FUNCTIONS
=========================== */
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

/* ===========================
   EXPORT FOR TESTING (Optional)
=========================== */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        applyFilters,
        sortProfessionals,
        createProfessionalCard,
        generateStars
    };
}

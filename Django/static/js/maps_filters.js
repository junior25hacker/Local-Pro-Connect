/**
 * LOCAL PRO CONNECT - GOOGLE MAPS & ADVANCED FILTERS
 * Premium Maps Integration and Filtering System
 */

// ==============================================
// GOOGLE MAPS INTEGRATION (Leaflet.js - Free Alternative)
// ==============================================

let mapInstance = null;
let detailMapInstance = null;
let markers = [];

/**
 * Initialize Leaflet map for list view
 */
function initializeListMap(requestsData) {
    const mapContainer = document.getElementById('map');
    if (!mapContainer || !requestsData || requestsData.length === 0) return;

    // Create map centered on first request
    const centerLat = requestsData[0].userLat || 40.7128;
    const centerLng = requestsData[0].userLng || -74.0060;

    mapInstance = L.map('map').setView([centerLat, centerLng], 11);

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(mapInstance);

    // Add markers for each request
    requestsData.forEach((request, index) => {
        if (request.userLat && request.userLng && request.providerLat && request.providerLng) {
            // User marker (blue)
            const userMarker = L.marker([request.userLat, request.userLng], {
                icon: createCustomIcon('user')
            }).addTo(mapInstance);

            userMarker.bindPopup(`
                <div style="font-family: inherit;">
                    <strong style="color: #0052CC;">Request #${request.id}</strong><br>
                    <span style="color: #4A5568;">User Location</span><br>
                    <span style="font-size: 12px;">${request.userAddress}</span>
                </div>
            `);

            // Provider marker (green)
            const providerMarker = L.marker([request.providerLat, request.providerLng], {
                icon: createCustomIcon('provider')
            }).addTo(mapInstance);

            providerMarker.bindPopup(`
                <div style="font-family: inherit;">
                    <strong style="color: #17B890;">Provider</strong><br>
                    <span style="color: #4A5568;">${request.providerName}</span><br>
                    <span style="font-size: 12px;">${request.providerAddress}</span>
                </div>
            `);

            // Draw line between user and provider
            const line = L.polyline([
                [request.userLat, request.userLng],
                [request.providerLat, request.providerLng]
            ], {
                color: '#0052CC',
                weight: 3,
                opacity: 0.6,
                dashArray: '5, 10'
            }).addTo(mapInstance);

            line.bindPopup(`
                <div style="font-family: inherit; text-align: center;">
                    <strong style="color: #0052CC;">Distance</strong><br>
                    <span style="font-size: 18px; font-weight: 700; color: #17B890;">
                        ${request.distance} miles
                    </span>
                </div>
            `);

            markers.push({ userMarker, providerMarker, line, requestId: request.id });
        }
    });

    // Fit map to show all markers
    if (markers.length > 0) {
        const bounds = L.latLngBounds(
            markers.flatMap(m => [
                m.userMarker.getLatLng(),
                m.providerMarker.getLatLng()
            ])
        );
        mapInstance.fitBounds(bounds, { padding: [50, 50] });
    }
}

/**
 * Initialize map for detail view (single request)
 */
function initializeDetailMap(userLat, userLng, providerLat, providerLng, userAddress, providerAddress, distance) {
    const mapContainer = document.getElementById('detail-map');
    if (!mapContainer) return;

    // Create map centered between user and provider
    const centerLat = (parseFloat(userLat) + parseFloat(providerLat)) / 2;
    const centerLng = (parseFloat(userLng) + parseFloat(providerLng)) / 2;

    detailMapInstance = L.map('detail-map').setView([centerLat, centerLng], 12);

    // Add OpenStreetMap tiles with custom style
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 19
    }).addTo(detailMapInstance);

    // User marker (home icon)
    const userMarker = L.marker([userLat, userLng], {
        icon: createCustomIcon('user')
    }).addTo(detailMapInstance);

    userMarker.bindPopup(`
        <div style="font-family: inherit; min-width: 200px;">
            <strong style="color: #0052CC; font-size: 16px;">🏠 User Location</strong><br>
            <span style="color: #4A5568; margin-top: 8px; display: block;">${userAddress}</span>
        </div>
    `).openPopup();

    // Provider marker (business icon)
    const providerMarker = L.marker([providerLat, providerLng], {
        icon: createCustomIcon('provider')
    }).addTo(detailMapInstance);

    providerMarker.bindPopup(`
        <div style="font-family: inherit; min-width: 200px;">
            <strong style="color: #17B890; font-size: 16px;">🏢 Provider Location</strong><br>
            <span style="color: #4A5568; margin-top: 8px; display: block;">${providerAddress}</span>
        </div>
    `);

    // Draw route line
    const routeLine = L.polyline([
        [userLat, userLng],
        [providerLat, providerLng]
    ], {
        color: '#0052CC',
        weight: 4,
        opacity: 0.8,
        dashArray: '10, 15',
        smoothFactor: 1
    }).addTo(detailMapInstance);

    // Add distance label at midpoint
    const midLat = (parseFloat(userLat) + parseFloat(providerLat)) / 2;
    const midLng = (parseFloat(userLng) + parseFloat(providerLng)) / 2;

    const distanceIcon = L.divIcon({
        className: 'distance-label',
        html: `
            <div style="
                background: linear-gradient(135deg, #17B890 0%, #139a77 100%);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: 700;
                font-size: 14px;
                box-shadow: 0 4px 12px rgba(23, 184, 144, 0.4);
                border: 3px solid white;
                white-space: nowrap;
            ">
                📍 ${distance} miles
            </div>
        `,
        iconSize: [120, 40],
        iconAnchor: [60, 20]
    });

    L.marker([midLat, midLng], { icon: distanceIcon }).addTo(detailMapInstance);

    // Fit map to show both markers with padding
    const bounds = L.latLngBounds([
        [userLat, userLng],
        [providerLat, providerLng]
    ]);
    detailMapInstance.fitBounds(bounds, { padding: [100, 100] });
}

/**
 * Create custom icon for markers
 */
function createCustomIcon(type) {
    const colors = {
        user: '#0052CC',
        provider: '#17B890'
    };
    
    const icons = {
        user: '🏠',
        provider: '🏢'
    };

    return L.divIcon({
        className: 'custom-marker',
        html: `
            <div style="
                background: ${colors[type]};
                width: 40px;
                height: 40px;
                border-radius: 50% 50% 50% 0;
                transform: rotate(-45deg);
                border: 4px solid white;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                display: flex;
                align-items: center;
                justify-content: center;
            ">
                <span style="
                    transform: rotate(45deg);
                    font-size: 20px;
                ">${icons[type]}</span>
            </div>
        `,
        iconSize: [40, 40],
        iconAnchor: [20, 40],
        popupAnchor: [0, -40]
    });
}

// ==============================================
// VIEW TOGGLE (List View / Map View)
// ==============================================

function initializeViewToggle() {
    const listViewBtn = document.getElementById('list-view-btn');
    const mapViewBtn = document.getElementById('map-view-btn');
    const requestsGrid = document.querySelector('.requests-grid');
    const mapContainer = document.getElementById('map-container');

    if (!listViewBtn || !mapViewBtn) return;

    listViewBtn.addEventListener('click', function() {
        listViewBtn.classList.add('active');
        mapViewBtn.classList.remove('active');
        if (requestsGrid) requestsGrid.style.display = 'grid';
        if (mapContainer) mapContainer.style.display = 'none';
    });

    mapViewBtn.addEventListener('click', function() {
        mapViewBtn.classList.add('active');
        listViewBtn.classList.remove('active');
        if (requestsGrid) requestsGrid.style.display = 'none';
        if (mapContainer) {
            mapContainer.style.display = 'block';
            // Invalidate size to fix map rendering issues
            if (mapInstance) {
                setTimeout(() => mapInstance.invalidateSize(), 100);
            }
        }
    });
}

// ==============================================
// ADVANCED FILTERS
// ==============================================

let activeFilters = {
    distance: 999,
    serviceTypes: [],
    dateFrom: null,
    dateTo: null,
    status: 'all',
    sortBy: 'date-desc'
};

/**
 * Initialize filter panel
 */
function initializeFilters() {
    const filtersToggleBtn = document.getElementById('filters-toggle-btn');
    const filtersPanel = document.getElementById('filters-panel');
    const clearFiltersBtn = document.getElementById('clear-filters-btn');

    if (!filtersToggleBtn || !filtersPanel) return;

    // Toggle filters panel
    filtersToggleBtn.addEventListener('click', function() {
        filtersPanel.classList.toggle('show');
        this.classList.toggle('active');
    });

    // Clear all filters
    if (clearFiltersBtn) {
        clearFiltersBtn.addEventListener('click', clearAllFilters);
    }

    // Initialize individual filters
    initializeDistanceFilter();
    initializeServiceTypeFilter();
    initializeDateFilters();
    initializeStatusFilter();
    initializeSortControls();
}

/**
 * Initialize distance range slider
 */
function initializeDistanceFilter() {
    const distanceSlider = document.getElementById('distance-slider');
    const distanceDisplay = document.getElementById('distance-value-display');

    if (!distanceSlider) return;

    distanceSlider.addEventListener('input', function() {
        const value = this.value;
        activeFilters.distance = parseInt(value);
        
        let displayText = '';
        if (value >= 100) {
            displayText = 'All Distances';
        } else {
            displayText = `Within ${value} miles`;
        }
        
        if (distanceDisplay) {
            distanceDisplay.textContent = displayText;
        }

        applyFilters();
        updateActiveFiltersBadge();
    });
}

/**
 * Initialize service type checkboxes
 */
function initializeServiceTypeFilter() {
    const checkboxes = document.querySelectorAll('.service-type-checkbox');
    
    checkboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            const serviceType = this.value;
            
            if (this.checked) {
                if (!activeFilters.serviceTypes.includes(serviceType)) {
                    activeFilters.serviceTypes.push(serviceType);
                }
            } else {
                activeFilters.serviceTypes = activeFilters.serviceTypes.filter(t => t !== serviceType);
            }

            applyFilters();
            updateActiveFiltersBadge();
        });
    });
}

/**
 * Initialize date range filters
 */
function initializeDateFilters() {
    const quickDateBtns = document.querySelectorAll('.quick-date-btn');
    const dateFromInput = document.getElementById('date-from');
    const dateToInput = document.getElementById('date-to');

    // Quick date filters
    quickDateBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            quickDateBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            const filter = this.dataset.filter;
            const today = new Date();
            let fromDate = null;

            switch(filter) {
                case 'today':
                    fromDate = new Date(today.setHours(0, 0, 0, 0));
                    break;
                case 'week':
                    fromDate = new Date(today.setDate(today.getDate() - 7));
                    break;
                case 'month':
                    fromDate = new Date(today.setMonth(today.getMonth() - 1));
                    break;
                case 'all':
                    fromDate = null;
                    break;
            }

            activeFilters.dateFrom = fromDate;
            activeFilters.dateTo = filter === 'all' ? null : new Date();

            if (dateFromInput && fromDate) {
                dateFromInput.value = fromDate.toISOString().split('T')[0];
            }
            if (dateToInput && activeFilters.dateTo) {
                dateToInput.value = activeFilters.dateTo.toISOString().split('T')[0];
            }

            applyFilters();
            updateActiveFiltersBadge();
        });
    });

    // Custom date inputs
    if (dateFromInput) {
        dateFromInput.addEventListener('change', function() {
            activeFilters.dateFrom = this.value ? new Date(this.value) : null;
            quickDateBtns.forEach(b => b.classList.remove('active'));
            applyFilters();
            updateActiveFiltersBadge();
        });
    }

    if (dateToInput) {
        dateToInput.addEventListener('change', function() {
            activeFilters.dateTo = this.value ? new Date(this.value) : null;
            quickDateBtns.forEach(b => b.classList.remove('active'));
            applyFilters();
            updateActiveFiltersBadge();
        });
    }
}

/**
 * Initialize status filter
 */
function initializeStatusFilter() {
    const statusRadios = document.querySelectorAll('input[name="status-filter"]');
    
    statusRadios.forEach(radio => {
        radio.addEventListener('change', function() {
            activeFilters.status = this.value;
            applyFilters();
            updateActiveFiltersBadge();
        });
    });
}

/**
 * Initialize sort controls
 */
function initializeSortControls() {
    const sortBtns = document.querySelectorAll('.sort-btn');
    
    sortBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            sortBtns.forEach(b => b.classList.remove('active'));
            this.classList.add('active');

            activeFilters.sortBy = this.dataset.sort;
            applyFilters();
        });
    });
}

/**
 * Apply all active filters to request cards
 */
function applyFilters() {
    const cards = Array.from(document.querySelectorAll('.request-card'));
    let visibleCount = 0;

    cards.forEach(card => {
        let visible = true;

        // Distance filter
        const distance = getDistanceFromCard(card);
        if (distance !== null && distance > activeFilters.distance) {
            visible = false;
        }

        // Service type filter
        if (activeFilters.serviceTypes.length > 0) {
            const cardServiceType = card.dataset.serviceType;
            if (!activeFilters.serviceTypes.includes(cardServiceType)) {
                visible = false;
            }
        }

        // Status filter
        if (activeFilters.status !== 'all') {
            const cardStatus = card.querySelector('.request-status');
            if (!cardStatus || !cardStatus.classList.contains(`status-${activeFilters.status}`)) {
                visible = false;
            }
        }

        // Date filter
        const cardDate = getDateFromCard(card);
        if (activeFilters.dateFrom && cardDate < activeFilters.dateFrom) {
            visible = false;
        }
        if (activeFilters.dateTo && cardDate > activeFilters.dateTo) {
            visible = false;
        }

        // Show/hide card
        if (visible) {
            card.style.display = 'block';
            card.style.animation = 'fadeInUp 0.4s ease-out';
            visibleCount++;
        } else {
            card.style.display = 'none';
        }
    });

    // Sort visible cards
    sortCards(cards.filter(card => card.style.display !== 'none'));

    // Update results count
    updateResultsCount(visibleCount);

    // Update map markers
    updateMapMarkers();
}

/**
 * Sort cards based on active sort option
 */
function sortCards(visibleCards) {
    const container = document.querySelector('.requests-grid');
    if (!container) return;

    visibleCards.sort((a, b) => {
        switch(activeFilters.sortBy) {
            case 'distance-asc':
                return getDistanceFromCard(a) - getDistanceFromCard(b);
            case 'date-desc':
                return getDateFromCard(b) - getDateFromCard(a);
            case 'date-asc':
                return getDateFromCard(a) - getDateFromCard(b);
            default:
                return 0;
        }
    });

    visibleCards.forEach(card => container.appendChild(card));
    animateCardsReorder(visibleCards);
}

/**
 * Clear all filters
 */
function clearAllFilters() {
    activeFilters = {
        distance: 999,
        serviceTypes: [],
        dateFrom: null,
        dateTo: null,
        status: 'all',
        sortBy: 'date-desc'
    };

    // Reset UI elements
    const distanceSlider = document.getElementById('distance-slider');
    if (distanceSlider) {
        distanceSlider.value = 100;
        document.getElementById('distance-value-display').textContent = 'All Distances';
    }

    document.querySelectorAll('.service-type-checkbox').forEach(cb => cb.checked = false);
    document.querySelectorAll('.quick-date-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('input[name="status-filter"]').forEach(radio => {
        radio.checked = radio.value === 'all';
    });
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';

    applyFilters();
    updateActiveFiltersBadge();
}

/**
 * Update active filters badge
 */
function updateActiveFiltersBadge() {
    const badge = document.getElementById('active-filters-badge');
    if (!badge) return;

    let count = 0;
    if (activeFilters.distance < 999) count++;
    if (activeFilters.serviceTypes.length > 0) count += activeFilters.serviceTypes.length;
    if (activeFilters.dateFrom || activeFilters.dateTo) count++;
    if (activeFilters.status !== 'all') count++;

    badge.textContent = count;
    badge.style.display = count > 0 ? 'inline-flex' : 'none';
}

/**
 * Update results count display
 */
function updateResultsCount(count) {
    const resultsCount = document.getElementById('results-count');
    if (resultsCount) {
        resultsCount.textContent = count;
    }
}

/**
 * Update map markers based on filtered cards
 */
function updateMapMarkers() {
    if (!mapInstance || markers.length === 0) return;

    const visibleCards = Array.from(document.querySelectorAll('.request-card'))
        .filter(card => card.style.display !== 'none');
    const visibleIds = visibleCards.map(card => parseInt(card.dataset.requestId));

    markers.forEach(marker => {
        const visible = visibleIds.includes(marker.requestId);
        if (marker.userMarker) {
            marker.userMarker.setOpacity(visible ? 1 : 0.2);
        }
        if (marker.providerMarker) {
            marker.providerMarker.setOpacity(visible ? 1 : 0.2);
        }
        if (marker.line) {
            marker.line.setStyle({ opacity: visible ? 0.6 : 0.1 });
        }
    });
}

// ==============================================
// UTILITY FUNCTIONS
// ==============================================

function getDistanceFromCard(card) {
    const distanceValue = card.querySelector('.distance-value');
    if (!distanceValue) return null;
    
    const match = distanceValue.textContent.match(/[\d.]+/);
    return match ? parseFloat(match[0]) : null;
}

function getDateFromCard(card) {
    const requestId = card.querySelector('.request-id');
    if (!requestId) return 0;
    
    const match = requestId.textContent.match(/\d+/);
    return match ? parseInt(match[0]) : 0;
}

function animateCardsReorder(cards) {
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            card.style.transition = 'opacity 0.4s ease-out, transform 0.4s ease-out';
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

// ==============================================
// INITIALIZE ON PAGE LOAD
// ==============================================

document.addEventListener('DOMContentLoaded', function() {
    console.log('Maps & Filters initialized');
    
    initializeViewToggle();
    initializeFilters();
    
    // Initialize maps if data is available
    if (typeof requestsMapData !== 'undefined') {
        initializeListMap(requestsMapData);
    }
    
    if (typeof detailMapData !== 'undefined') {
        initializeDetailMap(
            detailMapData.userLat,
            detailMapData.userLng,
            detailMapData.providerLat,
            detailMapData.providerLng,
            detailMapData.userAddress,
            detailMapData.providerAddress,
            detailMapData.distance
        );
    }
});

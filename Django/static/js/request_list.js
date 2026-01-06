/**
 * LOCAL PRO CONNECT - REQUEST LIST & DETAIL
 * Enhanced JavaScript for Distance Visualization and Interactivity
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Request List/Detail JS Loaded');
    
    // Initialize all features
    initializeAnimations();
    initializeDistanceVisuals();
    initializePhotoGallery();
    initializeFilterSort();
    
    /**
     * Animate cards on scroll
     */
    function initializeAnimations() {
        const cards = document.querySelectorAll('.request-card');
        
        if ('IntersectionObserver' in window) {
            const observer = new IntersectionObserver((entries) => {
                entries.forEach((entry, index) => {
                    if (entry.isIntersecting) {
                        setTimeout(() => {
                            entry.target.style.opacity = '1';
                            entry.target.style.transform = 'translateY(0)';
                        }, index * 100);
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });
            
            cards.forEach(card => {
                card.style.opacity = '0';
                card.style.transform = 'translateY(20px)';
                card.style.transition = 'opacity 0.6s ease-out, transform 0.6s ease-out';
                observer.observe(card);
            });
        }
    }
    
    /**
     * Enhanced distance visualization
     */
    function initializeDistanceVisuals() {
        const distanceSections = document.querySelectorAll('.distance-section');
        
        distanceSections.forEach(section => {
            const distanceValue = section.querySelector('.distance-value');
            if (!distanceValue) return;
            
            const distanceText = distanceValue.textContent.trim();
            const distanceMatch = distanceText.match(/[\d.]+/);
            
            if (distanceMatch) {
                const distance = parseFloat(distanceMatch[0]);
                
                // Add visual indicator based on distance
                const indicator = document.createElement('div');
                indicator.style.cssText = `
                    margin-top: 12px;
                    padding: 8px 16px;
                    border-radius: 20px;
                    text-align: center;
                    font-size: 13px;
                    font-weight: 700;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                `;
                
                if (distance < 5) {
                    indicator.textContent = '✓ Very Close - Excellent!';
                    indicator.style.background = 'linear-gradient(135deg, rgba(23, 184, 144, 0.2), rgba(16, 185, 129, 0.2))';
                    indicator.style.color = '#17B890';
                    indicator.style.border = '2px solid #17B890';
                } else if (distance < 15) {
                    indicator.textContent = '✓ Nearby - Good Match';
                    indicator.style.background = 'linear-gradient(135deg, rgba(23, 184, 144, 0.15), rgba(16, 185, 129, 0.15))';
                    indicator.style.color = '#17B890';
                    indicator.style.border = '2px solid #17B890';
                } else if (distance < 30) {
                    indicator.textContent = '⚠ Moderate Distance';
                    indicator.style.background = 'linear-gradient(135deg, rgba(255, 195, 0, 0.2), rgba(230, 176, 0, 0.2))';
                    indicator.style.color = '#E6B000';
                    indicator.style.border = '2px solid #E6B000';
                } else {
                    indicator.textContent = '⚠ Significant Distance';
                    indicator.style.background = 'linear-gradient(135deg, rgba(255, 140, 66, 0.2), rgba(231, 76, 60, 0.2))';
                    indicator.style.color = '#FF8C42';
                    indicator.style.border = '2px solid #FF8C42';
                }
                
                // Insert after distance value
                distanceValue.parentNode.insertBefore(indicator, distanceValue.nextSibling);
                
                // Animate the distance value counting up
                animateDistanceCounter(distanceValue, distance);
            }
        });
    }
    
    /**
     * Animate distance counter from 0 to target value
     */
    function animateDistanceCounter(element, targetDistance) {
        const duration = 1500; // 1.5 seconds
        const startTime = performance.now();
        const unitSpan = element.querySelector('.unit');
        const unitText = unitSpan ? unitSpan.textContent : 'miles';
        
        function updateCounter(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            
            // Easing function for smooth animation
            const easeOutQuart = 1 - Math.pow(1 - progress, 4);
            const currentDistance = (targetDistance * easeOutQuart).toFixed(1);
            
            if (unitSpan) {
                element.childNodes[0].textContent = currentDistance;
            } else {
                element.textContent = currentDistance + ' miles';
            }
            
            if (progress < 1) {
                requestAnimationFrame(updateCounter);
            }
        }
        
        requestAnimationFrame(updateCounter);
    }
    
    /**
     * Photo gallery lightbox functionality
     */
    function initializePhotoGallery() {
        const photoItems = document.querySelectorAll('.photo-item');
        
        photoItems.forEach(item => {
            const img = item.querySelector('img');
            if (!img) return;
            
            item.style.cursor = 'pointer';
            
            item.addEventListener('click', function() {
                openLightbox(img.src);
            });
            
            // Add hover effect
            item.addEventListener('mouseenter', function() {
                img.style.transform = 'scale(1.05)';
                img.style.transition = 'transform 0.3s ease';
            });
            
            item.addEventListener('mouseleave', function() {
                img.style.transform = 'scale(1)';
            });
        });
    }
    
    /**
     * Open photo in lightbox
     */
    function openLightbox(imageSrc) {
        // Create lightbox overlay
        const lightbox = document.createElement('div');
        lightbox.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            cursor: pointer;
            animation: fadeIn 0.3s ease;
        `;
        
        const img = document.createElement('img');
        img.src = imageSrc;
        img.style.cssText = `
            max-width: 90%;
            max-height: 90%;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            animation: scaleIn 0.3s ease;
        `;
        
        lightbox.appendChild(img);
        document.body.appendChild(lightbox);
        
        // Close on click
        lightbox.addEventListener('click', function() {
            lightbox.style.animation = 'fadeOut 0.3s ease';
            setTimeout(() => {
                document.body.removeChild(lightbox);
            }, 300);
        });
        
        // Close on ESC key
        const closeOnEsc = (e) => {
            if (e.key === 'Escape') {
                lightbox.click();
                document.removeEventListener('keydown', closeOnEsc);
            }
        };
        document.addEventListener('keydown', closeOnEsc);
    }
    
    /**
     * Initialize filter and sort functionality
     */
    function initializeFilterSort() {
        // Add filter/sort controls if on list page
        const requestsGrid = document.querySelector('.requests-grid');
        if (!requestsGrid) return;
        
        const cards = Array.from(document.querySelectorAll('.request-card'));
        if (cards.length === 0) return;
        
        // Create controls container
        const controls = document.createElement('div');
        controls.style.cssText = `
            display: flex;
            gap: 16px;
            justify-content: center;
            margin-bottom: 32px;
            flex-wrap: wrap;
        `;
        
        // Sort by distance button
        const sortDistanceBtn = createControlButton('📍 Sort by Distance', () => {
            sortCardsByDistance(cards, requestsGrid);
        });
        
        // Sort by date button
        const sortDateBtn = createControlButton('📅 Sort by Date', () => {
            sortCardsByDate(cards, requestsGrid);
        });
        
        // Filter by status buttons
        const filterAllBtn = createControlButton('All', () => {
            filterCardsByStatus(cards, null);
        });
        
        const filterPendingBtn = createControlButton('Pending', () => {
            filterCardsByStatus(cards, 'pending');
        });
        
        const filterAcceptedBtn = createControlButton('Accepted', () => {
            filterCardsByStatus(cards, 'accepted');
        });
        
        controls.appendChild(sortDistanceBtn);
        controls.appendChild(sortDateBtn);
        controls.appendChild(filterAllBtn);
        controls.appendChild(filterPendingBtn);
        controls.appendChild(filterAcceptedBtn);
        
        // Insert controls before the grid
        requestsGrid.parentNode.insertBefore(controls, requestsGrid);
    }
    
    /**
     * Create control button
     */
    function createControlButton(text, onClick) {
        const btn = document.createElement('button');
        btn.textContent = text;
        btn.style.cssText = `
            padding: 10px 20px;
            background: white;
            color: #0052CC;
            border: 2px solid #0052CC;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.3s ease;
        `;
        
        btn.addEventListener('click', onClick);
        
        btn.addEventListener('mouseenter', function() {
            this.style.background = '#E8F0FE';
            this.style.transform = 'translateY(-2px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.background = 'white';
            this.style.transform = 'translateY(0)';
        });
        
        return btn;
    }
    
    /**
     * Sort cards by distance
     */
    function sortCardsByDistance(cards, container) {
        const sortedCards = cards.sort((a, b) => {
            const distanceA = getDistanceFromCard(a);
            const distanceB = getDistanceFromCard(b);
            return distanceA - distanceB;
        });
        
        sortedCards.forEach(card => container.appendChild(card));
        animateReorder();
    }
    
    /**
     * Sort cards by date
     */
    function sortCardsByDate(cards, container) {
        const sortedCards = cards.sort((a, b) => {
            const dateA = getDateFromCard(a);
            const dateB = getDateFromCard(b);
            return dateB - dateA; // Newest first
        });
        
        sortedCards.forEach(card => container.appendChild(card));
        animateReorder();
    }
    
    /**
     * Filter cards by status
     */
    function filterCardsByStatus(cards, status) {
        cards.forEach(card => {
            const cardStatus = card.querySelector('.request-status');
            if (!cardStatus) return;
            
            if (!status || cardStatus.classList.contains(`status-${status}`)) {
                card.style.display = 'block';
                card.style.animation = 'fadeInUp 0.4s ease-out';
            } else {
                card.style.display = 'none';
            }
        });
    }
    
    /**
     * Extract distance from card
     */
    function getDistanceFromCard(card) {
        const distanceValue = card.querySelector('.distance-value');
        if (!distanceValue) return Infinity;
        
        const match = distanceValue.textContent.match(/[\d.]+/);
        return match ? parseFloat(match[0]) : Infinity;
    }
    
    /**
     * Extract date from card (using request ID as proxy)
     */
    function getDateFromCard(card) {
        const requestId = card.querySelector('.request-id');
        if (!requestId) return 0;
        
        const match = requestId.textContent.match(/\d+/);
        return match ? parseInt(match[0]) : 0;
    }
    
    /**
     * Animate reorder
     */
    function animateReorder() {
        const cards = document.querySelectorAll('.request-card');
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
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    @keyframes fadeOut {
        from { opacity: 1; }
        to { opacity: 0; }
    }
    
    @keyframes scaleIn {
        from { 
            transform: scale(0.8);
            opacity: 0;
        }
        to { 
            transform: scale(1);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);

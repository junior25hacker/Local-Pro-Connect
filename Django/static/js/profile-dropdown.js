/**
 * Local Pro Connect - Profile Dropdown Enhancement
 * Premium interaction behaviors for the user profile indicator
 */

(function() {
    'use strict';
    
    // Initialize when DOM is ready
    document.addEventListener('DOMContentLoaded', function() {
        initProfileDropdown();
    });
    
    /**
     * Initialize profile dropdown interactions
     */
    function initProfileDropdown() {
        const dropdownToggle = document.getElementById('profileDropdown');
        const dropdownMenu = dropdownToggle?.nextElementSibling;
        
        if (!dropdownToggle || !dropdownMenu) return;
        
        // Handle keyboard navigation
        dropdownToggle.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                dropdownToggle.click();
            }
        });
        
        // Add smooth close on outside click
        document.addEventListener('click', function(e) {
            if (!dropdownToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                const bsDropdown = bootstrap.Dropdown.getInstance(dropdownToggle);
                if (bsDropdown) {
                    bsDropdown.hide();
                }
            }
        });
        
        // Handle dropdown item keyboard navigation
        const dropdownItems = dropdownMenu.querySelectorAll('.dropdown-item');
        dropdownItems.forEach((item, index) => {
            item.addEventListener('keydown', function(e) {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const nextItem = dropdownItems[index + 1];
                    if (nextItem) nextItem.focus();
                } else if (e.key === 'ArrowUp') {
                    e.preventDefault();
                    const prevItem = dropdownItems[index - 1];
                    if (prevItem) prevItem.focus();
                    else dropdownToggle.focus();
                } else if (e.key === 'Escape') {
                    e.preventDefault();
                    const bsDropdown = bootstrap.Dropdown.getInstance(dropdownToggle);
                    if (bsDropdown) {
                        bsDropdown.hide();
                    }
                    dropdownToggle.focus();
                }
            });
        });
        
        // Add ripple effect on dropdown items
        dropdownItems.forEach(item => {
            item.addEventListener('click', function(e) {
                createRipple(e, this);
            });
        });
        
        // Handle profile image loading
        const profileImage = dropdownToggle.querySelector('.profile-avatar');
        if (profileImage) {
            profileImage.classList.add('loading');
            
            profileImage.addEventListener('load', function() {
                this.classList.remove('loading');
            });
            
            profileImage.addEventListener('error', function() {
                this.classList.remove('loading');
            });
        }
        
        // Show dropdown on first hover (for desktop)
        if (window.innerWidth >= 992) {
            let hoverTimeout;
            const profileIndicator = dropdownToggle.closest('.profile-indicator');
            
            profileIndicator.addEventListener('mouseenter', function() {
                hoverTimeout = setTimeout(() => {
                    const bsDropdown = bootstrap.Dropdown.getOrCreateInstance(dropdownToggle);
                    bsDropdown.show();
                }, 300);
            });
            
            profileIndicator.addEventListener('mouseleave', function() {
                clearTimeout(hoverTimeout);
            });
        }
    }
    
    /**
     * Create ripple effect on click
     */
    function createRipple(event, element) {
        const ripple = document.createElement('span');
        const rect = element.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = event.clientX - rect.left - size / 2;
        const y = event.clientY - rect.top - size / 2;
        
        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.classList.add('ripple-effect');
        
        element.style.position = 'relative';
        element.style.overflow = 'hidden';
        element.appendChild(ripple);
        
        setTimeout(() => {
            ripple.remove();
        }, 600);
    }
    
})();

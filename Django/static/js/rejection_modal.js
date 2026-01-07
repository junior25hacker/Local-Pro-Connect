/**
 * ============================================================================
 * LOCAL PRO CONNECT - REJECTION MODAL JAVASCRIPT
 * Handles interactivity, validation, and user feedback
 * ============================================================================
 */

document.addEventListener('DOMContentLoaded', function() {
    console.log('Rejection Modal initialized');

    // ========================================================================
    // DOM ELEMENTS
    // ========================================================================
    const modalOverlay = document.getElementById('rejectionModalOverlay');
    const modal = document.getElementById('rejectionModal');
    const closeModalBtn = document.getElementById('closeModalBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const rejectionForm = document.getElementById('rejectionForm');
    const submitBtn = document.getElementById('submitBtn');
    
    // Reason selection elements
    const reasonOptions = document.querySelectorAll('input[name="rejection_reason"]');
    const reasonError = document.getElementById('reasonError');
    const selectedReasonDisplay = document.getElementById('selectedReasonDisplay');
    const selectedReasonText = document.getElementById('selectedReasonText');
    
    // Description elements
    const descriptionSection = document.getElementById('descriptionSection');
    const descriptionTextarea = document.getElementById('rejection_description');
    const charCount = document.getElementById('charCount');

    // ========================================================================
    // STATE MANAGEMENT
    // ========================================================================
    let currentSelectedReason = null;

    // ========================================================================
    // REASON SELECTION LOGIC
    // ========================================================================
    reasonOptions.forEach(radio => {
        radio.addEventListener('change', function() {
            if (this.checked) {
                handleReasonSelection(this.value);
            }
        });

        // Add keyboard support for better accessibility
        radio.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ' ') {
                e.preventDefault();
                this.checked = true;
                handleReasonSelection(this.value);
            }
        });
    });

    /**
     * Handle reason selection and show appropriate UI elements
     * @param {string} reason - The selected reason value
     */
    function handleReasonSelection(reason) {
        currentSelectedReason = reason;
        
        // Hide error message if visible
        if (reasonError.style.display !== 'none') {
            reasonError.style.display = 'none';
        }

        // Update selected reason display
        const reasonLabels = {
            'distance': 'Distance',
            'price': 'Price',
            'time': 'Time',
            'other': 'Other'
        };

        selectedReasonText.textContent = reasonLabels[reason] || reason;
        
        // Show the selected reason display with animation
        selectedReasonDisplay.style.display = 'block';
        
        // Show description section with animation
        descriptionSection.style.display = 'block';
        
        // Enable submit button
        submitBtn.disabled = false;

        // Smooth scroll to description section on mobile
        setTimeout(() => {
            if (window.innerWidth <= 768) {
                descriptionSection.scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'nearest' 
                });
            }
        }, 100);

        console.log('Reason selected:', reason);
    }

    // ========================================================================
    // CHARACTER COUNTER FOR DESCRIPTION
    // ========================================================================
    if (descriptionTextarea) {
        descriptionTextarea.addEventListener('input', function() {
            const currentLength = this.value.length;
            const maxLength = this.getAttribute('maxlength');
            
            charCount.textContent = currentLength;
            
            // Visual feedback when approaching limit
            if (currentLength >= maxLength * 0.9) {
                charCount.style.color = '#e74c3c';
                charCount.style.fontWeight = '600';
            } else {
                charCount.style.color = '#666666';
                charCount.style.fontWeight = '500';
            }
        });
    }

    // ========================================================================
    // FORM VALIDATION
    // ========================================================================
    function validateForm() {
        // Check if a reason is selected
        const isReasonSelected = Array.from(reasonOptions).some(radio => radio.checked);
        
        if (!isReasonSelected) {
            // Show error message
            reasonError.style.display = 'flex';
            
            // Scroll to error
            reasonError.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });
            
            // Focus first radio button for accessibility
            reasonOptions[0].focus();
            
            return false;
        }
        
        return true;
    }

    // ========================================================================
    // FORM SUBMISSION
    // ========================================================================
    rejectionForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Validate form
        if (!validateForm()) {
            console.log('Form validation failed');
            return;
        }

        // Show loading state on submit button
        const originalButtonHTML = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Submitting...';

        // Get form data
        const formData = new FormData(this);
        const data = {
            rejection_reason: formData.get('rejection_reason'),
            rejection_description: formData.get('rejection_description') || ''
        };

        console.log('Form submitted with data:', data);

        // Show success message
        showSuccessMessage();
        
        // Submit the form to Django after a short delay
        setTimeout(() => {
            console.log('Submitting form to Django');
            this.submit();
        }, 800);
    });

    /**
     * Show success message after submission
     */
    function showSuccessMessage() {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-notification';
        successDiv.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>Rejection submitted successfully!</span>
        `;
        successDiv.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: linear-gradient(135deg, #17B890 0%, #139a77 100%);
            color: white;
            padding: 16px 24px;
            border-radius: 10px;
            box-shadow: 0 4px 16px rgba(23, 184, 144, 0.3);
            display: flex;
            align-items: center;
            gap: 12px;
            font-weight: 600;
            z-index: 10000;
            animation: slideInRight 0.4s ease-out;
        `;
        
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            successDiv.style.animation = 'slideOutRight 0.4s ease-out';
            setTimeout(() => {
                document.body.removeChild(successDiv);
            }, 400);
        }, 2000);
    }

    // ========================================================================
    // MODAL CLOSE FUNCTIONALITY
    // ========================================================================
    
    /**
     * Close the modal with animation
     */
    function closeModal() {
        modal.style.animation = 'slideDown 0.3s ease-out';
        modalOverlay.style.animation = 'fadeOut 0.3s ease-out';
        
        setTimeout(() => {
            // In a real implementation, you might redirect or hide the overlay
            console.log('Modal closed');
            
            // Reset everything
            resetModalUI();
            rejectionForm.reset();
            
            // For standalone page, you might want to redirect
            // window.location.href = '/requests/';
        }, 300);
    }

    /**
     * Reset modal UI to initial state
     */
    function resetModalUI() {
        currentSelectedReason = null;
        selectedReasonDisplay.style.display = 'none';
        descriptionSection.style.display = 'none';
        reasonError.style.display = 'none';
        submitBtn.disabled = true;
        charCount.textContent = '0';
        
        // Uncheck all radio buttons
        reasonOptions.forEach(radio => {
            radio.checked = false;
        });
    }

    // Close button click
    closeModalBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('Are you sure you want to cancel? Your changes will be lost.')) {
            closeModal();
        }
    });

    // Cancel button click
    cancelBtn.addEventListener('click', function(e) {
        e.preventDefault();
        if (confirm('Are you sure you want to cancel? Your changes will be lost.')) {
            closeModal();
        }
    });

    // Close on overlay click (optional - can be removed if not desired)
    modalOverlay.addEventListener('click', function(e) {
        if (e.target === modalOverlay) {
            if (confirm('Are you sure you want to cancel? Your changes will be lost.')) {
                closeModal();
            }
        }
    });

    // Close on Escape key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (confirm('Are you sure you want to cancel? Your changes will be lost.')) {
                closeModal();
            }
        }
    });

    // ========================================================================
    // ADDITIONAL ANIMATIONS
    // ========================================================================
    
    // Add CSS animations dynamically
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                opacity: 0;
                transform: translateX(100px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        @keyframes slideOutRight {
            from {
                opacity: 1;
                transform: translateX(0);
            }
            to {
                opacity: 0;
                transform: translateX(100px);
            }
        }
        
        @keyframes slideDown {
            from {
                opacity: 1;
                transform: translateY(0) scale(1);
            }
            to {
                opacity: 0;
                transform: translateY(40px) scale(0.95);
            }
        }
        
        @keyframes fadeOut {
            from {
                opacity: 1;
            }
            to {
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // ========================================================================
    // ACCESSIBILITY ENHANCEMENTS
    // ========================================================================
    
    // Trap focus within modal for accessibility
    const focusableElements = modal.querySelectorAll(
        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const firstFocusableElement = focusableElements[0];
    const lastFocusableElement = focusableElements[focusableElements.length - 1];

    modal.addEventListener('keydown', function(e) {
        if (e.key === 'Tab') {
            if (e.shiftKey) {
                // Shift + Tab
                if (document.activeElement === firstFocusableElement) {
                    e.preventDefault();
                    lastFocusableElement.focus();
                }
            } else {
                // Tab
                if (document.activeElement === lastFocusableElement) {
                    e.preventDefault();
                    firstFocusableElement.focus();
                }
            }
        }
    });

    // Set initial focus to first radio button
    if (reasonOptions.length > 0) {
        setTimeout(() => {
            reasonOptions[0].focus();
        }, 300);
    }

    // ========================================================================
    // UTILITY FUNCTIONS
    // ========================================================================
    
    /**
     * Log form state for debugging
     */
    function logFormState() {
        console.log('=== Form State ===');
        console.log('Selected Reason:', currentSelectedReason);
        console.log('Description Length:', descriptionTextarea.value.length);
        console.log('Submit Button Enabled:', !submitBtn.disabled);
        console.log('==================');
    }

    // Expose logFormState for debugging
    window.rejectionModal = {
        logState: logFormState,
        close: closeModal,
        reset: resetModalUI
    };

    console.log('Rejection Modal ready. Use window.rejectionModal for debugging.');
});

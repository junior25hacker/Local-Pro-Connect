document.addEventListener("DOMContentLoaded", function () {
    "use strict";

    // ===========================
    // FORM ENHANCEMENTS
    // ===========================

    // Initialize form functionality
    initializeForm();

    function initializeForm() {
        initializePhotoUpload();
        initializeFormValidation();
        addFormEnhancements();
        initializeBudgetSlider();
    }

    // ===========================
    // PHOTO UPLOAD FUNCTIONALITY
    // ===========================
    function initializePhotoUpload() {
        const photoInput = document.getElementById("id_photos");
        if (!photoInput) return;

        const wrapper = photoInput.closest(".file-input-wrapper");
        if (!wrapper) return;

        // Get or create preview container
        let previewContainer = wrapper.nextElementSibling;
        if (!previewContainer || !previewContainer.classList.contains("photo-preview-container")) {
            previewContainer = document.createElement("div");
            previewContainer.classList.add("photo-preview-container");
            wrapper.parentNode.insertBefore(previewContainer, wrapper.nextSibling);
        }

        // Handle file selection
        photoInput.addEventListener("change", function () {
            displayPhotoPreviews(this, previewContainer);
        });

        // Handle drag and drop
        const placeholder = wrapper.querySelector(".file-input-placeholder");
        if (placeholder) {
            wrapper.addEventListener("dragover", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.style.opacity = "0.8";
            });

            wrapper.addEventListener("dragleave", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.style.opacity = "1";
            });

            wrapper.addEventListener("drop", function (e) {
                e.preventDefault();
                e.stopPropagation();
                wrapper.style.opacity = "1";

                const files = e.dataTransfer.files;
                photoInput.files = files;
                displayPhotoPreviews(photoInput, previewContainer);
            });
        }
    }

    function displayPhotoPreviews(fileInput, previewContainer) {
        previewContainer.innerHTML = "";
        const files = Array.from(fileInput.files);

        files.forEach(file => {
            // Validate file type
            if (!file.type.startsWith("image/")) {
                console.warn(`Skipped non-image file: ${file.name}`);
                return;
            }

            // Validate file size (5MB max)
            if (file.size > 5 * 1024 * 1024) {
                console.warn(`File ${file.name} exceeds 5MB limit`);
                return;
            }

            const reader = new FileReader();
            reader.onload = function (e) {
                const imgContainer = document.createElement("div");
                imgContainer.style.position = "relative";
                imgContainer.style.display = "inline-block";

                const img = document.createElement("img");
                img.src = e.target.result;
                img.style.display = "block";

                const removeBtn = document.createElement("button");
                removeBtn.type = "button";
                removeBtn.innerHTML = "×";
                removeBtn.style.cssText = `
                    position: absolute;
                    top: -10px;
                    right: -10px;
                    width: 28px;
                    height: 28px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                    color: white;
                    border: 2px solid white;
                    font-size: 18px;
                    font-weight: bold;
                    cursor: pointer;
                    line-height: 1;
                    padding: 0;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    opacity: 0;
                    transition: all 300ms cubic-bezier(0.4, 0, 0.2, 1);
                    box-shadow: 0 4px 12px rgba(231, 76, 60, 0.4);
                    z-index: 10;
                `;

                removeBtn.addEventListener("click", function (e) {
                    e.preventDefault();
                    imgContainer.style.transform = "scale(0.8)";
                    imgContainer.style.opacity = "0";
                    setTimeout(() => imgContainer.remove(), 200);
                });
                
                removeBtn.addEventListener("mouseenter", function () {
                    this.style.transform = "scale(1.1) rotate(90deg)";
                    this.style.background = "linear-gradient(135deg, #c0392b 0%, #a93226 100%)";
                });
                
                removeBtn.addEventListener("mouseleave", function () {
                    this.style.transform = "scale(1) rotate(0deg)";
                    this.style.background = "linear-gradient(135deg, #e74c3c 0%, #c0392b 100%)";
                });

                imgContainer.addEventListener("mouseenter", function () {
                    removeBtn.style.opacity = "1";
                });

                imgContainer.addEventListener("mouseleave", function () {
                    removeBtn.style.opacity = "0";
                });

                imgContainer.appendChild(img);
                imgContainer.appendChild(removeBtn);
                previewContainer.appendChild(imgContainer);
            };
            reader.readAsDataURL(file);
        });
    }

    // ===========================
    // FORM VALIDATION
    // ===========================
    function initializeFormValidation() {
        const form = document.querySelector(".request-form");
        if (!form) return;

        const descriptionField = form.querySelector(".input-textarea");
        if (descriptionField) {
            // Real-time validation feedback
            descriptionField.addEventListener("blur", function () {
                validateDescriptionField(this);
            });

            descriptionField.addEventListener("focus", function () {
                clearFieldError(this);
            });
        }

        // Form submission handler
        form.addEventListener("submit", function (e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    }

    function validateDescriptionField(field) {
        const value = field.value.trim();
        if (value.length === 0) {
            addFieldError(field, "Please describe what you need");
        } else if (value.length < 10) {
            addFieldError(field, "Please provide at least 10 characters");
        } else {
            clearFieldError(field);
        }
    }

    function validateForm(form) {
        const descriptionField = form.querySelector(".input-textarea");
        let isValid = true;

        if (descriptionField) {
            const value = descriptionField.value.trim();
            if (value.length === 0) {
                addFieldError(descriptionField, "Please describe what you need");
                isValid = false;
            } else if (value.length < 10) {
                addFieldError(descriptionField, "Please provide at least 10 characters");
                isValid = false;
            }
        }

        return isValid;
    }

    function addFieldError(field, message) {
        clearFieldError(field);
        field.style.borderColor = "#e74c3c";
        field.style.backgroundColor = "rgba(231, 76, 60, 0.04)";
        field.style.boxShadow = "0 0 0 3px rgba(231, 76, 60, 0.1), 0 1px 2px rgba(0, 0, 0, 0.05)";

        const errorMsg = document.createElement("div");
        errorMsg.className = "field-error-message";
        errorMsg.textContent = "⚠️ " + message;
        errorMsg.style.cssText = `
            color: #e74c3c;
            font-size: 13px;
            margin-top: 8px;
            display: block;
            font-weight: 500;
            letter-spacing: 0.2px;
            animation: slideDown 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        `;
        field.parentNode.insertBefore(errorMsg, field.nextSibling);
        
        // Add animation
        const style = document.createElement("style");
        style.textContent = `
            @keyframes slideDown {
                from {
                    opacity: 0;
                    transform: translateY(-8px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }
        `;
        if (!document.querySelector('style[data-error-animation]')) {
            style.setAttribute('data-error-animation', 'true');
            document.head.appendChild(style);
        }
    }

    function clearFieldError(field) {
        field.style.borderColor = "";
        field.style.backgroundColor = "";
        field.style.boxShadow = "";
        const errorMsg = field.nextElementSibling;
        if (errorMsg && errorMsg.classList.contains("field-error-message")) {
            errorMsg.style.opacity = "0";
            errorMsg.style.transform = "translateY(-8px)";
            setTimeout(() => errorMsg.remove(), 200);
        }
    }

    // ===========================
    // FORM ENHANCEMENTS
    // ===========================
    function addFormEnhancements() {
        enhanceUrgentToggle();
        enhanceDateTimePicker();
        enhanceButtons();
    }

    function enhanceUrgentToggle() {
        const urgentCheckbox = document.getElementById("id_urgent");
        const urgentLabel = document.querySelector("label[for='id_urgent']");

        if (urgentCheckbox && urgentLabel) {
            // Make label clickable (it already is in CSS, but add feedback)
            urgentLabel.addEventListener("change", function () {
                // Add any additional behavior here
            });
        }
    }

    function enhanceDateTimePicker() {
        const dateTimeField = document.getElementById("id_date_time");
        if (!dateTimeField) return;

        // Add min date as today
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const minDate = today.toISOString().slice(0, 16);
        dateTimeField.min = minDate;
    }

    function enhanceButtons() {
        const buttons = document.querySelectorAll(".btn");
        buttons.forEach(btn => {
            btn.addEventListener("mouseenter", function () {
                // Add any button hover effects here
            });

            btn.addEventListener("click", function (e) {
                // Add button click feedback with ripple effect
                if (this.classList.contains("btn-primary") && !this.disabled) {
                    // Show loading state on submit
                    const form = this.closest("form");
                    if (form && form.checkValidity && form.checkValidity()) {
                        this.disabled = true;
                        const originalText = this.textContent.trim();
                        
                        // Add spinner animation
                        this.innerHTML = `
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none" style="animation: spin 1s linear infinite;">
                                <circle cx="10" cy="10" r="8" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-dasharray="40 10" opacity="0.8"/>
                            </svg>
                            <span>Submitting...</span>
                        `;
                        
                        // Add spin animation
                        if (!document.querySelector('style[data-spin-animation]')) {
                            const style = document.createElement("style");
                            style.setAttribute('data-spin-animation', 'true');
                            style.textContent = `
                                @keyframes spin {
                                    from { transform: rotate(0deg); }
                                    to { transform: rotate(360deg); }
                                }
                            `;
                            document.head.appendChild(style);
                        }
                    }
                }
            });
        });
    }

    // ===========================
    // BUDGET SLIDER FUNCTIONALITY
    // ===========================
    function initializeBudgetSlider() {
        const slider = document.getElementById("budget_slider");
        const budgetValue = document.getElementById("budget_value");
        const budgetAmount = document.getElementById("budget_amount");
        const providerSelect = document.querySelector("select[name='provider_choice']");
        const providerMinHint = document.getElementById("provider_min_hint");
        const providerMinValue = document.getElementById("provider_min_value");
        const rangeMinLabel = document.getElementById("range_min_label");
        const sliderWrapper = document.querySelector(".budget-slider-wrapper");

        if (!slider || !budgetValue || !budgetAmount) return;

        // Provider minimum prices (will be fetched dynamically)
        const providerMinPrices = {};

        // Format currency
        function formatCurrency(value) {
            return new Intl.NumberFormat('en-US', {
                style: 'decimal',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0
            }).format(value);
        }

        // Update budget display
        function updateBudgetDisplay(value) {
            // Add animation class
            budgetValue.classList.add("updating");
            
            // Update value
            budgetValue.textContent = formatCurrency(value);
            budgetAmount.value = value;
            
            // Remove animation class after animation
            setTimeout(() => {
                budgetValue.classList.remove("updating");
            }, 150);
        }

        // Check if budget is below provider minimum
        function checkMinimumBudget(currentValue, minPrice) {
            if (minPrice > 0 && currentValue < minPrice) {
                sliderWrapper.classList.add("below-minimum");
                return false;
            } else {
                sliderWrapper.classList.remove("below-minimum");
                return true;
            }
        }

        // Update slider based on provider selection
        function updateSliderForProvider(providerId) {
            if (!providerId) {
                // No provider selected, reset to default
                slider.min = 0;
                slider.dataset.providerMin = 0;
                providerMinHint.style.display = "none";
                rangeMinLabel.textContent = "$0";
                rangeMinLabel.classList.remove("provider-min-active");
                sliderWrapper.classList.remove("below-minimum");
                return;
            }

            // Fetch provider minimum price via AJAX
            fetchProviderMinPrice(providerId);
        }

        // Fetch provider minimum price from server
        function fetchProviderMinPrice(providerId) {
            // Check cache first
            if (providerMinPrices[providerId] !== undefined) {
                applyProviderMinPrice(providerMinPrices[providerId]);
                return;
            }

            // Fetch from API endpoint
            fetch(`/requests/api/provider/${providerId}/min-price/`)
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const minPrice = data.min_price;
                        // Cache the result
                        providerMinPrices[providerId] = minPrice;
                        applyProviderMinPrice(minPrice);
                    } else {
                        console.error('Failed to fetch provider min price:', data.error);
                        // Use default fallback
                        const defaultMin = 50;
                        providerMinPrices[providerId] = defaultMin;
                        applyProviderMinPrice(defaultMin);
                    }
                })
                .catch(error => {
                    console.error('Error fetching provider min price:', error);
                    // Use default fallback
                    const defaultMin = 50;
                    providerMinPrices[providerId] = defaultMin;
                    applyProviderMinPrice(defaultMin);
                });
        }

        // Apply provider minimum price to slider
        function applyProviderMinPrice(minPrice) {
            slider.dataset.providerMin = minPrice;
            
            // Update minimum label
            rangeMinLabel.textContent = `$${formatCurrency(minPrice)}`;
            rangeMinLabel.classList.add("provider-min-active");
            
            // Show provider minimum hint
            providerMinValue.textContent = `$${formatCurrency(minPrice)}`;
            providerMinHint.style.display = "block";
            
            // If current value is below minimum, adjust it
            const currentValue = parseInt(slider.value);
            if (currentValue < minPrice) {
                slider.value = minPrice;
                updateBudgetDisplay(minPrice);
            }
            
            // Check if below minimum
            checkMinimumBudget(parseInt(slider.value), minPrice);
        }

        // Slider input event (real-time update)
        slider.addEventListener("input", function() {
            const value = parseInt(this.value);
            updateBudgetDisplay(value);
            
            // Check against provider minimum
            const providerMin = parseInt(this.dataset.providerMin || 0);
            checkMinimumBudget(value, providerMin);
        });

        // Slider change event (final value)
        slider.addEventListener("change", function() {
            const value = parseInt(this.value);
            const providerMin = parseInt(this.dataset.providerMin || 0);
            
            // Snap to minimum if below
            if (providerMin > 0 && value < providerMin) {
                this.value = providerMin;
                updateBudgetDisplay(providerMin);
                
                // Show warning
                showMinimumWarning(providerMin);
            }
        });

        // Show warning when user tries to go below minimum
        function showMinimumWarning(minPrice) {
            const wrapper = sliderWrapper;
            wrapper.classList.add("below-minimum");
            
            // Add shake animation
            setTimeout(() => {
                wrapper.classList.remove("below-minimum");
            }, 500);
        }

        // Provider selection change event
        if (providerSelect) {
            providerSelect.addEventListener("change", function() {
                const providerId = this.value;
                updateSliderForProvider(providerId);
            });
            
            // Initialize on page load if provider is pre-selected
            if (providerSelect.value) {
                updateSliderForProvider(providerSelect.value);
            }
        }

        // Keyboard navigation support
        slider.addEventListener("keydown", function(e) {
            const currentValue = parseInt(this.value);
            const step = parseInt(this.step || 50);
            const providerMin = parseInt(this.dataset.providerMin || 0);
            
            // Arrow keys
            if (e.key === "ArrowLeft" || e.key === "ArrowDown") {
                const newValue = Math.max(providerMin, currentValue - step);
                this.value = newValue;
                updateBudgetDisplay(newValue);
                checkMinimumBudget(newValue, providerMin);
                e.preventDefault();
            } else if (e.key === "ArrowRight" || e.key === "ArrowUp") {
                const newValue = Math.min(parseInt(this.max), currentValue + step);
                this.value = newValue;
                updateBudgetDisplay(newValue);
                checkMinimumBudget(newValue, providerMin);
                e.preventDefault();
            } else if (e.key === "Home") {
                this.value = providerMin;
                updateBudgetDisplay(providerMin);
                checkMinimumBudget(providerMin, providerMin);
                e.preventDefault();
            } else if (e.key === "End") {
                this.value = this.max;
                updateBudgetDisplay(parseInt(this.max));
                checkMinimumBudget(parseInt(this.max), providerMin);
                e.preventDefault();
            }
        });

        // Touch device support
        let touchStartValue = 0;
        slider.addEventListener("touchstart", function() {
            touchStartValue = parseInt(this.value);
        });

        slider.addEventListener("touchend", function() {
            const touchEndValue = parseInt(this.value);
            if (touchStartValue !== touchEndValue) {
                const providerMin = parseInt(this.dataset.providerMin || 0);
                checkMinimumBudget(touchEndValue, providerMin);
            }
        });

        // Initialize with default value
        updateBudgetDisplay(parseInt(slider.value));
    }

    // ===========================
    // UTILITY FUNCTIONS
    // ===========================

    // Debounce function for form input
    function debounce(func, delay) {
        let timeoutId;
        return function (...args) {
            clearTimeout(timeoutId);
            timeoutId = setTimeout(() => func.apply(this, args), delay);
        };
    }

    // Add character counter for textarea (optional)
    const textarea = document.querySelector(".input-textarea");
    if (textarea) {
        const maxLength = 500;
        textarea.maxLength = maxLength;

        textarea.addEventListener("input", function () {
            const count = this.value.length;
            // Could show character count here
        });
    }

    // ===========================
    // ASYNC FORM SUBMISSION
    // ===========================
    const form = document.querySelector(".request-form");
    if (form) {
        form.addEventListener("submit", function (e) {
            e.preventDefault();
            handleAsyncSubmission(form);
        });
    }

    function handleAsyncSubmission(form) {
        // Create a loading overlay
        const loadingOverlay = document.createElement("div");
        loadingOverlay.className = "loading-overlay";
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <p>Submitting your request...</p>
                <p style="font-size: 12px; color: #999; margin-top: 10px;">Processing email notifications (5 seconds)</p>
            </div>
        `;
        document.body.appendChild(loadingOverlay);

        // Add styles for loading overlay
        const style = document.createElement("style");
        style.textContent = `
            .loading-overlay {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            }
            .loading-spinner {
                text-align: center;
                background: white;
                padding: 40px;
                border-radius: 12px;
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            }
            .spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #667eea;
                border-radius: 50%;
                width: 40px;
                height: 40px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            .loading-spinner p {
                color: #333;
                margin: 10px 0;
            }
        `;
        if (!document.head.querySelector("style[data-loading-styles]")) {
            style.setAttribute("data-loading-styles", "true");
            document.head.appendChild(style);
        }

        // Submit form data via AJAX with 5-second delay
        const formData = new FormData(form);
        
        // Show loading for 5 seconds
        setTimeout(() => {
            fetch(form.action, {
                method: "POST",
                body: formData,
                headers: {
                    "X-Requested-With": "XMLHttpRequest"
                }
            })
            .then(response => {
                if (response.ok) {
                    // Redirect to success page
                    window.location.href = response.url;
                } else {
                    throw new Error("Form submission failed");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                loadingOverlay.remove();
                alert("Error submitting form. Please try again.");
            });
        }, 5000); // 5-second delay for async email processing
    }
});
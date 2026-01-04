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
});
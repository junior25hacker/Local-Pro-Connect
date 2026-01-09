# Budget Slider - Frontend Integration Guide

This document provides frontend developers with everything needed to integrate the Budget Slider component with the backend.

---

## 1. API Integration Examples

### Fetch Provider Pricing

**JavaScript:**
```javascript
async function getProviderPricing(providerId) {
  try {
    const response = await fetch(
      `/requests/api/provider/${providerId}/min-price/`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      }
    );
    
    if (!response.ok) {
      if (response.status === 404) {
        throw new Error('Provider not found');
      }
      throw new Error(`Server error: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch provider pricing:', error);
    return null;
  }
}

// Usage
const pricing = await getProviderPricing(88);
if (pricing && pricing.success) {
  console.log(`Min: $${pricing.min_price}`);
  console.log(`Max: $${pricing.max_price}`);
  console.log(`Avg: $${pricing.avg_price}`);
  console.log(`Rate: ${pricing.service_rate}`);
}
```

### Initialize Budget Slider

**JavaScript:**
```javascript
async function initializeBudgetSlider(providerId, sliderElement) {
  const pricing = await getProviderPricing(providerId);
  
  if (!pricing || !pricing.success) {
    console.error('Could not load provider pricing');
    sliderElement.disabled = true;
    return;
  }
  
  // Initialize slider with provider constraints
  const slider = noUiSlider.create(sliderElement, {
    start: [pricing.min_price, pricing.avg_price],
    connect: true,
    step: 5,
    range: {
      'min': pricing.min_price,
      'max': pricing.max_price || pricing.min_price * 10
    }
  });
  
  // Update display as user adjusts slider
  slider.on('update', function(values, handle) {
    const budget = parseFloat(values[handle]);
    updateBudgetDisplay(budget, pricing);
  });
  
  return slider;
}

function updateBudgetDisplay(budget, pricing) {
  const display = document.getElementById('budget-display');
  const warning = document.getElementById('budget-warning');
  
  // Display current budget
  display.textContent = `$${budget.toFixed(2)}`;
  
  // Show service rate info
  const rateInfo = document.getElementById('rate-info');
  rateInfo.textContent = `(${pricing.service_rate} rate)`;
  
  // Show warnings if needed
  if (budget < pricing.min_price) {
    warning.textContent = `⚠️ Below minimum ($${pricing.min_price.toFixed(2)})`;
    warning.className = 'warning error';
  } else if (pricing.max_price && budget > pricing.max_price) {
    warning.textContent = `⚠️ Above maximum ($${pricing.max_price.toFixed(2)})`;
    warning.className = 'warning error';
  } else {
    warning.textContent = '';
  }
}
```

---

## 2. Form Integration

### HTML Form Structure

```html
<form id="serviceRequestForm" method="POST" enctype="multipart/form-data">
  {% csrf_token %}
  
  <!-- Provider Selection -->
  <div class="form-group">
    <label for="provider_choice">Select Provider</label>
    <select id="provider_choice" name="provider_choice" required>
      <option value="">Choose a provider...</option>
      {% for provider in providers %}
        <option value="{{ provider.id }}">{{ provider.company_name }}</option>
      {% endfor %}
    </select>
  </div>
  
  <!-- Budget Slider Container -->
  <div class="form-group">
    <label for="budget_slider">Budget</label>
    <div id="budget_slider" class="slider"></div>
    <div class="slider-display">
      <span>Offered Budget: </span>
      <span id="budget-display">$0.00</span>
      <span id="rate-info"></span>
    </div>
    <div id="budget-warning" class="warning"></div>
    <input 
      type="hidden" 
      id="offered_price" 
      name="offered_price" 
      value="0"
    >
  </div>
  
  <!-- Other form fields... -->
  <div class="form-group">
    <label for="description">Description</label>
    <textarea id="description" name="description" required></textarea>
  </div>
  
  <button type="submit" id="submit-btn">Submit Request</button>
</form>
```

### JavaScript Form Handling

```javascript
document.addEventListener('DOMContentLoaded', function() {
  const providerSelect = document.getElementById('provider_choice');
  const sliderElement = document.getElementById('budget_slider');
  const offeredPriceInput = document.getElementById('offered_price');
  const form = document.getElementById('serviceRequestForm');
  
  let currentSlider = null;
  
  // Initialize slider when provider is selected
  providerSelect.addEventListener('change', async function() {
    if (!this.value) return;
    
    // Clear previous slider
    if (currentSlider) {
      currentSlider.destroy();
    }
    
    // Initialize new slider
    currentSlider = await initializeBudgetSlider(this.value, sliderElement);
    
    if (currentSlider) {
      currentSlider.on('change', function(values, handle) {
        offeredPriceInput.value = parseFloat(values[handle]).toFixed(2);
      });
    }
  });
  
  // Form submission
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Validate budget is set
    const budget = parseFloat(offeredPriceInput.value);
    if (budget <= 0) {
      showError('Please set a budget');
      return;
    }
    
    // Validate against provider minimum
    const providerId = providerSelect.value;
    if (providerId) {
      const pricing = await getProviderPricing(providerId);
      if (budget < pricing.min_price) {
        showError(`Budget must be at least $${pricing.min_price.toFixed(2)}`);
        return;
      }
      if (pricing.max_price && budget > pricing.max_price) {
        showError(`Budget cannot exceed $${pricing.max_price.toFixed(2)}`);
        return;
      }
    }
    
    // Submit form if validation passes
    this.submit();
  });
});

function showError(message) {
  const errorDiv = document.createElement('div');
  errorDiv.className = 'error-message';
  errorDiv.textContent = message;
  document.body.insertBefore(errorDiv, document.body.firstChild);
  
  setTimeout(() => errorDiv.remove(), 5000);
}
```

---

## 3. Response Handling

### Handle API Success

```javascript
const data = {
  "success": true,
  "provider_id": 88,
  "min_price": 50.0,
  "max_price": 500.0,
  "avg_price": 275.0,
  "service_rate": "custom",
  "currency": "USD",
  "company_name": "Handy Expert Services"
};

// Use all fields for UI
console.log(`Provider: ${data.company_name}`);
console.log(`Price range: $${data.min_price} - $${data.max_price}`);
console.log(`Service rate: ${data.service_rate}`);
console.log(`Suggested budget: $${data.avg_price}`);
```

### Handle API Errors

```javascript
async function getProviderPricingSafe(providerId) {
  try {
    const response = await fetch(
      `/requests/api/provider/${providerId}/min-price/`
    );
    
    if (response.status === 404) {
      showUserMessage('Provider not found');
      return null;
    }
    
    if (response.status === 400) {
      showUserMessage('Invalid provider data');
      return null;
    }
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const data = await response.json();
    if (!data.success) {
      showUserMessage(data.error || 'Failed to load pricing');
      return null;
    }
    
    return data;
  } catch (error) {
    console.error('API Error:', error);
    showUserMessage('Failed to load provider pricing. Please try again.');
    return null;
  }
}
```

---

## 4. Budget Display Templates

### Email Preview (How budget appears in notifications)

**Provider Receives:**
```
REQUEST DETAILS
===============
Request ID: #23
Description: Fix my pipes
Offered Budget: $150.00
Service Rate: hourly
Status: Pending
```

**User Receives:**
```
YOUR REQUEST DETAILS
====================
Request ID: #23
Provider: Metro Plumbing Services
Description: Fix my pipes
Offered Budget: $150.00
Submitted: January 9, 2025 14:30
```

---

## 5. CSS Styling

### Budget Slider Styles

```css
/* Slider container */
.form-group .slider {
  width: 100%;
  height: 8px;
  background: #ddd;
  border-radius: 5px;
  margin: 20px 0;
}

/* Slider display */
.slider-display {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
  font-size: 16px;
  font-weight: bold;
}

#budget-display {
  color: #27ae60;
  font-size: 18px;
}

#rate-info {
  font-size: 12px;
  color: #7f8c8d;
}

/* Warning messages */
.warning {
  margin-top: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 13px;
}

.warning.error {
  background-color: #ffe0e0;
  color: #c0392b;
  border: 1px solid #e74c3c;
}

/* Error message (top of page) */
.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 12px 20px;
  border-radius: 4px;
  border: 1px solid #f5c6cb;
  margin-bottom: 20px;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## 6. Testing Scenarios

### Test Case 1: Valid Budget Within Range

```javascript
// Provider: Plumbing ($75-$400)
// User selects: $150

test('Valid budget acceptance', async () => {
  const provider = 1; // Plumbing provider
  const budget = 150;
  
  const pricing = await getProviderPricing(provider);
  expect(budget).toBeGreaterThanOrEqual(pricing.min_price);
  expect(budget).toBeLessThanOrEqual(pricing.max_price);
  
  // Form should accept this budget
  expect(validateBudget(budget, pricing)).toBe(true);
});
```

### Test Case 2: Budget Below Minimum

```javascript
test('Reject budget below minimum', async () => {
  const provider = 1; // Plumbing ($75-$400)
  const budget = 50;
  
  const pricing = await getProviderPricing(provider);
  expect(validateBudget(budget, pricing)).toBe(false);
  
  // Should show: "Budget must be at least $75.00"
});
```

### Test Case 3: Dynamic Provider Change

```javascript
test('Update slider when provider changes', async () => {
  // Select Plumbing ($75-$400)
  selectProvider(1);
  await initializeBudgetSlider(1, sliderElement);
  expect(getSliderMin()).toBe(75);
  
  // Change to Tutoring ($40-$150)
  selectProvider(2);
  await initializeBudgetSlider(2, sliderElement);
  expect(getSliderMin()).toBe(40);
});
```

---

## 7. Accessibility Features

### ARIA Labels for Screen Readers

```html
<div class="form-group">
  <label for="budget_slider">Budget Amount</label>
  <div 
    id="budget_slider" 
    class="slider"
    role="slider"
    aria-label="Budget amount slider"
    aria-valuemin="50"
    aria-valuemax="500"
    aria-valuenow="275"
    aria-describedby="budget-help"
  ></div>
  <div id="budget-help" class="sr-only">
    Select your budget between $50 and $500. Service is hourly-based.
  </div>
</div>
```

### Keyboard Navigation

```javascript
sliderElement.addEventListener('keydown', function(e) {
  if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
    e.preventDefault();
    adjustSlider(10); // Increase by $10
  } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
    e.preventDefault();
    adjustSlider(-10); // Decrease by $10
  }
});
```

---

## 8. Error Handling Best Practices

```javascript
async function loadProviderWithFallback(providerId) {
  try {
    const pricing = await getProviderPricing(providerId);
    
    if (!pricing) {
      // Use defaults if API fails
      console.warn('Using default pricing constraints');
      return {
        min_price: 50,
        max_price: 500,
        avg_price: 275,
        service_rate: 'custom'
      };
    }
    
    return pricing;
  } catch (error) {
    console.error('Critical error loading provider:', error);
    // Disable slider, show manual input instead
    sliderElement.style.display = 'none';
    showManualBudgetInput();
    return null;
  }
}

function showManualBudgetInput() {
  const input = document.createElement('input');
  input.type = 'number';
  input.name = 'offered_price';
  input.placeholder = 'Enter budget manually...';
  input.min = 0;
  input.step = 0.01;
  
  document.getElementById('budget_slider').parentElement.appendChild(input);
}
```

---

## 9. Mobile Responsive Design

```css
/* Mobile optimizations */
@media (max-width: 768px) {
  .slider-display {
    flex-direction: column;
    gap: 5px;
  }
  
  #budget-display {
    font-size: 24px;
    margin: 10px 0;
  }
  
  .form-group .slider {
    height: 12px; /* Larger touch target */
  }
  
  /* Increase touch area */
  .noUi-handle {
    width: 40px;
    height: 40px;
  }
}
```

---

## 10. Browser Compatibility

The backend supports:
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Android)
- Requires JavaScript enabled
- Graceful degradation for older browsers (fallback to text input)

**JavaScript Requirements:**
- ES6+ features supported
- Fetch API support recommended
- Alternative: jQuery AJAX for IE11 support

---

## Quick Integration Checklist

- [ ] Import noUiSlider or equivalent slider library
- [ ] Create HTML structure with slider element
- [ ] Implement getProviderPricing() function
- [ ] Implement initializeBudgetSlider() function
- [ ] Add form validation logic
- [ ] Update hidden input with budget value
- [ ] Test with multiple providers
- [ ] Test error scenarios
- [ ] Add CSS styling
- [ ] Verify accessibility
- [ ] Test on mobile devices
- [ ] Add unit tests

---

## Support

For backend questions:
- See `BUDGET_SLIDER_IMPLEMENTATION.md` for technical details
- See `BUDGET_SLIDER_TESTING.md` for testing procedures
- API endpoint: `/requests/api/provider/<id>/min-price/`

Backend is ready for integration! 🚀

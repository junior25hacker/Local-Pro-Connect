# GEOLOCATION FALLBACK IMPLEMENTATION GUIDE

## Overview
This guide provides detailed implementation steps to add manual address entry as a fallback when users deny location permissions.

---

## 1. FRONTEND IMPLEMENTATION

### Step 1: Update HTML Form
Add a manual address input section after the location display section.

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Location**: After line ~500 (after location display section)

**Add**:
```html
<!-- Location Section with Fallback -->
<div class="form-group">
    <label class="form-label">Share Your Location <span style="color: #DC3545;">*</span></label>
    
    <!-- Geolocation Button -->
    <button type="button" id="shareLocationBtn" class="btn btn-primary btn-lg w-100 mb-3">
        <i class="fas fa-crosshairs"></i> Share My Location
    </button>
    
    <!-- Location Display (shown after successful geolocation) -->
    <div id="locationDisplay" style="display:none;">
        <div class="alert alert-success">
            <i class="fas fa-check-circle"></i> Location Detected
            <div id="locationCoords" class="mt-2"></div>
        </div>
    </div>
    
    <!-- Manual Address Fallback (shown after permission denied) -->
    <div id="manualAddressSection" style="display:none;" class="mt-3">
        <div class="alert alert-info">
            <i class="fas fa-info-circle"></i> 
            Location permission was denied. Please enter your address manually.
        </div>
        <input type="text" id="manual_address" name="manual_address" 
               class="form-control" 
               placeholder="e.g., 123 Main St, Springfield, IL 62701"
               aria-label="Enter your address manually">
        <small class="form-text text-muted d-block mt-2">
            Your address will help providers locate and assist you faster.
        </small>
    </div>
    
    <!-- Hidden fields for form submission -->
    <input type="hidden" id="location_lat" name="location_lat">
    <input type="hidden" id="location_lng" name="location_lng">
    <input type="hidden" id="address" name="address">
</div>
```

### Step 2: Update JavaScript Error Handling

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Replace lines 632-643** (the geolocation error handler) with:

```javascript
function(error) {
    let errorMessage = '';
    let showManualEntry = false;
    
    console.error('Geolocation error:', error);
    
    switch(error.code) {
        case error.PERMISSION_DENIED:
            errorMessage = 'Location permission was denied. ';
            errorMessage += 'You can enter your address manually to proceed.';
            showManualEntry = true;
            console.warn('User denied geolocation permission');
            break;
            
        case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable. ';
            errorMessage += 'Please check your device settings or enter your address manually.';
            showManualEntry = true;
            console.warn('Position unavailable');
            break;
            
        case error.TIMEOUT:
            errorMessage = 'Location request timed out. ';
            errorMessage += 'Please try again or enter your address manually.';
            showManualEntry = true;
            console.warn('Geolocation timeout');
            break;
            
        default:
            errorMessage = 'Unable to get your location. ';
            errorMessage += 'Please enter your address manually.';
            showManualEntry = true;
            console.warn('Unknown geolocation error');
    }
    
    // Show error alert
    const errorAlert = document.createElement('div');
    errorAlert.className = 'alert alert-warning alert-dismissible fade show';
    errorAlert.role = 'alert';
    errorAlert.innerHTML = `
        <i class="fas fa-exclamation-triangle"></i> ${errorMessage}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.getElementById('locationDisplay').parentNode.insertBefore(
        errorAlert, 
        document.getElementById('locationDisplay')
    );
    
    // Show manual entry option if applicable
    if (showManualEntry) {
        document.getElementById('manualAddressSection').style.display = 'block';
    }
    
    // Reset button state
    shareLocationBtn.innerHTML = '<i class="fas fa-crosshairs"></i> Try Again';
    shareLocationBtn.disabled = false;
    
    // Trigger validation (may enable submit if manual address provided)
    validateForm();
}
```

### Step 3: Update Form Validation

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Replace the validateForm() function (lines 646-662)** with:

```javascript
function validateForm() {
    const emergencyType = document.querySelector('input[name="emergency_type"]:checked');
    const description = document.getElementById('description').value.trim();
    const contactPhone = document.getElementById('contact_phone').value.trim();
    const hasProvider = selectedProvider !== null;
    
    // Check for location - can be either geolocation OR manual address
    const hasAutoLocation = currentLocation !== null;
    const manualAddressInput = document.getElementById('manual_address');
    const hasManualAddress = manualAddressInput && manualAddressInput.value.trim() !== '';
    const hasLocation = hasAutoLocation || hasManualAddress;
    
    // Validate all required fields
    const isValid = emergencyType && description && contactPhone && hasLocation && hasProvider;
    
    // Update submit button state
    submitBtn.disabled = !isValid;
    submitBtn.style.opacity = isValid ? '1' : '0.6';
    
    // Log validation state for debugging
    if (!isValid) {
        console.log('Form validation failed:', {
            emergencyType: !!emergencyType,
            description: !!description,
            contactPhone: !!contactPhone,
            hasLocation: hasLocation,
            hasAutoLocation: hasAutoLocation,
            hasManualAddress: hasManualAddress,
            hasProvider: hasProvider
        });
    }
}
```

### Step 4: Add Real-Time Validation for Manual Address

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Add after line 718** (after existing event listeners):

```javascript
// Real-time validation for manual address entry
const manualAddressInput = document.getElementById('manual_address');
if (manualAddressInput) {
    manualAddressInput.addEventListener('input', function() {
        // When user types address, update the hidden address field
        document.getElementById('address').value = this.value;
        validateForm();
    });
    
    // Allow form submission with manual address if enter key pressed
    manualAddressInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            validateForm();
        }
    });
}
```

### Step 5: Update Form Submission

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Update the form submission handler (lines 664-676)** to handle both geolocation and manual address:

```javascript
// Form submission
form.addEventListener('submit', function(e) {
    e.preventDefault();
    
    // Check that we have either geolocation or manual address
    const hasAutoLocation = currentLocation !== null;
    const manualAddress = document.getElementById('manual_address')?.value.trim();
    
    if (!hasAutoLocation && !manualAddress) {
        alert('Please share your location or enter your address manually.');
        return;
    }
    
    if (!selectedProvider) {
        alert('Please select a provider.');
        return;
    }
    
    // Show loading state
    submitBtn.innerHTML = '<span class="loading"></span> Sending Request...';
    submitBtn.disabled = true;
    
    // Build form data
    const formData = new FormData(form);
    
    // If using manual address, ensure it's set
    if (!hasAutoLocation && manualAddress) {
        formData.set('address', manualAddress);
        formData.set('location_lat', '');
        formData.set('location_lng', '');
    }
    
    // Submit form
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('successMessage').style.display = 'block';
            submitBtn.innerHTML = '<i class="fas fa-check"></i> Request Sent!';
            submitBtn.style.background = 'linear-gradient(135deg, #28A745 0%, #20C997 100%)';
            
            // Redirect after success
            setTimeout(() => {
                window.location.href = '{% url "accounts:user_profile" %}';
            }, 3000);
        } else {
            alert('Error: ' + (data.error || 'Unknown error occurred'));
            submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Emergency Request';
            submitBtn.disabled = false;
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An error occurred while sending your request. Please try again.');
        submitBtn.innerHTML = '<i class="fas fa-paper-plane"></i> Send Emergency Request';
        submitBtn.disabled = false;
    });
});
```

---

## 2. BACKEND IMPLEMENTATION

### Step 1: Update View Validation

**File**: `Django/accounts/views.py`

**Update the emergency_request view (lines 256-356)** to handle both geolocation and manual address:

```python
@login_required
def emergency_request(request):
    """
    Handle emergency service requests with location sharing and provider selection.
    Supports both automatic geolocation and manual address entry.
    """
    if request.method == 'POST':
        # Handle emergency request submission
        emergency_type = request.POST.get('emergency_type', '').strip()
        description = request.POST.get('description', '').strip()
        location_lat = request.POST.get('location_lat', '').strip()
        location_lng = request.POST.get('location_lng', '').strip()
        address = request.POST.get('address', '').strip()
        manual_address = request.POST.get('manual_address', '').strip()
        selected_provider_id = request.POST.get('selected_provider', '').strip()
        contact_phone = request.POST.get('contact_phone', '').strip()

        # Validate required fields
        if not all([emergency_type, description, contact_phone, selected_provider_id]):
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'error': 'Please fill in all required fields.'
                })
            messages.error(request, 'Please fill in all required fields.')
            return redirect('accounts:emergency_request')

        # Validate location - must have either geolocation or manual address
        has_geolocation = location_lat and location_lng
        has_manual_address = manual_address
        
        if not (has_geolocation or has_manual_address):
            error_msg = 'Please share your location or enter your address manually.'
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': error_msg})
            messages.error(request, error_msg)
            return redirect('accounts:emergency_request')

        try:
            # Get the selected provider
            selected_provider = User.objects.get(id=selected_provider_id)
            provider_profile = ProviderProfile.objects.get(user=selected_provider)

            # Determine final address
            if has_geolocation:
                # Use geolocation-based address if available
                final_address = address or f"Lat: {location_lat}, Lng: {location_lng}"
                location_info = f"Coordinates: {location_lat}, {location_lng}"
            else:
                # Use manual address
                final_address = manual_address
                location_info = "Location: Manually entered"
                logger.info(f"Emergency request using manual address: {manual_address}")

            # Create emergency service request
            emergency_request = ServiceRequest.objects.create(
                user=request.user,
                provider=selected_provider,
                provider_name=provider_profile.company_name or selected_provider.get_full_name(),
                description=f"EMERGENCY {emergency_type.upper()}: {description}\n\nLocation: {final_address}\n{location_info}\nContact Phone: {contact_phone}",
                urgent=True,
                status='pending'
            )

            # Update user profile with phone if not set
            user_profile, created = UserProfile.objects.get_or_create(user=request.user)
            if not user_profile.phone:
                user_profile.phone = contact_phone
                user_profile.save()

            # Send email notification to provider
            try:
                location_details = f"Location: {final_address}\n{location_info}" if has_geolocation else f"Location: {final_address} (manually entered)"
                
                send_mail(
                    subject=f'EMERGENCY SERVICE REQUEST - {emergency_type.upper()}',
                    message=f"""EMERGENCY SERVICE REQUEST

Type: {emergency_type.upper()}
Description: {description}

Customer: {request.user.get_full_name()} ({request.user.email})
Phone: {contact_phone}
{location_details}

This is an EMERGENCY request. Please respond immediately!

View request: {request.build_absolute_uri(f'/requests/detail/{emergency_request.id}/')}""",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[selected_provider.email],
                    fail_silently=True
                )
                emergency_request.email_sent_to_provider = True
                emergency_request.email_sent_to_provider_timestamp = timezone.now()
                emergency_request.save()
            except Exception as e:
                logger.error(f"Failed to send emergency email: {e}")

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Emergency request sent successfully! Help is on the way.',
                    'request_id': emergency_request.id
                })

            messages.success(request, 'Emergency request sent successfully! Help is on the way.')
            return redirect('accounts:user_profile')

        except User.DoesNotExist:
            error_msg = 'Selected provider not found.'
        except ProviderProfile.DoesNotExist:
            error_msg = 'Provider profile not found.'
        except Exception as e:
            logger.error(f"Error creating emergency request: {e}")
            error_msg = 'An error occurred while processing your request.'

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': error_msg})

        messages.error(request, error_msg)
        return redirect('accounts:emergency_request')

    # Get nearby providers for the emergency request
    nearby_providers = ProviderProfile.objects.all()[:10]

    context = {
        'nearby_providers': nearby_providers,
        'user_profile': UserProfile.objects.get(user=request.user) if UserProfile.objects.filter(user=request.user).exists() else None
    }

    return render(request, 'accounts/emergency_request.html', context)
```

### Step 2: Add Import for timezone

**File**: `Django/accounts/views.py`

**Add to imports at top** (if not already present):
```python
from django.utils import timezone
```

---

## 3. CSS ENHANCEMENTS (Optional but Recommended)

**File**: `Django/accounts/templates/accounts/emergency_request.html`

**Add to the `<style>` section**:

```css
/* Manual address input styling */
#manual_address {
    border: 2px solid #FFC107;
    padding: 0.75rem;
    font-size: 1rem;
    border-radius: 8px;
    transition: all 0.3s ease;
}

#manual_address:focus {
    border-color: #FF6B6B;
    box-shadow: 0 0 0 0.2rem rgba(255, 107, 107, 0.25);
}

#manual_address::placeholder {
    color: #999;
}

/* Alert styling */
.alert-info {
    background-color: #D1ECF1;
    border-color: #BEE5EB;
    color: #0C5460;
    border-radius: 8px;
    padding: 1rem;
}

.alert-warning {
    background-color: #FFF3CD;
    border-color: #FFEAA7;
    color: #856404;
    border-radius: 8px;
    padding: 1rem;
}

/* Location display improvements */
#locationDisplay {
    margin-top: 1rem;
    animation: slideIn 0.3s ease;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateY(-10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Manual address section */
#manualAddressSection {
    animation: slideIn 0.3s ease;
    background: #F8F9FA;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #FFC107;
}
```

---

## 4. ERROR MESSAGE LOCALIZATION (Optional)

For multi-language support, create a constants file:

**File**: `Django/accounts/geolocation_messages.py`

```python
GEOLOCATION_ERRORS = {
    'PERMISSION_DENIED': {
        'title': 'Location Permission Denied',
        'message': 'Location permission was denied. You can enter your address manually to proceed.',
        'show_manual': True,
    },
    'POSITION_UNAVAILABLE': {
        'title': 'Location Unavailable',
        'message': 'Location information is unavailable. Please check your device settings or enter your address manually.',
        'show_manual': True,
    },
    'TIMEOUT': {
        'title': 'Location Request Timed Out',
        'message': 'Location request timed out. Please try again or enter your address manually.',
        'show_manual': True,
    },
    'UNKNOWN': {
        'title': 'Unable to Get Location',
        'message': 'Unable to get your location. Please enter your address manually.',
        'show_manual': True,
    },
}
```

---

## 5. TESTING CHECKLIST

### Frontend Testing
- [ ] Click "Share My Location" with location enabled - should capture coordinates
- [ ] Click "Share My Location" with location disabled - should show error and manual entry field
- [ ] Enter address manually - form should validate
- [ ] Submit form with manual address - should work
- [ ] Submit form with geolocation - should work
- [ ] Try to submit without address - should show validation error
- [ ] Test on mobile browser - geolocation should work
- [ ] Test on desktop browser - geolocation should work
- [ ] Test on browser with location disabled - fallback should appear

### Backend Testing
- [ ] Emergency request with geolocation should save coordinates
- [ ] Emergency request with manual address should save address text
- [ ] Email notification should include correct address
- [ ] User profile phone should update if empty
- [ ] Request should be marked as urgent=True
- [ ] Provider should receive email notification

### Edge Cases
- [ ] User denies permission, then allows it - "Try Again" button should work
- [ ] User enters manual address, then clicks "Share Location" - coordinates should override
- [ ] Very long address entry - should not break form
- [ ] Special characters in address - should handle properly
- [ ] Empty address submission - should fail validation

---

## 6. DEPLOYMENT CHECKLIST

- [ ] Code reviewed by team
- [ ] All tests passing
- [ ] No console errors
- [ ] Mobile responsiveness verified
- [ ] Email notifications tested
- [ ] Backwards compatibility confirmed
- [ ] Performance impact assessed
- [ ] Database backup taken
- [ ] Staging deployment successful
- [ ] Production deployment with monitoring

---

## 7. MONITORING & ROLLBACK

### Metrics to Monitor
- Emergency request creation success rate
- Geolocation permission denial rate
- Manual address entry usage rate
- Email delivery success rate
- Average request response time

### Rollback Plan
If issues occur:
1. Disable manual address validation in frontend
2. Require geolocation only (revert changes)
3. Notify users via email
4. Investigate issue
5. Re-deploy fix

---

## 8. FUTURE ENHANCEMENTS

### Phase 2 Improvements
1. **Address autocomplete** using Google Places API or similar
2. **Map visualization** showing address location before submission
3. **Nearby providers selection** based on entered address
4. **Address validation** using external geocoding service
5. **User address history** for quick re-entry

### Phase 3 Features
1. **Real-time provider tracking** with map integration
2. **ETA updates** sent via SMS/push notifications
3. **In-transit chat** between user and provider
4. **Photo sharing** for damage documentation
5. **Signature capture** for proof of service


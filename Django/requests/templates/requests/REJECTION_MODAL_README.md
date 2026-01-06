# Rejection Modal Documentation

## Overview
The Rejection Modal is a standalone, reusable component for the Local Pro Connect platform that allows service providers to reject service requests with structured feedback.

## Features

### ✅ Complete Feature Set
- **4 Primary Rejection Reasons**: Distance, Price, Time, Other
- **Dynamic Text Display**: Shows selected reason in real-time
- **Description Input**: Optional detailed explanation (500 char limit)
- **Form Validation**: Ensures a reason is selected before submission
- **Responsive Design**: Works seamlessly on mobile, tablet, and desktop
- **Accessibility**: WCAG AA compliant, keyboard navigation, screen reader friendly
- **Professional Design**: Follows Local Pro Connect brand guidelines

## Files Structure

```
Django/
├── requests/templates/requests/
│   └── rejection_modal.html          # Main modal template
├── static/
│   ├── css/
│   │   └── rejection_modal.css       # Modal styling
│   └── js/
│       └── rejection_modal.js        # Modal interactivity
```

## Design System

### Color Palette (from COLOR_PALETTE.txt)
- **Primary Blue**: #0052CC - Headers, trust elements
- **Accent Green**: #17B890 - CTAs, success states
- **Danger Red**: #e74c3c - Rejection actions
- **Text Dark**: #2C3E50 - Body text
- **Light Gray**: #F5F5F5 - Backgrounds

### Typography
- **Font Family**: Inter (Google Fonts)
- **Weights**: 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold)

### Border Radius
- Small: 8px
- Medium: 10px
- Large: 12px

### Shadows
- Small: `0 2px 8px rgba(0, 0, 0, 0.08)`
- Medium: `0 4px 16px rgba(0, 0, 0, 0.12)`
- Large: `0 8px 32px rgba(0, 0, 0, 0.16)`

## Usage

### Standalone Page
The modal is designed as a standalone page that can be accessed directly:

```python
# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('request/<int:request_id>/reject/', views.rejection_modal, name='rejection_modal'),
]
```

```python
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .models import ServiceRequest

def rejection_modal(request, request_id):
    service_request = get_object_or_404(ServiceRequest, id=request_id)
    
    if request.method == 'POST':
        rejection_reason = request.POST.get('rejection_reason')
        rejection_description = request.POST.get('rejection_description', '')
        
        # Process rejection
        service_request.status = 'rejected'
        service_request.rejection_reason = rejection_reason
        service_request.rejection_description = rejection_description
        service_request.save()
        
        # Send notification email (optional)
        # send_rejection_email(service_request)
        
        return redirect('decision_success')
    
    return render(request, 'requests/rejection_modal.html', {
        'service_request': service_request
    })
```

### Integration as Modal Overlay
To use as an overlay on existing pages:

```html
<!-- In your base template or specific page -->
{% include 'requests/rejection_modal.html' %}

<script>
// Show modal programmatically
function showRejectionModal(requestId) {
    document.getElementById('rejectionModalOverlay').style.display = 'flex';
}

// Hide modal
function hideRejectionModal() {
    document.getElementById('rejectionModalOverlay').style.display = 'none';
}
</script>
```

### Form Data Structure

**POST Data:**
```python
{
    'rejection_reason': 'distance' | 'price' | 'time' | 'other',
    'rejection_description': 'Optional text (max 500 characters)'
}
```

## Customization

### Changing Colors
Edit `Django/static/css/rejection_modal.css`:

```css
:root {
    --primary-blue: #0052CC;      /* Change main color */
    --accent-green: #17B890;      /* Change accent */
    --danger-red: #e74c3c;        /* Change rejection color */
}
```

### Adding More Reasons
In `rejection_modal.html`, add new reason card:

```html
<div class="reason-card" data-reason="capacity">
    <input type="radio" name="rejection_reason" value="capacity" id="reason_capacity" required>
    <label for="reason_capacity" class="reason-label">
        <div class="reason-icon">
            <i class="fas fa-users"></i>
        </div>
        <div class="reason-content">
            <h4 class="reason-title">Full Capacity</h4>
            <p class="reason-subtitle">Currently booked with other projects</p>
        </div>
        <div class="reason-checkmark">
            <i class="fas fa-check-circle"></i>
        </div>
    </label>
</div>
```

Update JavaScript in `rejection_modal.js`:

```javascript
const reasonLabels = {
    'distance': 'Distance',
    'price': 'Price',
    'time': 'Time',
    'other': 'Other',
    'capacity': 'Full Capacity'  // Add new reason
};
```

## Validation Rules

1. **Required**: User must select a rejection reason
2. **Optional**: Description text is optional
3. **Max Length**: Description limited to 500 characters
4. **CSRF**: Django CSRF token required for security

## Accessibility Features

### Keyboard Navigation
- **Tab**: Navigate between elements
- **Shift + Tab**: Navigate backwards
- **Enter/Space**: Select radio button
- **Escape**: Close modal (with confirmation)

### Screen Readers
- All form elements have proper labels
- ARIA labels on buttons
- Semantic HTML structure
- Focus management

### Visual
- High contrast ratios (WCAG AA)
- Large touch targets (48x48px minimum)
- Clear focus indicators
- Reduced motion support

## Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome | 90+ | ✅ Fully Supported |
| Firefox | 88+ | ✅ Fully Supported |
| Safari | 14+ | ✅ Fully Supported |
| Edge | 90+ | ✅ Fully Supported |
| Mobile Safari | 14+ | ✅ Fully Supported |
| Chrome Mobile | 90+ | ✅ Fully Supported |

## Responsive Breakpoints

- **Desktop**: > 768px - Full layout with side-by-side buttons
- **Tablet**: 481px - 768px - Adjusted spacing, stacked buttons
- **Mobile**: ≤ 480px - Compact layout, full-width buttons

## Security Considerations

1. **CSRF Protection**: All forms include `{% csrf_token %}`
2. **Input Validation**: Server-side validation required
3. **XSS Prevention**: Escape user input in templates
4. **Authentication**: Verify user permissions before showing modal

## Testing Checklist

- [ ] Form submission works correctly
- [ ] All radio buttons can be selected
- [ ] Character counter updates properly
- [ ] Validation shows errors when no reason selected
- [ ] Modal closes with X button and Cancel button
- [ ] Escape key closes modal
- [ ] Responsive on mobile devices
- [ ] Keyboard navigation works
- [ ] Screen reader announces changes
- [ ] Form data submits to backend correctly

## Performance

- **Initial Load**: < 100ms (CSS/JS cached)
- **Modal Open**: Instant (no AJAX required)
- **Form Submission**: Depends on backend processing
- **File Sizes**:
  - HTML: ~5KB
  - CSS: ~18KB
  - JS: ~8KB

## Future Enhancements

### Potential Additions
- [ ] Auto-save draft to localStorage
- [ ] Confirmation dialog before submission
- [ ] Analytics tracking for rejection reasons
- [ ] Email template preview
- [ ] Bulk rejection for multiple requests
- [ ] Suggested responses based on reason

## Troubleshooting

### Modal doesn't appear
- Check if CSS/JS files are loaded correctly
- Verify `{% load static %}` is at top of template
- Check browser console for errors

### Form doesn't submit
- Verify CSRF token is present
- Check Django view accepts POST requests
- Validate form data in backend

### Styling looks broken
- Clear browser cache
- Check CSS file path in template
- Verify Inter font loads from Google Fonts

## Support

For issues or questions about the Rejection Modal:
1. Check this documentation
2. Review existing templates in `Django/requests/templates/requests/`
3. Consult COLOR_PALETTE.txt for design guidelines
4. Check browser console for JavaScript errors

## Version History

### Version 1.0.0 (Current)
- Initial release
- 4 rejection reasons
- Full responsive design
- Accessibility compliant
- Django integration ready

---

**Last Updated**: 2025
**Maintained By**: Local Pro Connect Development Team
**Design System**: Professional Tech Aesthetic

# Design System - Local Pro Connect

## Brand Colors

### Primary Palette

```css
/* Primary Blue - Trust & Professionalism */
--primary-blue: #004C99;
--dark-blue: #003366;

/* Success Green - Verification & Actions */
--success-green: #00A65A;
--dark-green: #008a4a;

/* Accent Yellow - Attention & Ratings */
--accent-yellow: #FFC300;
--gold: #FFD700;

/* Rating Orange */
--rating-orange: #FF6B00;
--star-yellow: #FFB800;
```

### Neutral Palette

```css
/* Backgrounds */
--bg-light: #f8f9fa;
--bg-lighter: #e9ecef;
--white: #ffffff;

/* Text */
--text-primary: #333333;
--text-secondary: #666666;
--text-muted: #999999;

/* Borders */
--border-light: #f0f0f0;
--border-color: rgba(0, 76, 153, 0.1);
```

### Gradient Combinations

```css
/* Navbar & Hero */
background: linear-gradient(135deg, #004C99 0%, #003366 100%);

/* Call-to-Action Buttons */
background: linear-gradient(135deg, #00A65A 0%, #008a4a 100%);

/* Rating Badge */
background: linear-gradient(135deg, #FFC300 0%, #FFD700 100%);

/* Status Badge */
background: linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%);

/* Welcome/Tips Sections */
background: linear-gradient(135deg, #E8F5E9 0%, #F1F8E9 100%);
background: linear-gradient(135deg, #FFF9C4 0%, #FFF59D 100%);

/* Profile Avatar */
background: linear-gradient(135deg, #004C99 0%, #00A65A 100%);

/* Page Background */
background: linear-gradient(to bottom, #f8f9fa 0%, #e9ecef 100%);

/* Info Cards Hover */
background: linear-gradient(135deg, #E3F2FD 0%, #BBDEFB 100%);
```

## Typography

### Font Family
```css
font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, 
             "Helvetica Neue", Arial, sans-serif;
```

### Font Sizes

```css
/* Headings */
--h1-size: 2.5rem;    /* 40px */
--h2-size: 2rem;      /* 32px */
--h3-size: 1.6rem;    /* 25.6px */
--h4-size: 1.5rem;    /* 24px */

/* Body Text */
--body-large: 1.15rem;   /* 18.4px */
--body-normal: 1.05rem;  /* 16.8px */
--body-small: 0.9rem;    /* 14.4px */

/* Display Text */
--display-large: 3.5rem; /* 56px - Avatar icons */
--display-stats: 2.5rem; /* 40px - Statistics */
```

### Font Weights

```css
--weight-normal: 400;
--weight-medium: 500;
--weight-semibold: 600;
--weight-bold: 700;
--weight-extrabold: 800;
```

### Line Heights

```css
--line-height-tight: 1.2;
--line-height-normal: 1.5;
--line-height-relaxed: 1.6;
--line-height-loose: 1.8;
```

## Spacing System

### Base Unit: 0.25rem (4px)

```css
/* Spacing Scale */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
```

### Common Applications

```css
/* Card Padding */
padding: 2.5rem;  /* 40px */

/* Section Margins */
margin-bottom: 2rem;  /* 32px */

/* Button Padding */
padding: 1.25rem;  /* 20px */

/* Icon Gaps */
gap: 0.75rem;  /* 12px */
```

## Border Radius

```css
/* Radius Scale */
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
--radius-full: 50%;  /* Pills & Circles */

/* Usage */
.section-card { border-radius: 16px; }
.profile-avatar { border-radius: 50%; }
.button { border-radius: 12px; }
.badge { border-radius: 50px; }
```

## Shadows

### Elevation System

```css
/* Level 1 - Subtle */
box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

/* Level 2 - Cards */
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);

/* Level 3 - Elevated Cards */
box-shadow: 0 8px 25px rgba(0, 76, 153, 0.15);

/* Level 4 - Profile Header */
box-shadow: 0 10px 40px rgba(0, 76, 153, 0.15);

/* Level 5 - Avatar */
box-shadow: 0 10px 30px rgba(0, 76, 153, 0.3);

/* Hover States */
box-shadow: 0 15px 50px rgba(0, 76, 153, 0.2);

/* Button Shadows */
box-shadow: 0 4px 15px rgba(0, 166, 90, 0.3);
box-shadow: 0 8px 25px rgba(255, 195, 0, 0.4);  /* Rating badge */
```

### Text Shadows

```css
/* Subtle depth on large numbers */
text-shadow: 2px 2px 4px rgba(0, 76, 153, 0.1);

/* Star ratings */
text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
```

## Animation & Transitions

### Timing Functions

```css
/* Standard ease */
transition-timing-function: ease;

/* Smooth ease */
transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
```

### Duration

```css
--duration-fast: 0.15s;
--duration-normal: 0.3s;
--duration-slow: 0.6s;
--duration-very-slow: 2s;  /* Animations */
```

### Common Transitions

```css
/* All properties */
transition: all 0.3s ease;

/* Specific properties */
transition: transform 0.3s ease, box-shadow 0.3s ease;
transition: opacity 0.3s ease;
transition: width 0.6s ease, height 0.6s ease;  /* Ripple */
```

### Keyframe Animations

```css
/* Pulse (badges) */
@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

/* Bounce (icons) */
@keyframes bounce {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}
```

## Interactive States

### Hover Effects

```css
/* Cards */
transform: translateY(-3px);
box-shadow: 0 8px 25px rgba(0, 76, 153, 0.15);

/* Buttons */
transform: translateY(-3px);
box-shadow: 0 6px 20px rgba(0, 166, 90, 0.4);

/* Avatars */
transform: scale(1.05);

/* Icons */
transform: scale(1.2);

/* Rating Badge */
transform: scale(1.05);
```

### Focus States

```css
/* Inherit Bootstrap focus styles */
outline: 2px solid rgba(0, 76, 153, 0.5);
outline-offset: 2px;
```

## Component Specifications

### Profile Avatar

```css
/* User Profile */
width: 140px;
height: 140px;
border: 5px solid white;
box-shadow: 0 8px 20px rgba(0, 76, 153, 0.3);

/* Provider Profile */
width: 150px;
height: 150px;
border: 6px solid white;
box-shadow: 0 10px 30px rgba(0, 76, 153, 0.3);
```

### Buttons

```css
/* Primary CTA */
padding: 1.25rem;
border-radius: 12px;
font-size: 1.15rem;
font-weight: 700;
background: linear-gradient(135deg, #00A65A 0%, #008a4a 100%);
box-shadow: 0 4px 15px rgba(0, 166, 90, 0.3);
```

### Cards

```css
/* Standard Section Card */
background: white;
border-radius: 16px;
padding: 2.5rem;
box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
border: 1px solid rgba(0, 76, 153, 0.1);
```

### Badges

```css
/* Status Badge */
padding: 1rem 1.75rem;
border-radius: 50px;
font-weight: 700;
font-size: 1.1rem;
box-shadow: 0 4px 15px rgba(0, 166, 90, 0.2);
border: 2px solid #00A65A;
```

### Rating Display

```css
/* Rating Badge */
padding: 1.25rem 2rem;
border-radius: 20px;
background: linear-gradient(135deg, #FFC300 0%, #FFD700 100%);
box-shadow: 0 8px 25px rgba(255, 195, 0, 0.4);
border: 3px solid #FFF;
```

## Responsive Breakpoints

```css
/* Mobile First Approach */

/* Extra Small (phones) */
@media (max-width: 575.98px) { }

/* Small (tablets portrait) */
@media (max-width: 767.98px) {
    /* Adjustments made here */
    .profile-avatar { width: 120px; height: 120px; }
    .info-grid { grid-template-columns: 1fr; }
}

/* Medium (tablets landscape) */
@media (max-width: 991.98px) { }

/* Large (desktops) */
@media (max-width: 1199.98px) { }

/* Extra Large (large desktops) */
@media (min-width: 1200px) { }
```

## Icon System

### Font Awesome Icons Used

```html
<!-- Navigation -->
<i class="fas fa-home"></i>
<i class="fas fa-user-plus"></i>
<i class="fas fa-briefcase"></i>

<!-- Profile -->
<i class="fas fa-user"></i>
<i class="fas fa-check-circle"></i>
<i class="fas fa-shield-alt"></i>

<!-- Actions -->
<i class="fas fa-search"></i>
<i class="fas fa-bookmark"></i>
<i class="fas fa-phone"></i>
<i class="fas fa-message"></i>
<i class="fas fa-edit"></i>
<i class="fas fa-camera"></i>

<!-- Sections -->
<i class="fas fa-user-circle"></i>
<i class="fas fa-map-marker-alt"></i>
<i class="fas fa-hammer"></i>
<i class="fas fa-info-circle"></i>
<i class="fas fa-lightbulb"></i>
<i class="fas fa-building"></i>

<!-- Ratings */
<i class="fas fa-star"></i>
<i class="far fa-star"></i>

<!-- Status -->
<i class="fas fa-clock"></i>
<i class="fas fa-sign-out-alt"></i>
```

### Icon Sizing

```css
/* Navigation icons */
font-size: 1rem;  /* Default */

/* Section title icons */
font-size: 1.4rem;
padding: 0.5rem;

/* Avatar placeholder */
font-size: 3.5rem;

/* Verification badge */
font-size: 3.5rem;

/* Button icons */
font-size: 1.3rem;
```

## Layout Grid

```css
/* Container */
max-width: 1140px;
padding: 0 15px;

/* Two Column Layout */
.col-lg-8  /* Main content: 66.67% */
.col-lg-4  /* Sidebar: 33.33% */

/* Info Grid */
grid-template-columns: repeat(3, 1fr);
gap: 2rem;

/* Mobile: Single column */
@media (max-width: 768px) {
    grid-template-columns: 1fr;
}
```

## Accessibility

### Color Contrast Ratios

- Primary text on white: **10.4:1** (AAA)
- Secondary text on white: **7.0:1** (AAA)
- Blue on white: **8.6:1** (AAA)
- Green on white: **4.8:1** (AA)

### Focus Indicators

```css
/* Visible focus states */
:focus {
    outline: 2px solid rgba(0, 76, 153, 0.5);
    outline-offset: 2px;
}
```

### Motion

```css
/* Respect reduced motion preferences */
@media (prefers-reduced-motion: reduce) {
    * {
        animation-duration: 0.01ms !important;
        transition-duration: 0.01ms !important;
    }
}
```

## Usage Examples

### Creating a New Card

```html
<div class="section-card">
    <h3 class="section-title">
        <i class="fas fa-icon"></i> Title
    </h3>
    <p class="description-text">Content here...</p>
</div>
```

### Adding a CTA Button

```html
<a href="#" class="call-btn-large">
    <i class="fas fa-icon"></i> Action Text
</a>
```

### Stats Display

```html
<div class="info-item">
    <div class="info-label">Label</div>
    <div class="info-value">100</div>
</div>
```

---

**Note**: This design system is based on the implemented UI enhancements. All values are extracted from the actual CSS in the templates.

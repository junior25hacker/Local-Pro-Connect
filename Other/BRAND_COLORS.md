# Local Pro Connect - Brand Color Reference

## Official Brand Colors (from Logo)

### Primary Colors
```
Primary Blue:     #0052CC
Accent Green:     #17B890
Bright Yellow:    #FFC300
```

### Supporting Colors
```
Dark Text:        #2C3E50
Light Blue:       #E8F0FE
Light Green:      #E8F5F0
Light Gray:       #F5F5F5
Border Gray:      #E8E8E8
Pure White:       #FFFFFF
```

## Component Color Usage

### Navigation Bar
- Background: Primary Blue (#0052CC)
- Logo badge: Gradient (Primary Blue → Accent Green)
- Logo accent: Bright Yellow (#FFC300)
- Text: White
- Links on hover: Accent Green (#17B890)

### Hero Section
- Background gradient: Primary Blue → #003d99
- Decorative shapes: Light Green (opacity 0.15), Light Yellow (opacity 0.08)
- Text: White
- Button (primary): Accent Green
- Button (secondary): White border with transparent bg

### Service Categories
- Background gradient: Light Blue → Light Green
- Text: Primary Blue
- Border on hover: Accent Green
- Box shadow: Primary Blue (opacity 0.15)

### How It Works Section
- Background: Light Blue (#E8F0FE)
- Step numbers: Accent Green circles with white text
- Titles: Primary Blue
- Text: Dark Gray (#666)

### Features Section
- Background: Light Gray (#F5F5F5)
- Icons: Accent Green
- Top border: Accent Green
- Titles: Primary Blue
- Text: Dark Gray

### Testimonials
- Background: Light Gray
- Card border: Bright Yellow
- Author name: Primary Blue
- Stars: Bright Yellow
- Text: Dark Gray

### CTA Section
- Background: Primary Blue (gradient)
- Decorative shapes: Light Green (opacity 0.1)
- Buttons: Bright Yellow with Primary Blue text
- Text: White

### Footer
- Background: Primary Blue
- Section headers: Bright Yellow
- Links: White (opacity 0.8)
- Links on hover: Accent Green
- Border: White (opacity 0.2)

## Form Elements

### Text Inputs
- Border (default): Border Gray (#E8E8E8)
- Border (focus): Primary Blue (#0052CC)
- Shadow (focus): rgba(0, 82, 204, 0.1)
- Error border: #e74c3c
- Placeholder: #999

### Checkboxes
- Border: Border Gray
- Checked: Accent Green
- Focus shadow: rgba(0, 82, 204, 0.25)

### Buttons
- Primary (green): Accent Green (#17B890)
- Primary hover: #139a77
- Secondary (yellow): Bright Yellow (#FFC300)
- Secondary hover: #ffb800
- Shadow: rgba of button color with 0.3 opacity

## Implementation Notes

All colors are defined as CSS variables in the `:root` selector:

```css
:root {
    --primary-blue: #0052CC;
    --accent-green: #17B890;
    --accent-yellow: #FFC300;
    --bg-white: #FFFFFF;
    --text-dark: #2C3E50;
    --light-blue: #E8F0FE;
    --light-green: #E8F5F0;
    --light-gray: #F5F5F5;
    --border-gray: #E8E8E8;
}
```

This allows for:
- Easy theme updates by changing variable values
- Consistent color application across components
- Flexible opacity values: `rgba(0, 82, 204, 0.1)`
- Quick brand compliance checks

## Brand Color Psychology

- **Primary Blue (#0052CC)**: Trust, stability, professionalism - perfect for headers and primary branding
- **Accent Green (#17B890)**: Growth, verification, success - ideal for CTAs and positive actions
- **Bright Yellow (#FFC300)**: Attention, happiness, ratings - highlights important elements and star ratings
- **Dark Text (#2C3E50)**: Professional, readable, serious - for body copy and important information

---

**Color Palette Created**: December 8, 2025
**Source**: Local Pro Connect Logo
**All colors verified and implemented across all pages**

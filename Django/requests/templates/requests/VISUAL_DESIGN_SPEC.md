# Rejection Modal - Visual Design Specification

## 🎨 Design Philosophy

The rejection modal follows the **"Professional Tech"** aesthetic of Local Pro Connect, balancing the ruggedness of home services with modern technology platform polish.

## 📐 Layout Structure

```
┌─────────────────────────────────────────────────────┐
│  MODAL HEADER (Gradient Blue Background)            │
│  ┌──────┐  Reject Service Request          [X]     │
│  │ Icon │                                            │
│  └──────┘                                            │
├─────────────────────────────────────────────────────┤
│  MODAL BODY (White Background)                      │
│                                                      │
│  Instructions text...                               │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  ○ Distance                              ✓  │   │
│  │     Location is too far from service area   │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  ◉ Price [SELECTED]                      ✓  │   │ <- Selected State
│  │     Budget doesn't match my pricing         │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  ○ Time                                  ✓  │   │
│  │     Schedule doesn't work for me            │   │
│  └─────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────┐   │
│  │  ○ Other                                 ✓  │   │
│  │     Different reason not listed above       │   │
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  ℹ You selected: Price                      │   │ <- Dynamic Display
│  └─────────────────────────────────────────────┘   │
│                                                      │
│  Additional Details (Optional)                      │
│  ┌─────────────────────────────────────────────┐   │
│  │  Textarea for description...                │   │
│  │                                              │   │
│  └─────────────────────────────────────────────┘   │
│  0/500 characters                                   │
│                                                      │
│              [Cancel]  [Submit Rejection]           │
└─────────────────────────────────────────────────────┘
```

## 🎨 Color Usage Map

### Header Section
```css
Background: linear-gradient(135deg, #0052CC → #003d99)
Title Text: #FFFFFF (White)
Icon Background: rgba(231, 76, 60, 0.15) with red icon
Close Button: rgba(255, 255, 255, 0.15)
Decorative Circle: rgba(23, 184, 144, 0.1)
```

### Body Section
```css
Background: #FFFFFF (White)
Description Text: #666666 (Medium Gray)
Section Labels: #2C3E50 (Dark Text)
Icon Accent: #0052CC (Primary Blue)
```

### Reason Cards (Default State)
```css
Background: #FFFFFF (White)
Border: 2px solid #E8E8E8 (Border Gray)
Icon Background: #F5F5F5 (Light Gray)
Icon Color: #666666 (Medium Gray)
Title: #2C3E50 (Dark Text)
Subtitle: #666666 (Medium Gray)
Checkmark: Opacity 0 (hidden)
```

### Reason Cards (Hover State)
```css
Border: 2px solid #0052CC (Primary Blue)
Background: #E8F0FE (Light Blue)
Transform: translateY(-2px)
Shadow: 0 2px 8px rgba(0, 0, 0, 0.08)
```

### Reason Cards (Selected State)
```css
Border: 2px solid #17B890 (Accent Green)
Background: #E8F5F0 (Light Green)
Icon Background: #17B890 (Accent Green)
Icon Color: #FFFFFF (White)
Checkmark: Opacity 1, #17B890 (Accent Green)
Shadow: 0 4px 12px rgba(23, 184, 144, 0.3)
Animation: checkmarkPop (scale effect)
```

### Selected Reason Display
```css
Background: linear-gradient(135deg, #E8F0FE → #E8F5F0)
Border-left: 4px solid #17B890 (Accent Green)
Icon: #0052CC (Primary Blue)
Text: #2C3E50 (Dark Text)
Emphasis: #0052CC (Primary Blue)
```

### Description Textarea (Default)
```css
Border: 2px solid #E8E8E8 (Border Gray)
Background: #FFFFFF (White)
Text: #2C3E50 (Dark Text)
Placeholder: #999999 (Light Gray)
```

### Description Textarea (Focus)
```css
Border: 2px solid #0052CC (Primary Blue)
Shadow: 0 0 0 4px rgba(0, 82, 204, 0.1)
```

### Buttons
```css
Cancel Button:
  Background: #FFFFFF (White)
  Border: 2px solid #E8E8E8 (Border Gray)
  Text: #2C3E50 (Dark Text)
  Hover: Background #F5F5F5, Border #666666

Submit Button (Active):
  Background: #e74c3c (Danger Red)
  Text: #FFFFFF (White)
  Shadow: 0 4px 12px rgba(231, 76, 60, 0.3)
  Hover: Background #c0392b, lift 2px

Submit Button (Disabled):
  Background: #E8E8E8 (Border Gray)
  Text: #999999 (Light Gray)
  Opacity: 0.6
  Cursor: not-allowed
```

## 📏 Spacing & Dimensions

### Modal Container
```
Max Width: 650px
Border Radius: 12px
Shadow: 0 8px 32px rgba(0, 0, 0, 0.16)
Max Height: 90vh (with scroll)
```

### Header
```
Padding: 28px 32px
Icon Size: 48x48px (circle)
Title Font: 24px / Bold (700)
Close Button: 40x40px (circle)
```

### Body
```
Padding: 32px
Description Font: 15px / Regular
Section Labels: 15px / Semi-bold (600)
```

### Reason Cards
```
Padding: 18px 20px
Gap: 12px between cards
Border Radius: 10px
Icon: 48x48px (8px radius)
Title: 16px / Semi-bold (600)
Subtitle: 14px / Regular
Checkmark: 28x28px
```

### Description Textarea
```
Padding: 14px 16px
Border Radius: 10px
Min Height: 4 rows
Font Size: 15px
Line Height: 1.6
Max Length: 500 characters
```

### Buttons
```
Padding: 14px 28px
Border Radius: 10px
Font Size: 15px / Semi-bold (600)
Gap: 12px between buttons
Icon Size: 14px
```

## 🌊 Animation Specifications

### Modal Entrance
```css
Animation: slideUp 0.4s cubic-bezier(0.4, 0, 0.2, 1)
From: opacity 0, translateY(40px), scale(0.95)
To: opacity 1, translateY(0), scale(1)
```

### Overlay Fade
```css
Animation: fadeIn 0.3s ease-out
From: opacity 0
To: opacity 1
```

### Close Button Rotation
```css
Transition: transform 0.3s ease
Hover: rotate(90deg)
```

### Reason Card Selection
```css
Transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1)
Hover: translateY(-2px)
```

### Checkmark Pop
```css
Animation: checkmarkPop 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55)
0%: scale(0)
50%: scale(1.2)
100%: scale(1)
```

### Selected Reason Display
```css
Animation: slideDown 0.4s ease-out
From: opacity 0, translateY(-10px)
To: opacity 1, translateY(0)
```

### Description Section
```css
Animation: fadeInUp 0.4s ease-out
From: opacity 0, translateY(10px)
To: opacity 1, translateY(0)
```

### Error Message
```css
Animation: shakeError 0.4s ease
0%, 100%: translateX(0)
25%: translateX(-8px)
75%: translateX(8px)
```

## 📱 Responsive Breakpoints

### Desktop (> 768px)
- Modal: 650px width, centered
- Buttons: Side by side
- Spacing: Full (32px)
- Font sizes: Full scale

### Tablet (481px - 768px)
- Modal: 95% width
- Padding reduced: 24px
- Title: 20px (from 24px)
- Icons: 42px (from 48px)
- Buttons: Stacked (full width)

### Mobile (≤ 480px)
- Modal: Full width minus 20px
- Padding: 20px
- Title: 18px
- Compact spacing
- Touch-optimized targets (minimum 44px)

## 🎯 Interactive States

### Default State
- Cards: Gray border, white background
- Submit button: Disabled, gray
- Description: Hidden
- Selected display: Hidden

### Reason Selected State
- Selected card: Green border, green background
- Other cards: Default state
- Submit button: Enabled, red
- Description: Visible with animation
- Selected display: Visible with animation

### Focus State
- Blue outline (3px solid #0052CC)
- Offset: 2px
- Applies to: All interactive elements

### Hover State
- Reason cards: Blue border, blue background, lift
- Buttons: Darker color, lift
- Close button: Brighter, rotate

### Loading State (Submit)
- Button text: "Submitting..."
- Icon: Spinner animation
- Button: Disabled

## 🔍 Accessibility Features

### Color Contrast Ratios
```
Text on White: 4.5:1 minimum (WCAG AA)
White on Blue: 4.5:1 minimum
Button text: 4.5:1 minimum
Icon visibility: High contrast ensured
```

### Touch Targets
```
Minimum size: 44x44px (iOS/Android guidelines)
Reason cards: Full card clickable
Buttons: Proper spacing (12px gap)
Radio buttons: Hidden but accessible
```

### Keyboard Navigation
```
Tab order: Natural flow top to bottom
Radio selection: Arrow keys work
Submit: Enter key (with validation)
Close: Escape key (with confirmation)
Focus visible: Clear blue outline
```

### Screen Reader Support
```
All form elements: Proper labels
Required fields: Marked with aria-required
Dynamic content: Announced on change
Button states: Communicated clearly
Icons: Decorative (aria-hidden where needed)
```

## 🎨 Typography Scale

### Font Family
```
Primary: 'Inter', sans-serif
Fallback: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial
```

### Font Weights
```
Regular: 400 (body text, descriptions)
Medium: 500 (character count, emphasis)
Semi-bold: 600 (labels, titles, buttons)
Bold: 700 (modal header, important text)
```

### Font Sizes
```
Modal Title: 24px (desktop), 18px (mobile)
Section Labels: 15px
Body Text: 15px
Reason Title: 16px
Reason Subtitle: 14px
Button Text: 15px
Character Count: 13px
```

### Line Heights
```
Headings: 1.2
Body Text: 1.6
Compact Text: 1.4
```

## 🌈 Shadow System

### Elevation Levels
```
Level 1 (Cards): 0 2px 8px rgba(0, 0, 0, 0.08)
Level 2 (Hover): 0 4px 16px rgba(0, 0, 0, 0.12)
Level 3 (Modal): 0 8px 32px rgba(0, 0, 0, 0.16)
Special (Green): 0 4px 12px rgba(23, 184, 144, 0.3)
Special (Red): 0 4px 12px rgba(231, 76, 60, 0.3)
Special (Blue Focus): 0 0 0 4px rgba(0, 82, 204, 0.1)
```

## 🔲 Border Radius System

```
Small: 8px (icons, small elements)
Medium: 10px (cards, inputs, buttons)
Large: 12px (modal container)
Circle: 50% (icon wrappers, close button)
```

## ✨ Special Effects

### Backdrop Blur
```css
backdrop-filter: blur(4px)
Applied to: Modal overlay
Fallback: rgba background
```

### Gradient Overlays
```css
Header: linear-gradient(135deg, #0052CC → #003d99)
Selected Display: linear-gradient(135deg, #E8F0FE → #E8F5F0)
```

### Decorative Elements
```css
Header circle: 300px diameter, 10% green opacity, positioned top-right
Purpose: Visual interest without distraction
```

## 🎭 State Transitions

All transitions use: `cubic-bezier(0.4, 0, 0.2, 1)` (Material Design standard)
Duration: 0.3s for most interactions, 0.4s for entrances

This creates smooth, natural-feeling animations that enhance the professional feel.

---

**Design System Version**: 1.0
**Last Updated**: 2025
**Designer**: Senior UI Visual Designer, Local Pro Connect
**Aesthetic**: Professional Tech with Service Industry Trust

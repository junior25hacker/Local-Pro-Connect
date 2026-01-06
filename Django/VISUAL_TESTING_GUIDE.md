# Visual Testing Guide

**Detailed visual descriptions and screenshot verification checklist**

---

## 📸 Screenshot Descriptions

### Screen 1: Login Page

**URL:** `http://localhost:8000/accounts/login/`

**Visual Elements:**
```
┌─────────────────────────────────────────────────┐
│         Local Pro Connect Logo                  │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │  Welcome Back                           │   │
│  │  Sign in to your account                │   │
│  ├─────────────────────────────────────────┤   │
│  │ Username/Email:                         │   │
│  │ [_____________________]                 │   │
│  │ Password:                               │   │
│  │ [_____________________] [👁 Show]      │   │
│  │ [☑] Remember me                         │   │
│  ├─────────────────────────────────────────┤   │
│  │ [  Sign In  ]                           │   │
│  │ Forgot password? | Create account       │   │
│  └─────────────────────────────────────────┘   │
│                                                 │
└─────────────────────────────────────────────────┘
```

**Verification Checklist:**
- [ ] Logo visible at top
- [ ] Title "Welcome Back" displays
- [ ] Username field visible and clickable
- [ ] Password field with show/hide toggle
- [ ] Remember me checkbox
- [ ] Sign In button is prominent (blue)
- [ ] Links to forgot password and create account
- [ ] Form is responsive on mobile
- [ ] Error messages appear in red on invalid login

**Test Actions:**
1. Leave fields empty, click Sign In → Error: "This field is required"
2. Enter `john_miller` / `test123` → Redirects to /requests/list/
3. Check "Remember me" → Login persists after browser restart

---

### Screen 2: Request List - List View

**URL:** `http://localhost:8000/requests/list/`

**Visual Layout:**

```
╔═══════════════════════════════════════════════════════════════╗
║ Local Pro Connect                        [Logout] [Profile]   ║
╚═══════════════════════════════════════════════════════════════╝

╔═══════════════════════════════════════════════════════════════╗
║                   📋 My Service Requests                     ║
║     Track your service requests and provider responses       ║
║                                                               ║
║  📊 Total Requests: 10  |  👤 Customer View                 ║
╚═══════════════════════════════════════════════════════════════╝

┌─── View Toggle ──────────────────────────┐  ┌────────────────┐
│ [✓ List View] [ Map View]                │  │ [🔧 Advanced   │
│                                          │  │     Filters]   │
└──────────────────────────────────────────┘  └────────────────┘

┌─── Advanced Filters (Collapsed) ─────────────────────────────┐
│ [🔧 Filters  3] [Clear All ✕]                              │
├──────────────────────────────────────────────────────────────┤
│ Distance Range                   Service Type               │
│ [━━━━━━━━━━━━━━] 100 miles       [☑] Plumbing             │
│                 "All Distances"   [☐] Electrical            │
│                                   [☐] Carpentry             │
│ Date Range                        [☐] Cleaning              │
│ [Today] [Week] [Month] [✓ All]   [☑] HVAC                 │
│ From: [________]  To: [________]  [☐] Painting             │
│                                   [☐] Landscaping           │
│ Status                            [☐] Roofing               │
│ (●) All (◯) Pending (◯) Accept.. │                         │
└──────────────────────────────────────────────────────────────┘

  [📅 Newest First ✓]  [📏 Nearest First]  [📅 Oldest First]

  Results: 10 matching requests found

  ┌──────────────────────┐  ┌──────────────────────┐
  │ Request #1           │  │ Request #2           │
  │ 🕐 Pending           │  │ ✓ Accepted           │
  ├──────────────────────┤  ├──────────────────────┤
  │ Provider             │  │ Provider             │
  │ [T] Tom's Electric   │  │ [M] Maria's Cleaning │
  │     Tom's Electric   │  │     Maria Gonzalez   │
  │                      │  │                      │
  │ Description          │  │ Description          │
  │ Install new light... │  │ Deep clean apartm... │
  │                      │  │ ⚡ URGENT            │
  │ Date: Jan 15, 2024   │  │ Date: Jan 14, 2024   │
  │ Budget: $100-250     │  │ Budget: $50-100      │
  │                      │  │                      │
  │ 📍 Distance          │  │ 📍 Distance          │
  │    2.5 miles         │  │    5.2 miles         │
  │ 🏠 Your Location     │  │ 🏠 Your Location     │
  │    123 Main St...    │  │    456 Park Ave...   │
  │ 🏢 Provider Loc...   │  │ 🏢 Provider Loc...   │
  │    456 Broadway...   │  │    789 5th Ave...    │
  │                      │  │                      │
  │ [View Details →]     │  │ [View Details →]     │
  └──────────────────────┘  └──────────────────────┘
```

**Header Section Verification:**
- [ ] Page title: "📋 My Service Requests" visible
- [ ] Subtitle explains purpose
- [ ] Total requests count shows
- [ ] View type badge shows (Customer View or Provider View)

**View Toggle Verification:**
- [ ] "List View" button is active (highlighted)
- [ ] "Map View" button is inactive
- [ ] Buttons are side-by-side
- [ ] "Advanced Filters" button visible

**Filter Panel Verification:**
- [ ] Panel expands/collapses with toggle
- [ ] Distance slider ranges 5-100 miles
- [ ] Service type checkboxes list all 8 types
- [ ] Date quick-buttons (Today, Week, Month, All Time)
- [ ] Custom date inputs available
- [ ] Status radio buttons (All, Pending, Accepted, Declined)
- [ ] "Clear All" button visible
- [ ] Active filter count badge shows when filters applied

**Sort Controls Verification:**
- [ ] "Newest First" button (default active)
- [ ] "Nearest First" button
- [ ] "Oldest First" button
- [ ] Active button has different styling
- [ ] All buttons clickable

**Results Summary Verification:**
- [ ] Shows number of matching requests
- [ ] Text: "matching requests found"
- [ ] Updates when filters applied

**Request Card Verification (each card):**
- [ ] Card ID displays (#1, #2, etc.)
- [ ] Status badge visible with icon:
  - Pending: 🕐 orange/yellow background
  - Accepted: ✓ green background
  - Declined: ✗ red background
- [ ] Urgent badge displays when applicable (⚡ icon)
- [ ] Provider/Customer section:
  - Avatar with first letter (colored background)
  - Full name
  - Company name (if provider)
- [ ] Description preview (truncated ~20 words)
- [ ] Date submitted shows
- [ ] Budget shows with 💰 icon
- [ ] Distance section:
  - Large distance number
  - "miles" unit next to number
  - Two address items:
    - 🏠 icon + "Your Location" label + address
    - 🏢 icon + "Provider Location" label + address
- [ ] "View Details →" button (blue, clickable)
- [ ] Card has slight shadow/border styling

**Responsive Mobile Verification:**
- [ ] Resize to 375px width
- [ ] Cards stack vertically (1 column)
- [ ] Text remains readable
- [ ] Buttons are touch-friendly (large)
- [ ] Filters collapse into accordion

---

### Screen 3: Request List - Map View

**URL:** `http://localhost:8000/requests/list/` (after clicking Map View)

**Visual Layout:**

```
╔═══════════════════════════════════════════════════════════════╗
║ Local Pro Connect                        [Logout] [Profile]   ║
╚═══════════════════════════════════════════════════════════════╝

┌─── View Toggle ──────────────────────────┐
│ [ List View] [✓ Map View]                │
└──────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│ Leaflet Map (Full Width/Height)                             │
│ ┌────────────────────────────────────────────────────────┐  │
│ │                                                        │  │
│ │        🏙 Zoomable, Pannable Map                       │  │
│ │    🔷 User Location Marker                             │  │
│ │    🔶 Provider Location Marker (different color)      │  │
│ │    🔴 Multi-location clusters (if zoomed out)         │  │
│ │                                                        │  │
│ │  [+][-] Zoom Controls (top-left)                       │  │
│ │  [⌂] Home Button (top-left)                           │  │
│ │  Leaflet © OpenStreetMap contributors                 │  │
│ │                                                        │  │
│ └────────────────────────────────────────────────────────┘  │
│                                                               │
└──────────────────────────────────────────────────────────────┘
```

**Map Verification:**
- [ ] Map displays full screen
- [ ] Markers appear for each request location
- [ ] User locations marked with one color (e.g., blue)
- [ ] Provider locations marked with different color (e.g., purple)
- [ ] Map is interactive (can zoom and pan)
- [ ] Zoom controls visible (+ and - buttons)
- [ ] Home/reset button visible
- [ ] Attribution shows "Leaflet" and "OpenStreetMap"

**Marker Interactions Verification:**
- [ ] Clicking marker shows popup
- [ ] Popup contains:
  - Request ID
  - Provider name
  - Distance
  - User address
  - Provider address
- [ ] Popup has close button (X)
- [ ] Popup repositions when off-screen

**Performance Verification:**
- [ ] Map loads in < 2 seconds
- [ ] Zoom/pan is smooth (no lag)
- [ ] Markers render instantly

---

### Screen 4: Request Detail Page

**URL:** `http://localhost:8000/requests/1/`

**Visual Layout:**

```
╔═══════════════════════════════════════════════════════════════╗
║ Local Pro Connect                        [Logout] [Profile]   ║
╚═══════════════════════════════════════════════════════════════╝

[← Back to List]

╔═══════════════════════════════════════════════════════════════╗
║                    DETAIL VIEW - REQUEST #1                  ║
├───────────────────────────────────────────────────────────────┤
║ Service Request #1              Status: [🕐 Pending]  [⚡ Urg] ║
╚═══════════════════════════════════════════════════════════════╝

Provider Information
─────────────────────
    [T]
    Tom's Electric
    Tom's Electric Company
    Service Type: Electrical
    📧 tom@example.com

📝 Service Description
─────────────────────
Install new light fixtures in living room and kitchen. Need
dimmer switches included. Prefer evening installation between
6-8 PM on weekends.

┌─────────────────┬─────────────────┬─────────────────┐
│ 📅 Requested    │ 💰 Budget       │ 📤 Submitted    │
│ Jan 15, 2024    │ $100-250        │ Jan 14, 2024    │
│ 6:00 PM         │                 │ 3:45 PM         │
└─────────────────┴─────────────────┴─────────────────┘

📍 Distance Between Locations
─────────────────────────────
    2.5 miles
    ✓ Very Close - Excellent Match!

🏠 Your Location               🏢 Provider Location
   123 Main Street, NY 10001      456 Broadway, NY 10001

┌─────────────────────────────────────────────────────────┐
│ Interactive Map                                         │
│ ┌──────────────────────────────────────────────────┐   │
│ │  🏙 Map with two markers and route line         │   │
│ │  🔷 Blue marker: Your location                  │   │
│ │  🔶 Orange marker: Provider location            │   │
│ │  ━━ Line showing connection                      │   │
│ └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘

📷 Attached Photos (2)
─────────────────────
┌──────────────┐ ┌──────────────┐
│              │ │              │
│  Photo 1     │ │  Photo 2     │
│  (Click to   │ │  (Click to   │
│   enlarge)   │ │   enlarge)   │
└──────────────┘ └──────────────┘

[← Back to List]  [+ Create Another Request]
```

**Header Section Verification:**
- [ ] Request ID displays (#1)
- [ ] Status badge with color:
  - Pending: 🕐 orange
  - Accepted: ✓ green
  - Declined: ✗ red
- [ ] Urgent badge displays (⚡ URGENT) when applicable
- [ ] Back button at top, works correctly

**Provider Information Verification:**
- [ ] Avatar with first letter
- [ ] Provider/customer name
- [ ] Company name (if available)
- [ ] Service type displays
- [ ] Email shows if applicable

**Description Section Verification:**
- [ ] 📝 heading visible
- [ ] Full description text displays (not truncated)
- [ ] Text wraps properly
- [ ] Formatting preserved (line breaks, paragraphs)

**Request Details Grid Verification:**
- [ ] Shows in 3-column layout (responsive to 1 column on mobile)
- [ ] **Requested Date & Time** (if set):
  - 📅 Date
  - 🕐 Time
- [ ] **Budget Range**:
  - 💰 Price range label
- [ ] **Submitted On**:
  - Date and time of creation
- [ ] **Accepted On** (only if accepted):
  - Green colored text
  - Date and time
- [ ] **Declined On** (only if declined):
  - Red colored text
  - Date and time

**Decline Information Section (if declined):**
- [ ] Only appears for declined requests
- [ ] Red left border accent
- [ ] Light red background
- [ ] Shows decline reason
- [ ] Shows decline message if provided

**Distance Section Verification:**
- [ ] 📍 heading
- [ ] Large distance number
- [ ] "miles" unit label
- [ ] Distance category displays:
  - < 5 miles: "✓ Very Close - Excellent Match!" (green)
  - 5-15 miles: "✓ Nearby - Good Match" (green)
  - 15-30 miles: "⚠ Moderate Distance" (yellow)
  - > 30 miles: "⚠ Significant Distance" (orange)
- [ ] Two address sections:
  - 🏠 "Your Location" / "Customer Location"
  - 🏢 "Provider Location" / "Your Business Location"
- [ ] Map renders with both markers and route line

**Photos Section (if present):**
- [ ] 📷 heading
- [ ] Photo count shows in title
- [ ] Photos display in grid
- [ ] Clicking photo opens in new tab
- [ ] Photos are square thumbnails

**Action Buttons Verification:**
- [ ] "← Back to List" button visible
- [ ] "Create Another Request" button shows (for users)
- [ ] Both buttons are blue and clickable

---

### Screen 5: Export - CSV File

**File:** `service_requests_2024-01-15.csv`

**Visual Content:**

```
Request ID,Service Type,User,Provider,Status,Date,Price Range,Urgent
1,electrical,John Miller,Tom's Electric,pending,2024-01-15,100-250,false
2,cleaning,Sarah Johnson,Maria's Cleaning,accepted,2024-01-14,50-100,true
3,hvac,Mike Chen,Dave's HVAC,declined,2024-01-13,250-500,false
4,carpentry,Diana Garcia,Alex's Carpentry,pending,2024-01-12,500+,false
5,plumbing,John Miller,Joe's Plumbing,accepted,2024-01-11,50-100,false
6,electrical,Sarah Johnson,Tom's Electric,pending,2024-01-10,100-250,true
7,cleaning,Mike Chen,Maria's Cleaning,pending,2024-01-09,50-100,false
8,hvac,Diana Garcia,Dave's HVAC,accepted,2024-01-08,250-500,false
9,carpentry,John Miller,Alex's Carpentry,declined,2024-01-07,100-250,false
10,plumbing,Sarah Johnson,Joe's Plumbing,pending,2024-01-06,50-100,true
```

**Verification When Opened in Excel:**

```
┌──────────┬──────────────┬─────────────┬─────────────────┐
│ Request  │ Service Type │ User        │ Provider        │
├──────────┼──────────────┼─────────────┼─────────────────┤
│ 1        │ electrical   │ John Miller │ Tom's Electric  │
│ 2        │ cleaning     │ Sarah John..│ Maria's Clean...│
│ 3        │ hvac         │ Mike Chen   │ Dave's HVAC     │
└──────────┴──────────────┴─────────────┴─────────────────┘

...continues with Status, Date, Price Range, Urgent columns
```

**CSV Verification:**
- [ ] Headers present (Request ID, Service Type, User, Provider, Status, Date, Price Range, Urgent)
- [ ] Data rows contain all request information
- [ ] Comma-separated values
- [ ] No missing data (empty cells for optional fields)
- [ ] Dates in consistent format (YYYY-MM-DD)
- [ ] Status shows lowercase (pending, accepted, declined)
- [ ] Urgent shows true/false
- [ ] Opens correctly in Excel, Google Sheets, LibreOffice
- [ ] File size < 10KB

**Filtered CSV Verification:**
Example: `/requests/export/csv/?status=pending&service_type=electrical`
- [ ] Only 2 rows (pending electrical requests)
- [ ] Rows are for request IDs 1 and 6
- [ ] Status column shows only "pending"
- [ ] Service Type column shows only "electrical"

---

### Screen 6: Export - PDF File

**File:** `service_requests_2024-01-15.pdf`

**Visual Layout:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                  Service Requests Export
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Generated on January 15, 2024 at 3:45:22 PM

┌─────────┬──────────────┬─────────────┬─────────────────┬─────────┐
│ Request │ Service Type │ User        │ Provider        │ Status  │
├─────────┼──────────────┼─────────────┼─────────────────┼─────────┤
│ 1       │ electrical   │ John Miller │ Tom's Electric  │ pending │
├─────────┼──────────────┼─────────────┼─────────────────┼─────────┤
│ 2       │ cleaning     │ Sarah John..│ Maria's Clean...│accepted │
├─────────┼──────────────┼─────────────┼─────────────────┼─────────┤
│ 3       │ hvac         │ Mike Chen   │ Dave's HVAC     │ declined│
├─────────┼──────────────┼─────────────┼─────────────────┼─────────┤
│ 4       │ carpentry    │ Diana Ga... │ Alex's Carpent..│ pending │
└─────────┴──────────────┴─────────────┴─────────────────┴─────────┘
...continues on next pages...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This report was automatically generated. For more
information, please contact support.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

                        Page 1
```

**PDF Verification:**
- [ ] Title: "Service Requests Export"
- [ ] Timestamp shows generation date/time
- [ ] Table header has distinct color (purple/blue)
- [ ] Table header text is white
- [ ] Data rows have alternating background (beige)
- [ ] All columns visible (Request ID, Service Type, User, Provider, Status, Date, Price Range, Urgent, Description)
- [ ] Borders around cells clear
- [ ] Text is readable (not too small)
- [ ] Multiple pages handled correctly
- [ ] Footer text visible on each page
- [ ] Page number shows
- [ ] Opens in PDF reader without errors
- [ ] Can zoom without distortion
- [ ] Can be printed correctly

**PDF Styling Verification:**
- [ ] Header row background is purple (#667eea)
- [ ] Header text is white
- [ ] Data rows background is light beige
- [ ] Border lines are gray
- [ ] Text alignment is centered
- [ ] Column widths are proportional

---

## 🔄 Interactive Flow Verification

### Test Flow 1: Complete User Journey

**Step 1: Login**
- [ ] Form appears
- [ ] Enter `john_miller` / `test123`
- [ ] Click Sign In
- [ ] Redirects to /requests/list/

**Step 2: View List**
- [ ] 10 requests display
- [ ] Header shows "My Service Requests"
- [ ] All cards have proper styling

**Step 3: Apply Filters**
- [ ] Open Advanced Filters
- [ ] Set Distance to 30 miles
- [ ] Select "Electrical" service type
- [ ] Set Date to "This Month"
- [ ] Results update immediately
- [ ] Results count changes

**Step 4: View on Map**
- [ ] Click "Map View" button
- [ ] Map appears with filtered markers
- [ ] Click on marker
- [ ] Popup shows request info

**Step 5: Switch Back to List**
- [ ] Click "List View" button
- [ ] List reappears with same filters applied
- [ ] Filters still active

**Step 6: View Details**
- [ ] Click "View Details" on first card
- [ ] Detail page loads
- [ ] All information displays
- [ ] Distance shows
- [ ] Map shows locations

**Step 7: Export Data**
- [ ] Go back to list
- [ ] Apply same filters
- [ ] Export as CSV
- [ ] File downloads
- [ ] Open file, verify filtered data
- [ ] Export as PDF
- [ ] File downloads
- [ ] Opens in PDF reader

**Step 8: Sort Results**
- [ ] Go back to list
- [ ] Clear filters
- [ ] Click "Nearest First"
- [ ] Results reorder by distance
- [ ] Click "Oldest First"
- [ ] Results reorder by date (ascending)

---

### Test Flow 2: Provider Journey

**Step 1: Login as Provider**
- [ ] Login: `tom_electric` / `test123`
- [ ] Redirects to /requests/list/

**Step 2: View Provider Requests**
- [ ] Header says "Your Service Requests"
- [ ] Only requests assigned to tom_electric show
- [ ] "Your Business Location" shows instead of "Provider Location"

**Step 3: View Customer Info**
- [ ] Click request detail
- [ ] "Customer Information" section shows
- [ ] Customer name, email, phone visible
- [ ] Can see distance to customer

**Step 4: Check Map**
- [ ] Map shows provider location (provider's zip code)
- [ ] Map shows customer location
- [ ] Route line connects them

---

## ✅ Visual Testing Checklist

### Colors and Styling
- [ ] Primary blue (#667eea) used for headers
- [ ] Status colors consistent:
  - Orange for pending
  - Green for accepted
  - Red for declined
- [ ] Success messages in green
- [ ] Error messages in red
- [ ] Warning messages in yellow/orange
- [ ] Text hierarchy clear (h1 > h2 > body text)
- [ ] Font sizes readable on all screens
- [ ] Line heights comfortable for reading

### Typography
- [ ] Headings bold and prominent
- [ ] Body text size ~16px
- [ ] Label text size ~14px
- [ ] Labels have consistent font-weight
- [ ] No overlapping text
- [ ] Long text truncates appropriately

### Spacing and Layout
- [ ] Consistent padding around elements
- [ ] Cards have breathing room
- [ ] Gaps between filter controls
- [ ] Table rows evenly spaced
- [ ] No crowded layouts

### Buttons and Controls
- [ ] Buttons have hover effects
- [ ] Buttons have clear labels
- [ ] Active buttons show different styling
- [ ] Disabled buttons appear grayed out
- [ ] Click areas are large enough (mobile-friendly)
- [ ] Focus states visible (accessibility)

### Icons
- [ ] All Font Awesome icons load
- [ ] Icons are properly colored
- [ ] Icons align with text
- [ ] Icon size is consistent

### Responsive Design
- [ ] Mobile (375px): Single column, readable
- [ ] Tablet (768px): 2 columns
- [ ] Desktop (1920px): Multiple columns
- [ ] Touch targets large on mobile
- [ ] No horizontal scrolling on mobile
- [ ] No broken layouts

---

## 🎨 Color Reference

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Primary Blue | Blue | #667eea | Headers, active buttons, links |
| Success Green | Green | #27ae60 | Accepted status, close distance |
| Warning Yellow | Yellow-Gold | #f39c12 | Moderate distance |
| Error Red | Red | #e74c3c | Declined status, far distance |
| Light Gray | Light Gray | #ecf0f1 | Backgrounds, borders |
| Dark Gray | Dark Gray | #34495e | Text, headings |
| White | White | #ffffff | Cards, backgrounds |
| Beige | Beige | #faf1e6 | Alternative backgrounds |

---

## 📋 Final Verification Checklist

### Functionality
- [ ] All features work as described
- [ ] No 404 errors
- [ ] No 500 errors
- [ ] Forms submit correctly
- [ ] Redirects work properly
- [ ] Links are not broken

### Performance
- [ ] Pages load in < 1 second
- [ ] Filters respond in < 200ms
- [ ] Maps render smoothly
- [ ] Exports complete in < 5 seconds

### Accessibility
- [ ] Tab navigation works
- [ ] Forms have proper labels
- [ ] Alt text on images
- [ ] Color not sole differentiator
- [ ] Text contrast sufficient

### Mobile
- [ ] Responsive at all breakpoints
- [ ] Touch-friendly buttons
- [ ] No horizontal scroll
- [ ] Mobile layout tested

### Security
- [ ] Cannot view other user's requests
- [ ] Cannot access admin without permission
- [ ] Export respects user permissions
- [ ] Form data validated

### Browsers
- [ ] Chrome: ✓ / ✗ / ⚠
- [ ] Firefox: ✓ / ✗ / ⚠
- [ ] Safari: ✓ / ✗ / ⚠
- [ ] Edge: ✓ / ✗ / ⚠

---

**Ready to start visual testing? Print this guide and reference Screen 1 to begin! ✨**

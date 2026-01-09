# Quick Test Reference Card

**Print this page for quick reference while testing!**

---

## 🚀 Start Here (3 steps)

### 1️⃣ Start Server
```bash
cd Django
python manage.py runserver
```

### 2️⃣ Create Test Data
```bash
cd Django
python manage.py create_test_data
```

### 3️⃣ Login & Test
```
URL: http://localhost:8000/accounts/login/
Username: john_miller
Password: test123
```

---

## 🔗 Key URLs to Test

| Feature | URL |
|---------|-----|
| List View | `http://localhost:8000/requests/list/` |
| Detail View | `http://localhost:8000/requests/1/` |
| CSV Export | `http://localhost:8000/requests/export/csv/` |
| PDF Export | `http://localhost:8000/requests/export/pdf/` |
| Demo | `http://localhost:8000/static/demo_maps_filters.html` |
| Admin | `http://localhost:8000/admin/` |

---

## 👥 Test Credentials

**All passwords: `test123`**

### Users
- `john_miller` - NYC, Zip 10001
- `sarah_johnson` - NYC, Zip 10002
- `mike_chen` - Brooklyn, Zip 11201
- `diana_garcia` - Queens, Zip 11354

### Providers
- `tom_electric` - Electrical
- `maria_cleaning` - Cleaning
- `dave_hvac` - HVAC
- `alex_carpentry` - Carpentry
- `plumber_joe` - Plumbing

### Admin
- `admin` - Password: `admin123`

---

## ✅ 5-Minute Test Checklist

- [ ] Server running at localhost:8000
- [ ] Can login with john_miller
- [ ] Request list shows 10 requests
- [ ] Distance displays on cards
- [ ] Can toggle to map view
- [ ] Markers appear on map
- [ ] Can click "View Details"
- [ ] Distance shows on detail page
- [ ] CSV export downloads
- [ ] PDF export downloads

---

## 🔧 Feature Quick Tests

### Distance Display
```
✓ Check cards show miles (e.g., "2.5 miles")
✓ Check color coding (green=close, yellow=moderate, orange=far)
✓ Check distance categories (Very Close, Nearby, Moderate, Significant)
```

### Filters
```
✓ Distance slider 5-100 miles
✓ Service types (Plumbing, Electrical, etc.)
✓ Date range (Today, Week, Month, All Time)
✓ Status (All, Pending, Accepted, Declined)
```

### Sorting
```
✓ Newest First (date descending)
✓ Nearest First (distance ascending)
✓ Oldest First (date ascending)
```

### Map View
```
✓ Toggle to map appears
✓ Leaflet map loads
✓ Markers show locations
✓ Clicking markers shows popups
✓ Zoom/pan controls work
```

### Exports
```
✓ CSV downloads with headers and data
✓ PDF downloads and opens
✓ Filters apply to exports
✓ Filenames include date
```

---

## 🐛 Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| No requests show | Run `python manage.py create_test_data` |
| "Distance unavailable" | Check user has zip_code in profile |
| Map not showing | Press F12, check console for errors |
| Static files missing | Run `python manage.py collectstatic --clear --noinput` |
| Export not working | Install: `pip install weasyprint` or `pip install reportlab` |
| Filters slow | Clear cache: Ctrl+Shift+R |

---

## 📊 Performance Targets

| Action | Target Time |
|--------|-------------|
| List page load | < 500ms |
| Detail page load | < 300ms |
| Map toggle | < 200ms |
| CSV export | < 1 sec |
| PDF export | < 2 sec |
| Filter update | < 100ms |

---

## 🎯 Test Scenarios (Quick)

### Scenario A: User View (5 min)
```
1. Login: john_miller
2. View list → Should see their requests
3. Click detail → Should load detail page
4. Toggle map → Should see map with markers
5. Apply filters → Results should update
```

### Scenario B: Provider View (5 min)
```
1. Login: tom_electric
2. View list → Should see header "Your Service Requests"
3. Click detail → Should see customer info, not provider info
4. Check distance → Should show distance to customer
```

### Scenario C: Export Test (3 min)
```
1. Login: any user
2. Apply filters: Status=Pending, Service=Plumbing
3. Export CSV → File should download
4. Export PDF → File should download
5. Check files → Should contain only filtered data
```

### Scenario D: Map Demo (3 min)
```
1. Open: http://localhost:8000/static/demo_maps_filters.html
2. View map → Should see markers
3. Click markers → Popups should appear
4. Use filters → Map should update
5. Responsive test → Resize browser window
```

---

## 🎨 Visual Verification

### Cards Should Show
- [ ] Request ID (#001, #002, etc.)
- [ ] Status badge with icon (pending 🕐, accepted ✓, declined ✗)
- [ ] Urgent badge (⚡ when applicable)
- [ ] Provider/customer name
- [ ] Description preview
- [ ] Date submitted
- [ ] Budget (💰 icon)
- [ ] Distance (📍 icon + miles)
- [ ] Two addresses (🏠 and 🏢 icons)

### Detail Page Should Show
- [ ] Request ID and status
- [ ] Urgent badge (if applicable)
- [ ] Provider/customer info with avatar
- [ ] Full description
- [ ] Requested date/time
- [ ] Budget
- [ ] Submitted date
- [ ] Accepted/declined date (if applicable)
- [ ] Distance display
- [ ] Distance category (Very Close, Nearby, etc.)
- [ ] Interactive map with markers
- [ ] Two addresses
- [ ] Back button

---

## 📱 Responsive Testing

Test these breakpoints:
- [ ] Desktop (1920px)
- [ ] Laptop (1366px)
- [ ] Tablet (768px)
- [ ] Mobile (375px)

Quick test: Resize browser window, check:
- [ ] Text readable
- [ ] Buttons clickable
- [ ] Map responsive
- [ ] Cards stack properly

---

## 🖥️ Browser Console Tests

Press F12, paste in console:

```javascript
// Check Leaflet loaded
L ? console.log('✓ Leaflet OK') : console.log('✗ Leaflet missing');

// Check request data
console.log('Requests:', requestsMapData?.length || 'Not found');

// Check filters exist
console.log('Filters:', {
  distance: document.getElementById('distance-slider') ? 'OK' : 'Missing',
  serviceType: document.querySelectorAll('.service-type-checkbox').length,
  dateRange: document.getElementById('date-from') ? 'OK' : 'Missing',
  status: document.querySelector('input[name="status-filter"]') ? 'OK' : 'Missing'
});
```

---

## 📝 Test Report Template

```
Test Date: ___________
Tester: ___________
Django Version: 5.2.9
Python Version: 3.11

✓ PASSED / ✗ FAILED / ⚠ PARTIAL

Feature | Status | Notes
---------|--------|-------
Login | _____ | 
List View | _____ | 
Distance Display | _____ | 
Map View | _____ | 
Filters | _____ | 
Sorting | _____ | 
CSV Export | _____ | 
PDF Export | _____ | 
Responsive (Mobile) | _____ | 
Performance | _____ | 

Issues Found:
1. _____________________
2. _____________________
3. _____________________

Overall Status: READY FOR PRODUCTION / NEEDS FIXES
```

---

## 🔍 Database Checks

Access Django shell:
```bash
cd Django
python manage.py shell
```

Quick queries:
```python
# Count data
from requests.models import ServiceRequest
print(f"Total requests: {ServiceRequest.objects.count()}")
print(f"Pending: {ServiceRequest.objects.filter(status='pending').count()}")
print(f"Accepted: {ServiceRequest.objects.filter(status='accepted').count()}")
print(f"Declined: {ServiceRequest.objects.filter(status='declined').count()}")

# Check specific request
req = ServiceRequest.objects.first()
print(f"Request: {req.provider_name} - Status: {req.status}")
print(f"User: {req.user.username} - Provider: {req.provider.username if req.provider else 'None'}")

# Exit shell
exit()
```

---

## 🎬 Demo Mode

**Standalone Demo** (no backend needed):
```
File: Django/static/demo_maps_filters.html
Open: http://localhost:8000/static/demo_maps_filters.html
OR: File > Open in browser directly
```

Features shown:
- ✅ Interactive map
- ✅ Markers and popups
- ✅ Filter controls
- ✅ Sort options
- ✅ Responsive design
- ✅ No database required

---

## ⏱️ Time Estimates

| Task | Time |
|------|------|
| Setup server | 1 min |
| Create test data | 1 min |
| Full feature test | 10 min |
| Performance test | 5 min |
| Responsive test | 5 min |
| Export test | 3 min |
| **TOTAL** | **~30 min** |

---

## 📞 Need Help?

1. **Check logs:**
   ```bash
   tail -f Django/django_runtime.log
   # or
   tail -f Django/server.log
   ```

2. **Check Django admin:**
   `http://localhost:8000/admin/`
   Login: admin / admin123

3. **Review documentation:**
   - `Django/requests/QUICK_START.md`
   - `Django/requests/EXPORT_GUIDE.md`
   - `Django/requests/MAPS_FILTERS_README.md`

4. **Run debug:**
   ```bash
   cd Django
   python manage.py shell
   # Run queries to check data
   ```

---

**✨ Ready to test? Start with Step 1 above! ✨**

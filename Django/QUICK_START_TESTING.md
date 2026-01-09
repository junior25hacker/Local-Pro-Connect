# 🚀 Quick Start Testing Guide - Local Pro Connect

**Server Status:** ✅ Running on http://localhost:8000

---

## 📋 Quick Feature Testing

### 1. 🔐 Authentication & Login
**Test:** User login and session persistence

```
Step 1: Visit http://localhost:8000/accounts/login/
Step 2: Login with any user credentials
Step 3: Refresh page - should stay logged in ✅
Step 4: Close and reopen browser - should still be logged in ✅
```

**Expected:**
- ✅ Login successful
- ✅ Session persists across page reloads
- ✅ User profile indicator appears in top-right navbar

---

### 2. 👤 User Profile Indicator
**Test:** Profile indicator display and dropdown menu

```
Step 1: Login to any account
Step 2: Look at top-right corner of navbar
Step 3: See user's profile picture (40×40px circular)
Step 4: Click on profile picture
Step 5: Watch dropdown menu appear with smooth animation
Step 6: Try keyboard: Tab → Enter (opens), Escape (closes)
```

**Expected Dropdown Items:**
- My Profile
- Edit Profile (for providers)
- Dashboard (for providers)
- Settings
- Logout

**Mobile:** Compact layout, same functionality

---

### 3. 🔎 Find Service - Filtering
**Test:** Professional filtering functionality

```
Step 1: Visit Find Service page (or professionals list)
Step 2: Enter filter criteria:
   - Service Type: Select a service (e.g., "Plumbing")
   - Location: Enter a city (e.g., "New York")
   - Rating: Select minimum rating (e.g., "4.0+")
   - Experience: Select min years (e.g., "5 years")
Step 3: Click Filter/Search
Step 4: See results filtered appropriately ✅
```

**Expected:**
- ✅ 24 providers available
- ✅ Filters work individually and combined
- ✅ Results update in real-time
- ✅ "No results" message if no matches
- ✅ Pagination if many results (20-30 per page)

---

### 4. 💰 Budget Slider
**Test:** Budget slider with dynamic minimum price

```
Step 1: Go to Create Request page
Step 2: Select a service provider
Step 3: See budget slider appear
Step 4: Notice "Minimum: $XXX" label
Step 5: Try to slide below minimum - slider won't go below ✅
Step 6: Slide to desired budget amount
Step 7: See amount update in real-time
Step 8: Submit request - budget value saved ✅
```

**Expected:**
- ✅ Slider enforces provider's minimum price
- ✅ Currency format displayed ($)
- ✅ Real-time value update
- ✅ Works on mobile (touch support)

---

### 5. 📧 Email Notifications
**Test:** Email sending on request events

```
Step 1: Create a new service request as regular user
Step 2: Check provider's email (console in dev mode)
Step 3: Provider accepts/declines request
Step 4: Check user's email for confirmation
```

**Expected:**
- ✅ Email sent to provider on request
- ✅ Email sent to user on accept/decline
- ✅ Professional HTML templates
- ✅ Correct personalization (names, details)

**Dev Mode:** Check Django console or `server_output.log`

---

### 6. 🛡️ Role-Based Access Control
**Test:** Provider vs Regular User access

**As Regular User:**
```
Step 1: Login as regular user
Step 2: Check navbar - see "New Request", NOT "My Requests"
Step 3: Try to visit /requests/my-requests/
Step 4: Get 403 Forbidden ✅
Step 5: Can view provider profiles (read-only) ✅
Step 6: Cannot click "Edit Profile" ✅
```

**As Provider:**
```
Step 1: Login as provider user
Step 2: Check navbar - see "My Requests" link ✅
Step 3: Visit /requests/my-requests/ - access granted ✅
Step 4: See provider dashboard with requests
Step 5: Can edit own profile ✅
Step 6: Cannot edit other provider profiles (403) ✅
```

**Expected:**
- ✅ Correct navigation links for each role
- ✅ 403 errors for unauthorized access
- ✅ Edit buttons only for profile owner
- ✅ Dashboard access only for providers

---

### 7. 🚫 Rejection Modal
**Test:** Request decline functionality

```
Step 1: Login as provider
Step 2: Go to My Requests
Step 3: Find a pending request
Step 4: Click "Decline" button
Step 5: Modal opens with options
Step 6: Select decline reason
Step 7: Add optional message
Step 8: Click "Confirm Decline"
Step 9: See success message ✅
Step 10: Request status updated to "Declined" ✅
Step 11: Email sent to user ✅
```

**Expected:**
- ✅ Modal opens smoothly
- ✅ Reason selection required
- ✅ Status updates in database
- ✅ Email notification sent
- ✅ Request list refreshed

---

### 8. 📱 Responsive Design
**Test:** Mobile and tablet compatibility

```
Desktop (≥992px):
  Step 1: Visit any page on desktop
  Step 2: All features work perfectly ✅
  
Tablet (768-991px):
  Step 1: Resize browser to tablet width
  Step 2: Layout adapts, all features work ✅
  
Mobile (≤576px):
  Step 1: Resize to mobile width (or use DevTools)
  Step 2: Hamburger menu (if applicable)
  Step 3: Profile indicator compact ✅
  Step 4: Buttons large enough to tap (≥44px)
  Step 5: All touch targets work ✅
```

**Expected:**
- ✅ No horizontal scrolling
- ✅ All buttons accessible
- ✅ Text readable
- ✅ Images scale properly
- ✅ Dropdowns work with touch

---

### 9. ♿ Accessibility
**Test:** Keyboard navigation and screen reader support

```
Keyboard Navigation:
  Step 1: Tab through entire page
  Step 2: Focus visible on all interactive elements ✅
  Step 3: Enter key activates buttons
  Step 4: Arrow keys navigate dropdowns
  Step 5: Escape closes modals/dropdowns ✅
  
Screen Reader:
  Step 1: Use screen reader software
  Step 2: All images have alt text ✅
  Step 3: Form labels associated with inputs ✅
  Step 4: ARIA labels on interactive elements ✅
```

**Expected:**
- ✅ WCAG AA compliant
- ✅ All navigation keyboard accessible
- ✅ High contrast (4.5:1 ratio)
- ✅ Screen reader friendly

---

## 🧪 Test Data Available

**24 Seeded Providers:**
- Various service types (plumbing, electrical, carpentry, etc.)
- Multiple locations and states
- Ratings: 3.5-5.0 stars
- Experience: 1-30 years
- All with realistic pricing data

**Sample Query:**
```python
# In Django shell
from accounts.models import ProviderProfile
ProviderProfile.objects.all().count()  # 24
ProviderProfile.objects.values('service_type').distinct()  # All types
```

---

## 📊 Key URLs to Test

| Feature | URL | Method |
|---------|-----|--------|
| Homepage | http://localhost:8000/ | GET |
| Login | http://localhost:8000/accounts/login/ | POST |
| Professionals List | http://localhost:8000/accounts/professionals/ | GET |
| Create Request | http://localhost:8000/requests/create/ | POST |
| My Requests (Provider) | http://localhost:8000/requests/my-requests/ | GET |
| Filter API | http://localhost:8000/api/professionals/filter/ | GET |
| Decline Request | http://localhost:8000/api/requests/{id}/decline/ | POST |

---

## 🐛 Troubleshooting

**Issue:** Profile indicator not showing after login
- **Solution:** Hard refresh (Ctrl+Shift+R) to clear cache
- **Check:** User is actually logged in (check Django session)

**Issue:** Filters not working
- **Solution:** Verify providers exist: `python manage.py shell`
- **Check:** Database seeding completed

**Issue:** Emails not sending
- **Solution:** Check SMTP credentials in .env file
- **Check:** Dev mode shows email in console
- **Check:** `server_output.log` for errors

**Issue:** Mobile layout broken
- **Solution:** Clear browser cache
- **Check:** DevTools mobile view is enabled
- **Check:** Viewport meta tag in base.html

**Issue:** 403 Forbidden on restricted pages
- **Solution:** This is correct behavior ✅
- **Check:** Ensure you're using correct user role
- **Note:** Providers see different pages than regular users

---

## ✅ Quick Verification Checklist

Run through this checklist to verify all features:

- [ ] Login works and persists
- [ ] Profile indicator visible after login
- [ ] Profile dropdown menu functional
- [ ] Navigation links correct for user role
- [ ] Filtering returns correct results
- [ ] Budget slider enforces minimum price
- [ ] Request can be created with budget
- [ ] Provider can accept/decline requests
- [ ] Decline modal works and updates status
- [ ] Emails sent on request events
- [ ] Regular users see read-only profiles
- [ ] Providers can edit own profiles
- [ ] 403 errors for unauthorized access
- [ ] Responsive on mobile/tablet/desktop
- [ ] Keyboard navigation works
- [ ] No JavaScript console errors
- [ ] Database has 24 providers

---

## 📞 Quick Reference

**Server:** http://localhost:8000  
**Admin Panel:** http://localhost:8000/admin/  
**API Base:** http://localhost:8000/api/  

**Stop Server:**
```bash
pkill -f "python manage.py runserver"
```

**Restart Server:**
```bash
cd Django && python manage.py runserver 0.0.0.0:8000 &
```

**Check Logs:**
```bash
tail -f Django/server_output.log
```

---

## 🎯 Success Indicators

When testing is complete, you should see:

✅ All features working as expected  
✅ No console errors  
✅ Responsive on all devices  
✅ Accessible with keyboard  
✅ Professional appearance  
✅ Database properly populated  
✅ Emails sending correctly  

**Result:** Application ready for QA and deployment! 🚀


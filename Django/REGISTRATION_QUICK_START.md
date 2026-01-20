# Provider Registration - Quick Start Guide

## 🚀 Test the New Multi-Step Registration

### Access URL
```
http://localhost:8000/accounts/register/provider/
```

## 📋 What to Test

### Step 1: Account Information
✅ **Try this:**
- Enter email: `testprovider@example.com`
- Leave first/last name (optional)
- Password: Try `short` (should fail - needs 7+ chars)
- Password: Enter `password123` (should work)
- Confirm password: Must match

❌ **Expected validations:**
- Email required
- Valid email format
- Password minimum 7 characters
- Passwords must match
- Cannot proceed until valid

### Step 2: Service Information
✅ **Try this:**
- Leave service type blank and click Next (should fail)
- Select "Plumbing" (should work)
- Select "Other" → text field appears
- Leave "Other" text blank and click Next (should fail)
- Type "Photography" in Other field (should work)

❌ **Expected validations:**
- Service type required
- When "Other" selected, specification required
- Phone and experience are optional

### Step 3: Location Information
✅ **Try this:**
- Leave city blank (should fail)
- Enter "Douala" for city
- Leave region blank (should fail)
- Select "Littoral" for region
- Leave address and postal code blank (optional)

❌ **Expected validations:**
- City required
- Region required
- Address and postal code optional

### Step 4: Profile & Bio
✅ **Try this:**
- Leave bio blank (optional)
- Read the reassurance text
- Click "Complete Registration"

✅ **Expected result:**
- Account created successfully
- Logged in automatically
- Redirected to provider dashboard
- No username was asked (auto-generated from email)

## 🎯 Key Features to Verify

### Visual Elements
- [ ] Progress bar updates as you move through steps
- [ ] Step circles show: pending (gray), active (blue), completed (green)
- [ ] Smooth animations between steps
- [ ] Error messages appear in red below fields
- [ ] Error summary appears at top of step when validation fails
- [ ] "Other" service type field appears/disappears correctly

### Validation Behavior
- [ ] Cannot proceed to next step with errors
- [ ] Errors show immediately when you leave a field (on blur)
- [ ] Errors clear when you start typing
- [ ] Password hint shows "at least 7 characters"
- [ ] All required fields marked with red asterisk (*)
- [ ] Optional fields have helper text

### Navigation
- [ ] "Next" button advances to next step (with validation)
- [ ] "Back" button returns to previous step (no validation)
- [ ] Can navigate back and forth freely
- [ ] Form data preserved when navigating between steps
- [ ] Final step has "Complete Registration" button

### Responsive Design
- [ ] Works on desktop
- [ ] Works on tablet
- [ ] Works on mobile (test by resizing browser)

## 🐛 Common Issues & Solutions

### Issue: Page not loading
**Solution:** Make sure Django server is running:
```bash
cd Django
python manage.py runserver
```

### Issue: Email already exists error
**Solution:** The email is already registered. Try a different email or check the database.

### Issue: Template not found
**Solution:** Verify the view is using the new template:
```python
# In Django/accounts/views.py
return render(request, 'accounts/register_provider_multistep.html', {'form': form})
```

### Issue: JavaScript not working
**Solution:** Check browser console for errors. Make sure simple_base.html has `{% block extra_js %}`.

## 📸 Visual Testing Checklist

### Colors (Should match existing design)
- Primary Blue: #004C99
- Secondary Blue: #007bff
- Success Green: #28a745
- Danger Red: #dc3545
- Background gradient: Blue overlay on image

### Typography
- Headers: Poppins font
- Body: Inter font
- Icons: Font Awesome 6.4.0

### Spacing
- Form fields well-spaced
- Buttons sized appropriately
- Progress indicators visible
- Mobile-friendly layout

## 🔄 Test Different Scenarios

### Scenario 1: Minimal Registration
```
Email: minimal@test.com
Password: password123
Service Type: Plumbing
City: Douala
Region: Littoral
```
✅ Should work with just these fields

### Scenario 2: Full Registration
```
Email: fulltest@test.com
First Name: John
Last Name: Doe
Password: securepass123
Company: John's Plumbing
Service Type: Other → "Photography"
Phone: +237 612345678
Years Experience: 5
City: Yaounde
Region: Centre
Business Address: 123 Main Street
Postal Code: 237
Bio: Professional photographer...
```
✅ Should work with all fields filled

### Scenario 3: Error Handling
```
Step 1: Try to proceed without email
Step 2: Try to proceed without service type
Step 2: Select "Other" without specifying
Step 3: Try to proceed without city/region
```
❌ Each should show appropriate validation errors

## 📊 Expected Behavior Summary

| Field | Required | Validated | Default |
|-------|----------|-----------|---------|
| Email | Yes | Format, Unique | - |
| First Name | No | - | - |
| Last Name | No | - | - |
| Password | Yes | Min 7 chars | - |
| Confirm Password | Yes | Must match | - |
| Username | No (Hidden) | Auto-generated | From email |
| Company Name | No | - | - |
| Service Type | Yes | Must select | - |
| Other Service | Conditional | Required if "Other" | - |
| Phone | No | Basic format | - |
| Years Experience | No | Non-negative | 0 |
| City | Yes | - | - |
| Region | Yes | Must select | - |
| Business Address | No | - | - |
| Postal Code | No | - | - |
| Bio | No | - | - |

## ✅ Success Criteria

Registration is successful when:
1. ✅ All required fields are filled correctly
2. ✅ Password is 7+ characters and matches confirmation
3. ✅ Service type is selected (and specified if "Other")
4. ✅ City and region are provided
5. ✅ Email is unique (not already registered)
6. ✅ User is created and logged in automatically
7. ✅ Redirected to provider dashboard

---

**Need help?** Check `PROVIDER_REGISTRATION_IMPROVEMENTS.md` for detailed documentation.

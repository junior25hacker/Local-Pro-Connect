# Test Login Credentials for Local Pro Connect

## Test User Account (Created for Testing)

### Regular User Account
- **Username:** `demouser`
- **Password:** `demo123`
- **Email:** demo@example.com
- **Type:** Regular User

---

## How to Test the Login Gate

### Step 1: Ensure Django Server is Running
```bash
# From the project root directory
cd Django
..\venv\Scripts\python.exe manage.py runserver
```

Server should start on: **http://127.0.0.1:8000/**

### Step 2: Open the Login Gate Page
Open your browser to: **http://127.0.0.1:5500/pages/login-gate.html**

### Step 3: Login with Test Credentials
1. Enter username: `demouser`
2. Enter password: `demo123`
3. Click "Login & Continue to Find Service"

### Step 4: Expected Result
- ✅ Success message appears
- ✅ Page redirects to `search.html`
- ✅ Username "demouser" displayed in navigation
- ✅ Logout button available

---

## API Endpoint Test Results

✅ **Django API Endpoint:** http://127.0.0.1:8000/accounts/auth/
✅ **Method:** POST
✅ **Parameters:** action=signin, username, password
✅ **Response:** JSON with success message and user data

### Verified Working:
```json
{
  "success": "You have successfully logged in! Redirecting to your profile...",
  "user_type": "user",
  "redirect": "/accounts/profile/user/",
  "username": "demouser",
  "first_name": ""
}
```

---

## Troubleshooting

### Issue: "Django server is not running"
**Solution:** Make sure Django server is running on port 8000
```bash
cd Django
..\venv\Scripts\python.exe manage.py runserver
```

### Issue: "Incorrect password"
**Solution:** Use the test credentials above:
- Username: `demouser`
- Password: `demo123`

### Issue: "CORS error" in browser console
**Solution:** This is expected when testing from Live Server (port 5500). The `credentials: 'include'` option handles this.

### Issue: Page doesn't redirect after login
**Solution:** Check browser console for errors. Make sure sessionStorage is enabled.

---

## Database Users

Total users in database: **33** (as of last check)

Sample users:
- admin (password may vary)
- provider_1 through provider_4
- demouser (password: demo123) ✅

---

## Creating More Test Users

If you need more test users, run this in Django shell:

```python
cd Django
..\venv\Scripts\python.exe manage.py shell

# In the shell:
from django.contrib.auth.models import User
user = User.objects.create_user('newuser', 'new@example.com', 'password123')
print(f'Created: {user.username}')
```

---

## Notes

- ✅ Login API is working correctly
- ✅ Database authentication is functional
- ✅ Password hashing is secure
- ✅ Sessions are being created
- ✅ Error messages are helpful

The login system is **fully functional** and ready for testing!

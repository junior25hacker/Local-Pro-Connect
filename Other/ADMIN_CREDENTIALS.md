# Local Pro Connect - Admin Access Credentials

## Date Created: December 26, 2025

### Admin Panel Access
- **URL:** http://127.0.0.1:8000/admin/
- **Server Status:** Running and operational

---

## Superuser Accounts

### Account 1: Perez
- **Username:** `perez`
- **Email:** `Perez@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

### Account 2: Hueala
- **Username:** `hueala`
- **Email:** `Hueala@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

### Account 3: Oliver
- **Username:** `oliver`
- **Email:** `Oliver@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

### Account 4: Michelle
- **Username:** `michelle`
- **Email:** `Michelle@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

### Account 5: Melaine
- **Username:** `melaine`
- **Email:** `Melaine@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

### Account 6: Sandra
- **Username:** `sandra`
- **Email:** `Sandra@localpro.dev`
- **Password:** `LocalPro2025!`
- **Role:** Superuser (Full Admin Access)

---

## Quick Login Guide

1. Open your browser and navigate to: **http://127.0.0.1:8000/admin/**
2. Enter your username (e.g., `perez`)
3. Enter your password: `LocalPro2025!`
4. Click **Sign In**

You'll have full access to:
- User management
- Provider profiles
- Database administration
- Site configuration

---

## Important Security Notes

⚠️ **BEFORE PRODUCTION:**
1. Change all passwords to unique, strong passwords
2. Use the following pattern for new passwords:
   - Minimum 12 characters
   - Include uppercase and lowercase letters
   - Include numbers and special characters
   - Example: `P@ssw0rd!Secure2025`

3. Consider implementing:
   - Two-factor authentication (2FA)
   - Email verification
   - Password expiration policies
   - Admin activity logging

---

## Admin Panel Features Available

Once logged in, you can manage:
- **Users:** View, edit, delete user accounts
- **Providers:** Manage service provider profiles
- **Authentication & Authorization:** Control user permissions
- **Site Administration:** Manage Django site settings

---

## Troubleshooting

### Can't login?
- Verify the Django server is running: `python manage.py runserver 0.0.0.0:8000`
- Check that you're using the correct username (not email)
- Ensure caps lock is off
- Try clearing browser cache and cookies

### Forgot password?
- Contact the system administrator
- Or reset via Django shell: `python manage.py changepassword [username]`

### Port 8000 already in use?
- Use an alternative port: `python manage.py runserver 0.0.0.0:8001`
- Update the URL to http://127.0.0.1:8001/admin/

---

## Support

For technical support or access issues, refer to:
- SETUP_GUIDE.md - Setup instructions
- SETUP.md - Detailed setup documentation
- CHANGES_MADE.md - Recent changes and fixes

---

**Last Updated:** December 26, 2025  
**Status:** ✅ All accounts active and verified

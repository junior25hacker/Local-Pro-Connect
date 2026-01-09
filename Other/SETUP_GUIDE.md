# Local Pro Connect - Developer Setup Guide

## Quick Start (Local Machine)

### 1. Open Terminal and Navigate to Django Folder
```bash
cd Django
```

### 2. Activate Virtual Environment
```bash
source .venv/bin/activate
```

### 3. Apply Database Migrations
```bash
python manage.py migrate
```

### 4. Start Django Development Server
```bash
python manage.py runserver
```

You should see:
```
Starting development server at http://127.0.0.1:8000/
```

### 5. Open Sign-Up Pages in Browser
- **Sign up as User:** http://127.0.0.1:8000/accounts/signup/user/
- **Become a Provider:** http://127.0.0.1:8000/accounts/signup/provider/

---

## For Team Members on the Same Network

### Setup on Your Machine
1. Follow steps 1-3 above (navigate, activate venv, migrate)

### 2. Start Server Accessible to Network
```bash
python manage.py runserver 0.0.0.0:8000
```

### 3. Share Your IP Address
Find your machine IP:
```bash
hostname -I
# Example output: 192.168.1.100
```

Share this IP with teammates (e.g., `192.168.1.100`)

### 4. Team Members Access Pages
They can now visit:
- **Sign up as User:** http://192.168.1.100:8000/accounts/signup/user/
- **Become a Provider:** http://192.168.1.100:8000/accounts/signup/provider/

---

## Troubleshooting

### "Cannot GET /accounts/signup/user"
- ✅ **Solution:** Make sure Django server is running (`python manage.py runserver`)
- Check that no Python errors appear in the server terminal

### "Connection refused" when accessing from another machine
- ✅ **Solution:** Start server with `python manage.py runserver 0.0.0.0:8000` (not 127.0.0.1)
- Check firewall allows port 8000: `sudo ufw allow 8000` (Linux)

### "Module not found" or "ModuleNotFoundError"
- ✅ **Solution:** Make sure virtual environment is activated: `source .venv/bin/activate`

### Database Errors
- ✅ **Solution:** Run migrations: `python manage.py migrate`

---

## Key Folder Structure
```
Django/
├── manage.py                 # Django management script
├── .venv/                    # Python virtual environment
├── locapro_project/
│   ├── settings.py          # Django configuration
│   └── urls.py              # Main URL routes
└── accounts/
    ├── views.py             # View handlers for signup
    ├── models.py            # Database models (User, Provider)
    ├── urls.py              # Signup URL routes
    └── templates/accounts/  # HTML templates
        ├── register_user.html
        └── register_provider.html
```

---

## Important Notes
- The Django development server is **local-only** by default (127.0.0.1)
- Use `0.0.0.0:8000` to allow network access
- Do NOT use the development server in production
- Default database is SQLite (`db.sqlite3`) - fine for development

---

## Questions?
Check the Django output in terminal for error messages—they usually indicate the exact issue.

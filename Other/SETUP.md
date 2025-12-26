# Local Pro Connect - Setup Guide for Team Members

## Prerequisites
- Python 3.11+ installed on your machine
- Git installed
- Browser (Chrome, Firefox, Safari, Edge)

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/junior25hacker/Local-Pro-Connect.git
cd LocaProConnect-WebAPP
```

### 2. Create and Activate Virtual Environment

**On Linux/Mac:**
```bash
cd Django
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**
```bash
cd Django
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist, run:
```bash
pip install Django==5.2.9 Pillow==12.0.0
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create Superuser (Admin)
```bash
python manage.py createsuperuser
# Follow the prompts to create an admin account
```

### 6. Start the Development Server
```bash
python manage.py runserver 0.0.0.0:8000
```

You should see output like:
```
Starting development server at http://127.0.0.1:8000/
```

### 7. Access the Application
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **User Signup:** http://127.0.0.1:8000/accounts/signup/user/
- **Provider Signup:** http://127.0.0.1:8000/accounts/signup/provider/
- **Home:** http://127.0.0.1:8000/

## Project Structure
```
LocaProConnect-WebAPP/
├── Django/                    # Django backend
│   ├── .venv/                # Virtual environment
│   ├── accounts/             # User/Provider app
│   │   ├── models.py         # Database models
│   │   ├── views.py          # Views/Business logic
│   │   ├── forms.py          # Forms
│   │   ├── templates/        # HTML templates
│   │   └── migrations/       # Database migrations
│   ├── locapro_project/      # Django project settings
│   ├── templates/            # Base templates
│   ├── media/                # Uploaded files (images)
│   ├── db.sqlite3            # Database
│   ├── manage.py             # Django management
│   └── requirements.txt      # Dependencies
├── pages/                     # Static HTML pages
├── assets/                    # CSS, JS, images
└── index.html                # Main landing page
```

## Key Features
1. **User Registration:** Sign up as a regular user
2. **Provider Registration:** Sign up as a service provider
3. **Profile Picture Upload:** Providers can upload profile pictures
4. **Admin Panel:** Manage users and providers (http://127.0.0.1:8000/admin/)
5. **Database:** SQLite stores all user and provider data

## Database
- **Location:** `Django/db.sqlite3`
- **Tables:**
  - `auth_user` — User accounts
  - `accounts_userprofile` — User profile data
  - `accounts_providerprofile` — Provider profile data

## Troubleshooting

### Virtual Environment Not Activating
Make sure you're in the `Django/` directory when activating.

### Django Not Found
Make sure the virtual environment is activated (you should see `(.venv)` in your terminal).

### Port 8000 Already in Use
Run on a different port:
```bash
python manage.py runserver 0.0.0.0:8001
```

### Database Errors
Reset the database:
```bash
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

## Next Steps
- Explore the admin panel to view registered users and providers
- Test the signup forms
- Upload a profile picture as a provider
- Check the database to see stored data

## Support
If you encounter issues, check:
1. Python version: `python --version` (should be 3.11+)
2. Virtual environment is activated
3. All dependencies installed: `pip list`
4. Django is running: `python manage.py check`

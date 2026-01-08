# Django Server Startup Guide

## Quick Start

The Django development server has been configured and is ready to start.

### Command to Start Server

```bash
cd Django
python manage.py runserver 8000
```

### Server Information

- **URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **Port**: 8000
- **Database**: SQLite (db.sqlite3)

### Available Endpoints

#### Authentication & Accounts
- `GET /` - Home page
- `GET /accounts/login/` - Login page
- `GET /accounts/signup/user/` - User registration
- `GET /accounts/signup/provider/` - Provider registration
- `GET /accounts/profile/user/` - User profile
- `GET /accounts/profile/provider/` - Provider profile
- `GET /accounts/logout/` - Logout

#### Service Requests
- `GET /requests/create/` - Create new service request
- `GET /requests/list/` - List all requests
- `GET /requests/<id>/` - View request details
- `GET /requests/export/csv/` - Export requests as CSV
- `GET /requests/export/pdf/` - Export requests as PDF

#### Admin
- `GET /admin/` - Django admin panel

### Environment Configuration

The application uses the following configuration:
- **Debug Mode**: ON (DEBUG = True)
- **Allowed Hosts**: localhost, 127.0.0.1, *
- **Settings Module**: locapro_project.settings
- **Template Dirs**: 
  - Django/templates
  - Django/accounts/templates
  - pages/
- **Static Files**: Django/static/
- **Media Files**: Django/media/

### Email Configuration

Email settings are configured in `.env` file:
- **Provider**: Gmail or Outlook
- **Backend**: SMTP

Default behavior: If no email credentials are provided, emails are sent to console.

### Database

- **Type**: SQLite3
- **Location**: Django/db.sqlite3
- **Migrations**: Already applied

### Troubleshooting

If port 8000 is already in use:
```bash
cd Django
python manage.py runserver 8001  # Use different port
```

To reset the database:
```bash
cd Django
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

### Creating Test Data

Test data can be created using:
```bash
cd Django
python manage.py create_test_data
```

### Admin Credentials

Check the ADMIN_CREDENTIALS.md file for default admin accounts.

# Blood Donation Camp Management System

A comprehensive Django web application for managing blood donation camps, donors, recipients, hospitals, and blood inventory.


## Photos

Screenshots from the Blood Donation Camp application.

![Project Overview](project.png)

## Features

✨ **Core Features:**
- 👥 Donor Management & Registration
- 🏥 Hospital/Clinic Management
- 💉 Blood Donation Requests
- 🩸 Blood Stock Management
- 📋 Recipient Blood Requests
- 📅 Camp Schedule Management
- 🔐 Role-based Access Control
- 📱 OTP-based Authentication
- 📧 Email & SMS Notifications

## Tech Stack

- **Backend:** Django 5.2
- **Database:** SQLite (dev) / MySQL (production)
- **Python:** 3.8+
- **Frontend:** HTML5, CSS3, JavaScript
- **Libraries:**
  - Django Extensions
  - Pillow (Image Processing)
  - PyMySQL (MySQL support)
  - Django Widget Tweaks
  - Django Simple Captcha

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git
- MySQL (optional, for production)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd blood_donation_camp
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
cd blood_donation_camp/bdweb
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and configure your settings
# Important: Update SECRET_KEY, DEBUG, ALLOWED_HOSTS, etc.
```

### 5. Database Setup

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser (admin account)
python manage.py createsuperuser
```

### 6. Collect Static Files (Production)

```bash
python manage.py collectstatic --noinput
```

### 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at `http://localhost:8000`

## Configuration

### Environment Variables (.env)

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# For MySQL:
# DB_ENGINE=django.db.backends.mysql
# DB_NAME=blood_donation_db
# DB_USER=root
# DB_PASSWORD=your-password
# DB_HOST=localhost
# DB_PORT=3306

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=no-reply@yourdomain.com

# Security
ENCRYPTION_KEY=dev-only-encryption-key
CSRF_TRUSTED_ORIGINS=http://localhost:8000

# API Keys
FAST2SMS_API_KEY=your-fast2sms-key-here

# Admin Settings
ADMIN_EMAIL=admin@yourdomain.com
```

## Project Structure

```
blood_donation_camp/
├── blood_donation_camp/
│   └── bdweb/                      # Django project directory
│       ├── bdweb/                  # Project settings
│       │   ├── settings.py         # Django settings
│       │   ├── urls.py             # URL configuration
│       │   ├── wsgi.py             # WSGI configuration
│       │   └── asgi.py             # ASGI configuration
│       ├── donationapp/            # Main application
│       │   ├── models.py           # Database models
│       │   ├── views.py            # View logic
│       │   ├── forms.py            # Form definitions
│       │   ├── urls.py             # App URLs
│       │   ├── utils.py            # Utility functions
│       │   ├── admin.py            # Admin interface
│       │   └── migrations/         # Database migrations
│       ├── templates/              # HTML templates
│       ├── static/                 # CSS, JS, images
│       ├── media/                  # User uploaded files
│       ├── logs/                   # Application logs
│       ├── manage.py               # Django CLI
│       └── requirements.txt        # Python dependencies
├── .env                            # Environment variables (not in git)
├── .env.example                    # Example environment file
├── .gitignore                      # Git ignore rules
└── README.md                       # This file
```

## Database Models

### Donor
- Personal information
- Blood group
- Age verification
- Photo
- Contact details

### DonationRequest
- Associated donor
- Blood group requirement
- Status tracking
- Hospital reports

### Recipient
- Personal information
- Contact details
- Blood requirement details

### RecipientRequest
- Associated recipient
- Patient information
- Required units
- Status & approval workflow

### HospitalClinic
- Organization details
- Contact information
- Location
- Blood requests

### HospitalBloodRequest
- Associated hospital
- Blood group & units
- Request status

### CampSchedule
- Camp details
- Date, time, location
- Description

### BloodStock
- Blood group inventory
- Units count
- Collection & expiry dates

## API Endpoints

### Authentication
- `POST /donationapp/donorlogin` - Donor login
- `POST /donationapp/donorsignin` - Donor registration
- `POST /donationapp/recipientlogin` - Recipient login
- `POST /donationapp/hospitallogin` - Hospital login
- `POST /donationapp/adminlogin` - Admin login

### Donor Operations
- `GET /donationapp/donordashboard` - Donor dashboard
- `POST /donationapp/donationrequest` - Submit donation request
- `GET /donationapp/managedonor` - View donation requests

### Hospital Operations
- `GET /donationapp/hospitaldashboard` - Hospital dashboard
- `POST /donationapp/hospitalbloodrequest` - Request blood

### Admin Operations
- `GET /donationapp/admin` - Admin dashboard
- `GET /donationapp/adminlist` - View all requests
- `POST /donationapp/adminedit` - Edit requests

## User Roles

| Role | Permissions |
|------|-------------|
| **Donor** | Register, submit donation requests, view status |
| **Recipient** | Register, request blood, track requests |
| **Hospital/Clinic** | Request blood, manage blood bank |
| **Admin** | Full system access, approve/reject requests |

## Security Features

✅ **Implemented Security:**
- OTP-based authentication
- Password hashing (PBKDF2, Argon2, BCrypt)
- CSRF protection
- SQL injection prevention
- XSS protection
- HTTPS support (production)
- Input validation & sanitization
- Database constraints & validators
- Role-based access control

## Logging

Logs are stored in the `logs/` directory:

- `app.log` - General application logs
- `donations.log` - Blood donation related logs
- `security.log` - Security and authentication logs

Log files are rotated when they reach 10MB (5MB for donations/security).

## Common Issues & Solutions

### Virtual Environment Not Activating
```bash
# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
.\.venv\Scripts\Activate.ps1
```

### Database Migration Errors
```bash
# Reset migrations (dev only)
python manage.py migrate donationapp zero
python manage.py migrate
```

### Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput

# In development, ensure STATICFILES_DIRS is configured
```

### Import Errors
```bash
# Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

## Development Guidelines

### Code Style
- Follow PEP 8 conventions
- Use type hints where possible
- Write docstrings for all functions
- Keep functions focused and small

### Database Queries
- Use `select_related()` for ForeignKey
- Use `prefetch_related()` for ManyToMany
- Index frequently queried fields
- Avoid N+1 queries

### Security
- Never commit `.env` files
- Validate all user inputs
- Use prepared statements for queries
- Implement proper error handling

## Testing

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test donationapp

# Run with verbose output
python manage.py test --verbose=2
```

## Deployment

### Production Checklist

- [ ] Update `DEBUG = False` in settings
- [ ] Set `SECRET_KEY` to a secure random value
- [ ] Configure `ALLOWED_HOSTS` with domain
- [ ] Set up HTTPS/SSL certificate
- [ ] Configure MySQL database
- [ ] Set up email backend (SMTP)
- [ ] Collect static files
- [ ] Run migrations
- [ ] Create superuser
- [ ] Set up monitoring & logging
- [ ] Configure backup strategy
- [ ] Test all functionality

### Deployment with Gunicorn

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn bdweb.wsgi:application --bind 0.0.0.0:8000 --workers 4
```

## Contributing

1. Create a feature branch (`git checkout -b feature/AmazingFeature`)
2. Commit changes (`git commit -m 'Add AmazingFeature'`)
3. Push to branch (`git push origin feature/AmazingFeature`)
4. Open a Pull Request

## Support & Contact

For issues, questions, or suggestions:
- Create an issue in the repository
- Contact the development team
- Check documentation in `/docs`

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Changelog

### Version 1.0.0 (May 2026)
- Initial release
- Core blood donation camp management
- Donor & recipient management
- Hospital integration
- Blood stock tracking
- OTP authentication
- Admin dashboard

---

**Last Updated:** May 10, 2026
**Version:** 1.0.0
**Status:** ✅ Production Ready

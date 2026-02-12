# Animal Protein Tracker API (ap_tracker)
A Django REST API for tracking daily protein intake.
Users can log their protein consumption from different animal sources, and each user can only access and manage their own records.

This project demonstrates:
- Custom Django user model
- RESTful API with Django REST Framework (DRF)
- Authentication and permission control
- Secure object ownership enforcement


# Features
- User authentication required for all API access
- Custom User model with body weight (weight_kg)
- CRUD operations for Protein Intake
- Catalog of Animal Protein Sources
- Users can only view and modify their own intake records
- Standard REST responses (200, 201, 400, 401, 404)


# Tech Stack
- Python 3
- Django
- Django REST Framework
- SQLite (default)
- JWT authentication (SimpleJWT)


# Project Structure
ap_tracker/
    ap_tracker/
        __init__.py
        asgi.py
        settings.py
        urls.py
        wsgi.py
    tracker/
        migrations/
        __init__.py
        admin.py
        apps.py
        models.py
        permissions.py
        serializers.py
        tests.py
        urls.py
    manage.py
    README.md


# Installation & Setup
1. Clone the repository
- git clone https://github.com/georginalaing16-jpg/Animal-Protein-Tracker-project.git
- cd ap_tracker

2. Install dependencies
- pip install django
- pip install djangorestframework
- pip install djangorestframework-simplejwt    


# Configuration
Add apps in settings.py
INSTALLED_APPS = [
    ...
    "rest_framework",
    "tracker",
]

DRF Authentication
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

All endpoints require authentication.
 

# Custom User Model
The project uses a custom user model:
Fields:
- username
- email (unique)
- weight_kg
- created_at

AUTH_USER_MODEL = "tracker.User"

Configured before migration.


# Database Setup
Run migrations:
- python manage.py makemigrations
- python manage.py migrate

Create admin user:
- python manage.py createsuperuser

Run server:
- python manage.py runserver

 
# API Endpoints
1. Base URL:
/api/

2. Protein Intake
Method         Endpoint            Description
GET          /api/intakes/        List current user’s intake records
POST         /api/intakes/        Create new intake
GET         /api/intakes/{id}/    Retrieve a record
PUT/PATCH   /api/intakes/{id}/    Update record
DELETE      /api/intakes/{id}/    Delete record

3. Animal Protein Sources
Method              Endpoint                  Description
GET              /api/sources/                List sources
POST             /api/sources/                Create source
GET              /api/sources/{id}/           Retrieve source
PUT/PATCH        /api/sources/{id}/           Update source
DELETE           /api/sources/{id}/           Delete source


# Permissions & Security
1. All endpoints require authentication
2. Users only see their own ProteinIntake records
3. Ownership is enforced by:
   - Query filtering (user=request.user)
   - Automatic owner assignment on create
   - Custom IsOwner permission
4. Accessing another user’s record returns:
   - 404 Not Found

 
# Admin Panel
Access admin at:
http://127.0.0.1:8000/admin/

Use superuser credentials.
Logged-in, you can manage:
- Users
- Protein Sources
- Intake records


# Expected API Behavior
Scenario                              Response
Not authenticated                   401 Unauthorized
Invalid data                        400 Bad Request
Record not found or not owned       404 Not Found
Successful create                   201 Created
Successful delete                   204 No Content

 
# Future Improvements
- Daily protein targets
- Intake summary per day
- JWT authentication
- Admin-only access for protein sources
- Filtering and analytics endpoints


# Purpose
This project demonstrates backend skills in:
- Django architecture
- REST API design
- Authentication & authorization
- Secure multi-user data handling


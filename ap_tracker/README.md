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





### WEEK 2

# What was added

1. Daily Protein Targets (per user)
- Users can create, view, update, and delete a protein target for a specific date.
- Only one target per user per date is allowed (database constraint).

2. Intake Summaries (per user)
- Stores daily totals of protein intake alongside the target for that day.
- Only one summary per user per date is allowed.

# Ownership and Security

- All records are automatically linked to the logged-in user.
- Users cannot see or modify other users’ data.
- The user field is read-only and set using request.user.
- Requests for another user’s data return 404 Not Found.

# Daily Summary Generator

Endpoint:
POST /api/summaries/generate/?date=YYYY-MM-DD

This endpoint:
- Validates the date
- Calculates total protein consumed that day from ProteinIntake
- Retrieves the user’s DailyProteinTarget for the same date
- Creates or updates the IntakeSummary for that day

Behavior
- Returns 200 OK with the summary
- Returns 400 if the date is missing or invalid
- Returns 404 if no target exists for that date
- Uses update-or-create so repeated calls don’t create duplicates

Why this design
- Database constraints ensure one target and one summary per day
- Server-side aggregation keeps calculations accurate and consistent
- Idempotent generation makes the endpoint safe to call multiple times
- Per-user scoping ensures full data isolation

What the system now supports
- Log daily protein intake
- Set daily protein targets
- Generate daily intake vs. target summaries
- Secure, RESTful, user-isolated data management

This completes the core tracking workflow defined in the ERD.


### Key Improvements
1. User Profile Management
- Added /api/me/ endpoint.
- Users can view their profile and update weight_kg.
- Username and email remain read-only for safety.

2. Automatic Daily Targets
- Daily targets are now calculated automatically using:
   * target_grams = weight_kg × 0.8
- Users no longer provide target_grams.
- If weight is not set, the API returns 400 Bad Request.

3. JWT Authentication
- Added token-based authentication for Postman, mobile, or frontend use.
- Users obtain a token via /api/token/ and include it in requests.
- Session authentication still works for browser testing.

4. Date Filtering
- Intake records can be filtered:
   * By single date
   * By date range
- Invalid formats return 400.

5. Protein Source Security
- All authenticated users can read protein sources.
- Only admin users can create, update, or delete them.
- Non-admin write attempts return 403 Forbidden.

6. Data Validation
- weight_kg must be greater than 0.
- protein_quantity_grams must be greater than 0.
- Invalid values return 400 Bad Request.

# Recommended Usage Flow
1. Authenticate (JWT or session)
2. Set weight via /api/me/
3. Create daily target (auto-calculated)
4. Log protein intake
5. Generate daily summary
6. Retrieve summary for the date

# Result
- The API now provides:
- User-driven profile management
- Consistent server-side calculations
- Secure per-user data access
- Practical querying and filtering
- Admin-controlled reference data
- Production-ready authentication and validation

This completes a full end-to-end protein tracking workflow.
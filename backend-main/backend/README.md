# TypeID Backend - Module 1: User Registration

Backend API for TypeID: Behavioral Biometrics for Passwordless Login system.

## Module 1: User Registration with Keystroke Enrollment

This module provides user registration functionality with keystroke biometric enrollment and a fallback password system.

## Project Structure

```
backend/
├── app.py                          # Main Flask application entry point
├── config.py                       # Configuration settings
├── extensions.py                   # Flask extensions (db, etc.)
├── models/                         # Database models
│   ├── __init__.py
│   ├── user.py                    # User model
│   └── keystroke_profile.py       # Keystroke profile model
├── routes/                         # API routes/endpoints
│   ├── __init__.py
│   └── registration_routes.py     # Registration routes
├── services/                       # Business logic layer
│   ├── __init__.py
│   ├── user_service.py            # User registration service
│   └── keystroke_service.py       # Keystroke preprocessing service
├── repositories/                   # Data access layer
│   ├── __init__.py
│   ├── user_repository.py         # User database operations
│   └── keystroke_profile_repository.py  # Keystroke profile database operations
├── utils/                          # Utility functions
│   ├── __init__.py
│   ├── password_util.py           # Password hashing
│   └── validation_util.py         # Input validation
└── requirements.txt                # Python dependencies
```

## Architecture

The project follows **Clean Architecture** principles with clear separation of concerns:

- **Models**: Database entities (SQLAlchemy models)
- **Repositories**: Data access layer (database operations)
- **Services**: Business logic layer (validation, keystroke preprocessing)
- **Routes**: API endpoints (HTTP request/response handling)
- **Utils**: Shared utility functions

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the `backend/` directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///typeid.db
```

### 3. Run the Application

```bash
python app.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

### Base URL
```
http://localhost:5000/api
```

### Endpoints

#### 1. Health Check
```
GET /api/health
```
Returns service status.

#### 2. User Registration
```
POST /api/register
```
Register a new user with username, email, role, password, and keystroke data.

**Request Body:**
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "role": "student",
    "password": "securepassword123",
    "keystroke_data": {
        "dwell_times": [120, 150, 130, 140, 125],
        "flight_times": [50, 60, 55, 58, 52]
    }
}
```

**Response (201):**
```json
{
    "message": "User registered successfully",
    "user_id": 1
}
```

**Error Responses:**

- `400 Bad Request`: Missing required fields, invalid data, or email already exists
- `500 Internal Server Error`: Server error

## Validation Rules

### Name
- 2 to 100 characters
- Letters, spaces, hyphens, and apostrophes only

### Email
- Valid email format (standard regex validation)
- Must be unique

### Role
- Must be one of: `student`, `teacher`, `admin` (case-insensitive)

### Password
- Minimum 8 characters
- Stored as bcrypt hash (not plain text)

### Keystroke Data
- Must contain `dwell_times` and/or `flight_times` arrays
- Arrays must contain numeric values
- At least one array must have data

## Database Schema

### Users Table
- `id` (PK, Integer)
- `name` (String, 100 chars)
- `email` (String, 120 chars, unique, indexed)
- `role` (String, 20 chars)
- `password_hash` (String, 255 chars)
- `created_at` (DateTime)

### Keystroke Profiles Table
- `id` (PK, Integer)
- `user_id` (FK to users.id, indexed)
- `keystroke_features` (JSON)
  - `mean_dwell_time` (float)
  - `mean_flight_time` (float)
  - `features` (array)
- `attempts` (Integer, default: 1)
- `created_at` (DateTime)

## Keystroke Processing

The service layer preprocesses keystroke data by:
1. Validating input data structure
2. Calculating mean dwell time (average time key is pressed)
3. Calculating mean flight time (average time between key releases and next key press)
4. Creating a clean feature vector with processed features
5. Storing the processed features in the database

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Running with Flask CLI

```bash
flask run
```

## Notes

- Passwords are hashed using bcrypt before storage (NEVER stored in plain text)
- Keystroke biometrics is the primary authentication method; password is only a fallback
- Keystroke data is preprocessed and stored as features (mean dwell time, mean flight time)
- Email addresses are normalized to lowercase before storage
- All validation is performed in the service layer, not in routes
- Database tables are automatically created on first run

## Testing

Test the application by:
1. Starting the server: `python app.py`
2. Checking root endpoint: `GET http://localhost:5000/`
3. Checking health: `GET http://localhost:5000/api/health`
4. Registering a user: `POST http://localhost:5000/api/register` with the request body shown above

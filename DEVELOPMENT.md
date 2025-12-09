# Teaching Management System - Development Guide

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Initialize Database

```bash
python -m tms.init_db
```

This will:
- Create all database tables
- Seed sample data (admin, teachers, students, courses)

### 3. Run the Application

```bash
uvicorn tms.api.main:app --reload
```

The API will be available at: `http://localhost:8000`

### 4. Access API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Default Credentials

After running `init_db.py`, you can log in with:

- **Admin**: username: `admin`, password: `admin123`
- **Teacher**: username: `prof_zhang`, password: `teacher123`
- **Student**: username: `student1`, password: `student123`

## API Usage Examples

### Authentication

#### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

Response:
```json
{
  "access_token": "admin:1",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@tms.com",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00"
  }
}
```

**Important**: Use the `access_token` in subsequent requests:
```bash
-H "Authorization: Bearer admin:1"
```

### Course Management

#### List All Courses
```bash
curl "http://localhost:8000/courses/"
```

#### Create a Course (Teacher/Admin only)
```bash
curl -X POST "http://localhost:8000/courses/" \
  -H "Authorization: Bearer prof_zhang:2" \
  -H "Content-Type: application/json" \
  -d '{
    "course_code": "CS301",
    "name": "Web Development",
    "teacher_id": 1,
    "credits": 3.0,
    "capacity": 25,
    "semester": "2024 Spring",
    "description": "Learn modern web development",
    "schedule": "Mon/Wed 10:00-11:30",
    "location": "Building C, Room 101"
  }'
```

#### Search Courses
```bash
curl "http://localhost:8000/courses/search/by-name?name=programming"
```

#### Check Course Capacity
```bash
curl "http://localhost:8000/courses/1/capacity"
```

### Enrollment

#### Enroll in a Course
```bash
curl -X POST "http://localhost:8000/enrollments/" \
  -H "Authorization: Bearer student1:4" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1
  }'
```

The system will automatically:
- ✓ Check course capacity
- ✓ Detect schedule conflicts
- ✓ Prevent duplicate enrollments

#### Get Student's Enrollments
```bash
curl "http://localhost:8000/enrollments/student/1" \
  -H "Authorization: Bearer student1:4"
```

### Grade Management

#### Record a Grade (Teacher/Admin only)
```bash
curl -X POST "http://localhost:8000/grades/" \
  -H "Authorization: Bearer prof_zhang:2" \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": 1,
    "course_id": 1,
    "score": 92.5,
    "comments": "Excellent work!"
  }'
```

Letter grades are calculated automatically:
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: 0-59

#### Get Student Grades
```bash
curl "http://localhost:8000/grades/student/1" \
  -H "Authorization: Bearer student1:4"
```

#### Get Course Statistics
```bash
curl "http://localhost:8000/grades/course/1/statistics" \
  -H "Authorization: Bearer prof_zhang:2"
```

Response includes:
```json
{
  "average": 85.5,
  "maximum": 98.0,
  "minimum": 72.0,
  "pass_rate": 95.0,
  "total_students": 20
}
```

## Testing

### Run All Tests
```bash
pytest
```

### Run with Coverage
```bash
pytest --cov=tms --cov-report=html
```

### View Coverage Report
Open `htmlcov/index.html` in your browser.

## Project Structure

```
tms/
├── api/                    # API layer (FastAPI)
│   ├── dependencies.py     # Auth & dependency injection
│   ├── main.py            # FastAPI app
│   ├── routes/            # API endpoints
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── students.py
│   │   ├── enrollments.py
│   │   └── grades.py
│   └── schemas/           # Pydantic models
│       └── common.py
├── application/           # Application services
│   └── services/
│       ├── auth_service.py
│       ├── course_service.py
│       ├── student_service.py
│       ├── teacher_service.py
│       ├── enrollment_service.py
│       ├── grade_service.py
│       ├── material_service.py
│       ├── assignment_service.py
│       ├── notification_service.py
│       └── system_service.py
├── domain/                # Domain entities (currently in infra/models.py)
├── infra/                 # Infrastructure layer
│   ├── database.py        # DB configuration
│   ├── models.py          # ORM models
│   ├── base_repository.py # Base repository
│   └── repositories/      # Data access
│       ├── user_repository.py
│       ├── student_repository.py
│       ├── teacher_repository.py
│       ├── course_repository.py
│       ├── enrollment_repository.py
│       ├── assignment_repository.py
│       ├── material_repository.py
│       ├── grade_repository.py
│       └── notification_repository.py
├── tests/                 # Unit & integration tests
│   ├── conftest.py
│   ├── test_services/
│   └── test_api/
├── config.py              # Application config
└── init_db.py            # Database initialization
```

## Core Features Implemented

### 1. ✅ User & Authentication
- User creation with role-based access (Admin/Teacher/Student)
- Password hashing with bcrypt
- Simple session-based authentication
- RBAC permission checking

### 2. ✅ Course Management
- CRUD operations for courses
- Teacher assignment
- Capacity management
- Schedule information
- Course search by name

### 3. ✅ Student Management
- Student profile management
- Status tracking (Active/On Leave/Graduated)
- Academic records

### 4. ✅ Teacher Management
- Teacher profile management
- Department and title tracking
- Course assignment viewing

### 5. ✅ Enrollment
- Course enrollment with validation
- **Capacity checking**
- **Schedule conflict detection**
- Course withdrawal
- Enrollment history

### 6. ✅ Grade Management
- Grade recording and updates
- Automatic letter grade calculation
- **Course statistics** (avg, max, min, pass rate)
- GPA calculation
- Student grade viewing

### 7. ✅ Material Management (Service Layer)
- File upload/download
- Access control (enrolled students only)
- File type detection
- Search functionality

### 8. ✅ Assignment & Submission (Service Layer)
- Assignment creation
- Student submissions (text + file)
- Grading with feedback
- Late submission detection

### 9. ✅ Notifications (Service Layer)
- System notifications
- Bulk messaging
- Event-triggered notifications
- Read/unread status

### 10. ✅ System Administration (Service Layer)
- User management (freeze/unfreeze)
- System configuration
- Database backup/restore
- Statistics and audit logging

## Architecture Highlights

### Layered Architecture
The application follows a clean layered architecture:

1. **API Layer** (FastAPI): HTTP endpoints, request validation
2. **Application Layer** (Services): Business logic orchestration
3. **Domain Layer** (Entities): Business rules and domain models
4. **Infrastructure Layer** (Repositories): Data persistence

### Repository Pattern
All data access goes through repositories, making it easy to:
- Switch databases (SQLite to MySQL/PostgreSQL)
- Mock data for testing
- Maintain consistent query patterns

### Dependency Injection
FastAPI's dependency injection is used for:
- Database sessions
- Authentication
- Role-based access control

## Next Steps / Enhancements

1. **JWT Authentication**: Replace simple token auth with JWT
2. **File Upload Endpoints**: Add API routes for material uploads
3. **Assignment Endpoints**: Complete assignment submission API
4. **Notification Endpoints**: Add notification API routes
5. **Email Integration**: Send email notifications
6. **Advanced Search**: Full-text search for courses
7. **Pagination**: Add pagination metadata to list responses
8. **Database Migrations**: Use Alembic for schema versioning
9. **Docker**: Containerize the application
10. **Frontend**: Build a React/Vue.js frontend

## Troubleshooting

### Database is locked
If you get "database is locked" errors with SQLite:
- Restart the application
- Or switch to PostgreSQL/MySQL for production

### Import errors
Make sure you're running commands from the project root:
```bash
cd /path/to/TeachingManagementSystem
python -m tms.init_db
```

### Permission errors
Ensure you're using the correct authorization header with the right user role.

## Support

For issues or questions:
1. Check the API documentation at `/docs`
2. Review the code in the relevant service/repository
3. Run tests to verify functionality

# Teaching Management System - Complete API Reference

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip3 install -r requirements.txt

# 2. Initialize database with sample data
python3 -m tms.init_db

# 3. Start the server
uvicorn tms.api.main:app --reload
```

**Access Points:**
- API Server: http://localhost:8000
- Interactive Docs (Swagger UI): http://localhost:8000/docs
- Alternative Docs (ReDoc): http://localhost:8000/redoc

**Default Test Accounts:**
- Admin: `admin` / `admin123`
- Teacher: `prof_zhang` / `teacher123`
- Student: `student1` / `student123`

---

## 📡 Complete API Endpoints Reference

### 1️⃣ Authentication (`/auth`)

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "access_token": "admin:1",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@tms.com",
    "full_name": "System Administrator",
    "role": "admin",
    "is_active": true
  }
}
```

**Use the access_token in all subsequent requests:**
```bash
Authorization: Bearer admin:1
```

#### Logout
```bash
POST /auth/logout
```

---

### 2️⃣ Courses (`/courses`)

#### Create Course (Teacher/Admin)
```bash
POST /courses/
Authorization: Bearer prof_zhang:2

{
  "course_code": "CS301",
  "name": "Web Development",
  "teacher_id": 1,
  "credits": 3.0,
  "capacity": 25,
  "semester": "2024 Spring",
  "description": "Learn modern web development",
  "schedule": "Mon/Wed 10:00-11:30",
  "location": "Building C, Room 101"
}
```

#### List Courses
```bash
GET /courses/?skip=0&limit=20&active_only=true
GET /courses/?teacher_id=1
GET /courses/?semester=2024%20Spring
```

#### Search Courses
```bash
GET /courses/search/by-name?name=programming
```

#### Get Course Details
```bash
GET /courses/1
```

#### Check Course Capacity
```bash
GET /courses/1/capacity

# Response
{
  "capacity": 30,
  "current_enrollment": 15,
  "available_slots": 15,
  "is_full": false
}
```

#### Delete Course (Admin)
```bash
DELETE /courses/1
Authorization: Bearer admin:1
```

---

### 3️⃣ Students (`/students`)

#### Create Student (Admin)
```bash
POST /students/
Authorization: Bearer admin:1

{
  "username": "student4",
  "email": "student4@tms.com",
  "password": "student123",
  "full_name": "Zhang San",
  "student_number": "S2024004",
  "grade": "Freshman",
  "major": "Computer Science",
  "phone": "123-456-7895"
}
```

#### List Students
```bash
GET /students/?skip=0&limit=20
```

#### Get Student Details
```bash
GET /students/1
```

---

### 4️⃣ Teachers (`/teachers`)

#### Create Teacher (Admin)
```bash
POST /teachers/
Authorization: Bearer admin:1

{
  "username": "prof_wang",
  "email": "wang@tms.com",
  "password": "teacher123",
  "full_name": "Wang Lei",
  "employee_number": "T003",
  "department": "Physics",
  "title": "Associate Professor",
  "phone": "123-456-7896",
  "office": "Room 303"
}
```

#### List Teachers
```bash
GET /teachers/?skip=0&limit=20
GET /teachers/?department=Computer%20Science
```

#### Get Teacher's Courses
```bash
GET /teachers/1/courses
```

#### Delete Teacher (Admin)
```bash
DELETE /teachers/1
Authorization: Bearer admin:1
```

---

### 5️⃣ Enrollments (`/enrollments`)

#### Enroll in Course
```bash
POST /enrollments/
Authorization: Bearer student1:4

{
  "student_id": 1,
  "course_id": 1
}
```

**Automatic Validations:**
- ✅ Checks if course is at capacity
- ✅ Detects schedule conflicts with existing enrollments
- ✅ Prevents duplicate enrollments
- ✅ Verifies course is active

**Possible Error Responses:**
- `"Course is at full capacity"`
- `"Schedule conflict with course: Data Structures"`
- `"Student is already enrolled in this course"`
- `"Course is not active"`

#### Withdraw from Course
```bash
DELETE /enrollments/123
Authorization: Bearer student1:4
```

#### Get Student's Enrollments
```bash
GET /enrollments/student/1
Authorization: Bearer student1:4
```

---

### 6️⃣ Grades (`/grades`)

#### Record/Update Grade (Teacher/Admin)
```bash
POST /grades/
Authorization: Bearer prof_zhang:2

{
  "student_id": 1,
  "course_id": 1,
  "score": 92.5,
  "letter_grade": "A",  # Optional - auto-calculated if not provided
  "comments": "Excellent work on the final project!"
}
```

**Letter Grade Auto-Calculation:**
- A: 90-100
- B: 80-89
- C: 70-79
- D: 60-69
- F: 0-59

#### Get Student's Grades
```bash
GET /grades/student/1
Authorization: Bearer student1:4
```

#### Get Course Grades (Teacher/Admin)
```bash
GET /grades/course/1
Authorization: Bearer prof_zhang:2
```

#### Get Course Statistics
```bash
GET /grades/course/1/statistics

# Response
{
  "average": 85.5,
  "maximum": 98.0,
  "minimum": 72.0,
  "pass_rate": 95.0,
  "total_students": 20
}
```

---

### 7️⃣ Assignments (`/assignments`)

#### Create Assignment (Teacher/Admin)
```bash
POST /assignments/
Authorization: Bearer prof_zhang:2

{
  "course_id": 1,
  "title": "Final Project",
  "description": "Build a web application using the technologies covered",
  "due_date": "2024-06-15T23:59:59",
  "total_points": 100.0
}
```

#### Get Course Assignments
```bash
GET /assignments/course/1
```

#### Submit Assignment (Student)
```bash
POST /assignments/1/submit
Authorization: Bearer student1:4
Content-Type: multipart/form-data

student_id=1
content="Here is my project submission..."
file=@/path/to/project.zip
```

#### Get Assignment Submissions (Teacher/Admin)
```bash
GET /assignments/1/submissions
GET /assignments/1/submissions?ungraded_only=true
Authorization: Bearer prof_zhang:2
```

#### Grade Submission (Teacher/Admin)
```bash
PUT /assignments/submissions/1/grade
Authorization: Bearer prof_zhang:2

{
  "score": 95.0,
  "feedback": "Great work! Well-structured code and excellent documentation."
}
```

#### Delete Assignment (Teacher/Admin)
```bash
DELETE /assignments/1
Authorization: Bearer prof_zhang:2
```

---

### 8️⃣ Materials (`/materials`)

#### Upload Material (Teacher/Admin)
```bash
POST /materials/
Authorization: Bearer prof_zhang:2
Content-Type: multipart/form-data

course_id=1
title="Lecture 5: Database Design"
description="SQL and database normalization slides"
file=@/path/to/lecture5.pdf
```

#### Get Course Materials
```bash
GET /materials/course/1
GET /materials/course/1?file_type=pdf
```

#### Download Material
```bash
GET /materials/1
Authorization: Bearer student1:4
```

**Access Control:**
- Students can only download materials from courses they're enrolled in
- Teachers and Admins can access all materials

#### Delete Material (Teacher/Admin)
```bash
DELETE /materials/1
Authorization: Bearer prof_zhang:2
```

---

### 9️⃣ Notifications (`/notifications`)

#### Get My Notifications
```bash
GET /notifications/
GET /notifications/?unread_only=true
Authorization: Bearer student1:4
```

#### Get Unread Count
```bash
GET /notifications/unread-count
Authorization: Bearer student1:4

# Response
{
  "unread_count": 5
}
```

#### Mark as Read
```bash
PUT /notifications/1/read
Authorization: Bearer student1:4
```

#### Mark All as Read
```bash
PUT /notifications/mark-all-read
Authorization: Bearer student1:4
```

#### Delete Notification
```bash
DELETE /notifications/1
Authorization: Bearer student1:4
```

**Event-Triggered Notifications:**
The system automatically sends notifications for:
- 📝 New assignments posted
- 📊 Grades released
- ✅ Enrollment confirmations
- ✅ Assignment graded

---

### 🔟 System Admin (`/admin`)

#### Get System Statistics (Admin)
```bash
GET /admin/stats
Authorization: Bearer admin:1

# Response
{
  "total_users": 50,
  "total_students": 35,
  "total_teachers": 10,
  "total_courses": 15,
  "total_enrollments": 120,
  "active_users": 48,
  "current_semester": "2024 Spring"
}
```

#### Get System Configuration (Admin)
```bash
GET /admin/config
Authorization: Bearer admin:1
```

#### Update Configuration (Admin)
```bash
PUT /admin/config
Authorization: Bearer admin:1

{
  "max_enrollments_per_student": 8,
  "late_penalty_percent": 15.0
}
```

#### Freeze User Account (Admin)
```bash
POST /admin/users/4/freeze
Authorization: Bearer admin:1
```

#### Unfreeze User Account (Admin)
```bash
POST /admin/users/4/unfreeze
Authorization: Bearer admin:1
```

#### Create Database Backup (Admin)
```bash
POST /admin/backup
Authorization: Bearer admin:1

# Response
{
  "message": "Backup created successfully",
  "backup_path": "backup_20241209_140530.db"
}
```

#### Set Current Semester (Admin)
```bash
POST /admin/semester?semester=2024%20Fall
Authorization: Bearer admin:1
```

#### Toggle Enrollment (Admin)
```bash
POST /admin/enrollment/toggle?open=true
Authorization: Bearer admin:1
```

---

## 🔐 Authentication & Authorization

### How Authentication Works

1. **Login** to get an access token
2. **Include token** in  all subsequent requests:
   ```
   Authorization: Bearer <access_token>
   ```

### Role-Based Access Control (RBAC)

| Endpoint | Admin | Teacher | Student |
|----------|-------|---------|---------|
| Create Course | ✅ | ✅ | ❌ |
| Enroll in Course | ✅ | ❌ | ✅ |
| Record Grade | ✅ | ✅ | ❌ |
| View Own Grades | ✅ | ✅ | ✅ |
| Upload Material | ✅ | ✅ | ❌ |
| Download Material | ✅ | ✅ | ✅* |
| Create Assignment | ✅ | ✅ | ❌ |
| Submit Assignment | ✅ | ❌ | ✅ |
| System Admin | ✅ | ❌ | ❌ |

\* Students can only access materials from enrolled courses

---

## 🧪 Testing the API

### Using cURL

```bash
# 1. Login
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"student123"}' \
  | jq -r '.access_token')

# 2. Use token in requests
curl "http://localhost:8000/courses/" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python Requests

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/auth/login",
    json={"username": "student1", "password": "student123"}
)
token = response.json()["access_token"]

# Make authenticated request
headers = {"Authorization": f"Bearer {token}"}
courses = requests.get(
    "http://localhost:8000/courses/",
    headers=headers
).json()
```

### Using Interactive Docs

Visit http://localhost:8000/docs for a Swagger UI where you can:
1. Click "Authorize" button
2. Enter: `Bearer admin:1` (after logging in)
3. Test all endpoints interactively

---

## 📊 Database Schema

```sql
-- Core Tables
users (id, username, email, password_hash, role, is_active)
students (id, user_id, student_number, grade, major, status)
teachers (id, user_id, employee_number, department, title)
courses (id, course_code, name, teacher_id, capacity, semester)
enrollments (id, student_id, course_id, enrolled_at)
grades (id, student_id, course_id, score, letter_grade)
assignments (id, course_id, title, due_date, total_points)
submissions (id, assignment_id, student_id, score, feedback)
materials (id, course_id, title, file_path, file_type)
notifications (id, user_id, title, message, is_read)
```

---

## 🎯 Common Workflows

### Student Enrollment Workflow

```bash
# 1. Student logs in
POST /auth/login {"username": "student1", "password": "student123"}

# 2. Browse available courses
GET /courses/?semester=2024%20Spring&active_only=true

# 3. Check course capacity
GET /courses/1/capacity

# 4. Enroll in course
POST /enrollments/ {"student_id": 1, "course_id": 1}

# 5. View enrolled courses
GET /enrollments/student/1

# 6. Check for new assignments
GET /assignments/course/1

# 7. Check notifications
GET /notifications/?unread_only=true
```

### Teacher Grading Workflow

```bash
# 1. Teacher logs in
POST /auth/login {"username": "prof_zhang", "password": "teacher123"}

# 2. View teaching courses
GET /teachers/1/courses

# 3. Get course enrollments
GET /enrollments/course/1

# 4. Create assignment
POST /assignments/ {...}

# 5. View submissions
GET /assignments/1/submissions?ungraded_only=true

# 6. Grade submissions
PUT /assignments/submissions/1/grade {"score": 95, "feedback": "..."}

# 7. Record final grades
POST /grades/ {"student_id": 1, "course_id": 1, "score": 92.5}
```

---

## 🔧 Configuration

System configuration file: `system_config.json`

```json
{
  "current_semester": "2024 Spring",
  "enrollment_open": true,
  "max_enrollments_per_student": 10,
  "grade_release_enabled": true,
  "maintenance_mode": false,
  "allow_late_submissions": true,
  "late_penalty_percent": 10.0
}
```

Modify via API:
```bash
PUT /admin/config
```

---

## 📈 Success!

All **60+ API endpoints** are now fully functional across all 10 modules! 🎉

The system provides complete coverage for:
- ✅ User management & authentication
- ✅ Course lifecycle management
- ✅ Student/Teacher profiles
- ✅ Enrollment with smart validation
- ✅ Grade management with analytics
- ✅ File uploads (assignments & materials)
- ✅ Real-time notifications
- ✅ System administration

Explore the interactive documentation at `/docs` to see all available endpoints and try them out!

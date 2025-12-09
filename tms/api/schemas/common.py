"""
Common Pydantic schemas
"""
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum


# Enums
class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class StudentStatusEnum(str, Enum):
    ACTIVE = "active"
    ON_LEAVE = "on_leave"
    GRADUATED = "graduated"


# Base schemas
class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# User schemas
class UserBase(BaseSchema):
    username: str
    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    password: str
    role: UserRoleEnum


class UserResponse(UserBase):
    id: int
    role: UserRoleEnum
    is_active: bool
    created_at: datetime


class UserLogin(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    user: UserResponse


# Student schemas
class StudentBase(BaseSchema):
    student_number: str
    grade: Optional[str] = None
    major: Optional[str] = None
    phone: Optional[str] = None


class StudentCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    student_number: str
    grade: Optional[str] = None
    major: Optional[str] = None
    phone: Optional[str] = None


class StudentResponse(StudentBase):
    id: int
    user_id: int
    status: StudentStatusEnum
    enrollment_date: datetime


# Teacher schemas
class TeacherBase(BaseSchema):
    employee_number: str
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None


class TeacherCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    employee_number: str
    department: Optional[str] = None
    title: Optional[str] = None
    phone: Optional[str] = None
    office: Optional[str] = None


class TeacherResponse(TeacherBase):
    id: int
    user_id: int


# Course schemas
class CourseBase(BaseSchema):
    course_code: str
    name: str
    description: Optional[str] = None
    credits: float
    capacity: int
    schedule: Optional[str] = None
    location: Optional[str] = None
    semester: str


class CourseCreate(CourseBase):
    teacher_id: int


class CourseResponse(CourseBase):
    id: int
    teacher_id: int
    is_active: bool
    created_at: datetime


# Enrollment schemas
class EnrollmentCreate(BaseModel):
    student_id: int
    course_id: int


class EnrollmentResponse(BaseSchema):
    id: int
    student_id: int
    course_id: int
    enrolled_at: datetime


# Grade schemas
class GradeCreate(BaseModel):
    student_id: int
    course_id: int
    score: float = Field(..., ge=0, le=100)
    letter_grade: Optional[str] = None
    comments: Optional[str] = None


class GradeResponse(BaseSchema):
    id: int
    student_id: int
    course_id: int
    score: float
    letter_grade: Optional[str]
    comments: Optional[str]
    recorded_at: datetime
    updated_at: datetime


# Assignment schemas
class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    due_date: datetime
    total_points: float = 100.0


class AssignmentResponse(BaseSchema):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    due_date: datetime
    total_points: float
    created_at: datetime


# Submission schemas
class SubmissionResponse(BaseSchema):
    id: int
    assignment_id: int
    student_id: int
    content: Optional[str]
    file_path: Optional[str]
    submitted_at: datetime
    score: Optional[float]
    feedback: Optional[str]
    graded_at: Optional[datetime]


class GradeSubmissionRequest(BaseModel):
    score: float
    feedback: Optional[str] = None


# Material schemas
class MaterialResponse(BaseSchema):
    id: int
    course_id: int
    title: str
    description: Optional[str]
    file_path: str
    file_type: Optional[str]
    file_size: Optional[int]
    uploaded_at: datetime


# Notification schemas
class NotificationResponse(BaseSchema):
    id: int
    user_id: int
    title: str
    message: str
    notification_type: Optional[str]
    is_read: bool
    created_at: datetime


# System schemas
class SystemStats(BaseModel):
    total_users: int
    total_students: int
    total_teachers: int
    total_courses: int
    total_enrollments: int
    active_users: int
    current_semester: str

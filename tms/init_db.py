"""
Database Initialization Script
Create tables and seed initial data
"""
from sqlalchemy.orm import Session

from tms.infra.database import init_db, SessionLocal
from tms.infra.models import UserRole
from tms.application.services.auth_service import AuthService
from tms.application.services.student_service import StudentService
from tms.application.services.teacher_service import TeacherService
from tms.application.services.course_service import CourseService
from datetime import datetime, timedelta


def create_sample_data(db: Session):
    """Create sample data for testing"""
    
    auth_service = AuthService(db)
    student_service = StudentService(db)
    teacher_service = TeacherService(db)
    course_service = CourseService(db)
    
    print("Creating admin user...")
    admin = auth_service.create_user(
        username="admin",
        email="admin@tms.com",
        password="admin123",
        full_name="System Administrator",
        role=UserRole.ADMIN
    )
    
    print("Creating sample teachers...")
    teacher1 = teacher_service.create_teacher(
        username="prof_zhang",
        email="zhang@tms.com",
        password="teacher123",
        full_name="Zhang Wei",
        employee_number="T001",
        department="Computer Science",
        title="Professor",
        phone="123-456-7890",
        office="Room 301"
    )
    
    teacher2 = teacher_service.create_teacher(
        username="prof_li",
        email="li@tms.com",
        password="teacher123",
        full_name="Li Ming",
        employee_number="T002",
        department="Mathematics",
        title="Associate Professor",
        phone="123-456-7891",
        office="Room 302"
    )
    
    print("Creating sample students...")
    student1 = student_service.create_student(
        username="student1",
        email="student1@tms.com",
        password="student123",
        full_name="Wang Xiaoming",
        student_number="S2024001",
        grade="Sophomore",
        major="Computer Science",
        phone="123-456-7892"
    )
    
    student2 = student_service.create_student(
        username="student2",
        email="student2@tms.com",
        password="student123",
        full_name="Liu Xiaohua",
        student_number="S2024002",
        grade="Sophomore",
        major="Computer Science",
        phone="123-456-7893"
    )
    
    student3 = student_service.create_student(
        username="student3",
        email="student3@tms.com",
        password="student123",
        full_name="Chen Lei",
        student_number="S2024003",
        grade="Junior",
        major="Mathematics",
        phone="123-456-7894"
    )
    
    print("Creating sample courses...")
    if teacher1 and teacher2:
        course1 = course_service.create_course(
            course_code="CS101",
            name="Introduction to Programming",
            teacher_id=teacher1.id,
            credits=3.0,
            capacity=30,
            semester="2024 Spring",
            description="Learn the fundamentals of programming with Python",
            schedule="Mon/Wed 10:00-11:30",
            location="Building A, Room 101"
        )
        
        course2 = course_service.create_course(
            course_code="CS201",
            name="Data Structures and Algorithms",
            teacher_id=teacher1.id,
            credits=4.0,
            capacity=25,
            semester="2024 Spring",
            description="Advanced data structures and algorithm design",
            schedule="Tue/Thu 14:00-15:30",
            location="Building A, Room 102"
        )
        
        course3 = course_service.create_course(
            course_code="MATH101",
            name="Calculus I",
            teacher_id=teacher2.id,
            credits=4.0,
            capacity=40,
            semester="2024 Spring",
            description="Differential and integral calculus",
            schedule="Mon/Wed 14:00-15:30",
            location="Building B, Room 201"
        )
    
    print("Sample data created successfully!")
    print("\nDefault credentials:")
    print("Admin - username: admin, password: admin123")
    print("Teacher - username: prof_zhang, password: teacher123")
    print("Student - username: student1, password: student123")


def main():
    """Main initialization function"""
    print("Initializing database...")
    init_db()
    print("Database tables created!")
    
    print("\nCreating sample data...")
    db = SessionLocal()
    try:
        create_sample_data(db)
    finally:
        db.close()
    
    print("\n✓ Database initialization complete!")


if __name__ == "__main__":
    main()

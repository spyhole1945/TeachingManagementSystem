"""
Seed 20 test students
"""
from sqlalchemy.orm import Session
from tms.infra.database import SessionLocal
from tms.application.services.enrollment_service import EnrollmentService
from tms.application.services.student_service import StudentService
from tms.infra.models import Course
import random

def seed_students(db: Session):
    student_service = StudentService(db)
    enrollment_service = EnrollmentService(db)
    
    # Get a course to enroll them in (e.g., first course)
    course = db.query(Course).first()
    if not course:
        print("No courses found. Please run init_db first.")
        return

    print(f"Creating 20 students and enrolling them in {course.name} ({course.course_code})...")

    # Common Chinese surnames and names for variety
    surnames = ["Zhao", "Qian", "Sun", "Li", "Zhou", "Wu", "Zheng", "Wang", "Feng", "Chen"]
    names = ["Wei", "Fang", "Jie", "Min", "Liang", "Hui", "Jun", "Yang", "Lei", "Na"]

    for i in range(1, 21):
        num = f"{i:03d}"
        username = f"student_test_{num}"
        email = f"student_test_{num}@tms.com"
        password = "password123"
        
        # Generate random name
        full_name = f"{random.choice(surnames)} {random.choice(names)}"
        student_number = f"S2024TEST{num}"
        
        print(f"Processing {username} ({full_name})...")
        
        try:
            # Check if student already exists
            existing_student = student_service.get_student_by_number(student_number)
            if existing_student:
                student = existing_student
                print(f"  - Student exists ({student.id})")
            else:
                student = student_service.create_student(
                    username=username,
                    email=email,
                    password=password,
                    full_name=full_name,
                    student_number=student_number,
                    grade="Freshman" if i <= 10 else "Sophomore",
                    major="Computer Science",
                    phone=f"1380000{num}"
                )
                print(f"  - Created student ({student.id})")
            
            # Enroll in course
            result, error = enrollment_service.enroll_student(student.id, course.id)
            if error:
                print(f"  - Enrollment message: {error}")
            else:
                print(f"  - Enrolled in {course.course_code}")
            
        except Exception as e:
            print(f"  - Error: {str(e)}")

    print("\nDone! Processed 20 students.")

def main():
    db = SessionLocal()
    try:
        seed_students(db)
    finally:
        db.close()

if __name__ == "__main__":
    main()

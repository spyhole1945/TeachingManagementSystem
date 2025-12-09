"""
Student Service
Handles student profile management and operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from tms.infra.models import Student, StudentStatus, User, UserRole
from tms.infra.repositories.student_repository import StudentRepository
from tms.infra.repositories.user_repository import UserRepository
from tms.application.services.auth_service import AuthService


class StudentService:
    """Service for student management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.student_repo = StudentRepository(db)
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)
    
    def create_student(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        student_number: str,
        grade: Optional[str] = None,
        major: Optional[str] = None,
        phone: Optional[str] = None
    ) -> Optional[Student]:
        """
        Create a new student with user account
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            full_name: Student's full name
            student_number: Unique student number
            grade: Grade level
            major: Major/specialization
            phone: Contact phone
            
        Returns:
            Created student or None if failed
        """
        # Check if student number already exists
        if self.student_repo.student_number_exists(student_number):
            return None
        
        # Create user account
        user = self.auth_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.STUDENT
        )
        
        if not user:
            return None
        
        # Create student profile
        student = Student(
            user_id=user.id,
            student_number=student_number,
            grade=grade,
            major=major,
            phone=phone,
            status=StudentStatus.ACTIVE,
            enrollment_date=datetime.utcnow()
        )
        
        return self.student_repo.create(student)
    
    def get_student(self, student_id: int) -> Optional[Student]:
        """Get student by ID"""
        return self.student_repo.get_by_id(student_id)
    
    def get_student_by_number(self, student_number: str) -> Optional[Student]:
        """Get student by student number"""
        return self.student_repo.get_by_student_number(student_number)
    
    def get_student_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        return self.student_repo.get_by_user_id(user_id)
    
    def list_students(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[StudentStatus] = None
    ) -> List[Student]:
        """
        List students with optional status filter
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            status: Filter by student status
            
        Returns:
            List of students
        """
        if status:
            return self.student_repo.get_by_status(status, skip, limit)
        return self.student_repo.get_all(skip, limit)
    
    def update_student(
        self,
        student_id: int,
        grade: Optional[str] = None,
        major: Optional[str] = None,
        phone: Optional[str] = None,
        status: Optional[StudentStatus] = None
    ) -> Optional[Student]:
        """
        Update student information
        
        Args:
            student_id: Student ID
            grade: New grade level
            major: New major
            phone: New phone number
            status: New status
            
        Returns:
            Updated student or None
        """
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None
        
        if grade is not None:
            student.grade = grade
        if major is not None:
            student.major = major
        if phone is not None:
            student.phone = phone
        if status is not None:
            student.status = status
        
        self.db.commit()
        self.db.refresh(student)
        return student
    
    def change_status(
        self,
        student_id: int,
        new_status: StudentStatus
    ) -> Optional[Student]:
        """
        Change student status (active, on leave, graduated)
        
        Args:
            student_id: Student ID
            new_status: New status
            
        Returns:
            Updated student or None
        """
        return self.update_student(student_id, status=new_status)
    
    def delete_student(self, student_id: int) -> bool:
        """Delete a student (and associated user account)"""
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return False
        
        user_id = student.user_id
        
        # Delete student (cascade will handle related records)
        success = self.student_repo.delete(student_id)
        
        if success:
            # Delete user account
            self.user_repo.delete(user_id)
        
        return success
    
    def get_enrolled_courses(self, student_id: int):
        """Get all courses a student is enrolled in"""
        student = self.student_repo.get_with_enrollments(student_id)
        if not student:
            return []
        return [enrollment.course for enrollment in student.enrollments]

"""
Teacher Service
Handles teacher profile management and operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from tms.infra.models import Teacher, User, UserRole
from tms.infra.repositories.teacher_repository import TeacherRepository
from tms.infra.repositories.user_repository import UserRepository
from tms.application.services.auth_service import AuthService


class TeacherService:
    """Service for teacher management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.teacher_repo = TeacherRepository(db)
        self.user_repo = UserRepository(db)
        self.auth_service = AuthService(db)
    
    def create_teacher(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        employee_number: str,
        department: Optional[str] = None,
        title: Optional[str] = None,
        phone: Optional[str] = None,
        office: Optional[str] = None
    ) -> Optional[Teacher]:
        """
        Create a new teacher with user account
        
        Args:
            username: Unique username
            email: Email address
            password: Plain text password
            full_name: Teacher's full name
            employee_number: Unique employee number
            department: Department
            title: Academic title (Professor, etc.)
            phone: Contact phone
            office: Office location
            
        Returns:
            Created teacher or None if failed
        """
        # Check if employee number already exists
        if self.teacher_repo.employee_number_exists(employee_number):
            return None
        
        # Create user account
        user = self.auth_service.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=UserRole.TEACHER
        )
        
        if not user:
            return None
        
        # Create teacher profile
        teacher = Teacher(
            user_id=user.id,
            employee_number=employee_number,
            department=department,
            title=title,
            phone=phone,
            office=office
        )
        
        return self.teacher_repo.create(teacher)
    
    def get_teacher(self, teacher_id: int) -> Optional[Teacher]:
        """Get teacher by ID"""
        return self.teacher_repo.get_by_id(teacher_id)
    
    def get_teacher_by_employee_number(self, employee_number: str) -> Optional[Teacher]:
        """Get teacher by employee number"""
        return self.teacher_repo.get_by_employee_number(employee_number)
    
    def get_teacher_by_user_id(self, user_id: int) -> Optional[Teacher]:
        """Get teacher by user ID"""
        return self.teacher_repo.get_by_user_id(user_id)
    
    def list_teachers(
        self,
        skip: int = 0,
        limit: int = 100,
        department: Optional[str] = None
    ) -> List[Teacher]:
        """
        List teachers with optional department filter
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            department: Filter by department
            
        Returns:
            List of teachers
        """
        if department:
            return self.teacher_repo.get_by_department(department, skip, limit)
        return self.teacher_repo.get_all(skip, limit)
    
    def update_teacher(
        self,
        teacher_id: int,
        department: Optional[str] = None,
        title: Optional[str] = None,
        phone: Optional[str] = None,
        office: Optional[str] = None
    ) -> Optional[Teacher]:
        """
        Update teacher information
        
        Args:
            teacher_id: Teacher ID
            department: New department
            title: New academic title
            phone: New phone number
            office: New office location
            
        Returns:
            Updated teacher or None
        """
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return None
        
        if department is not None:
            teacher.department = department
        if title is not None:
            teacher.title = title
        if phone is not None:
            teacher.phone = phone
        if office is not None:
            teacher.office = office
        
        self.db.commit()
        self.db.refresh(teacher)
        return teacher
    
    def delete_teacher(self, teacher_id: int) -> bool:
        """Delete a teacher (and associated user account)"""
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return False
        
        user_id = teacher.user_id
        
        # Delete teacher (cascade will handle related records)
        success = self.teacher_repo.delete(teacher_id)
        
        if success:
            # Delete user account
            self.user_repo.delete(user_id)
        
        return success
    
    def get_teaching_courses(self, teacher_id: int):
        """Get all courses taught by a teacher"""
        teacher = self.teacher_repo.get_with_courses(teacher_id)
        if not teacher:
            return []
        return teacher.courses

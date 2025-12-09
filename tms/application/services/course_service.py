"""
Course Service
Handles course management operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session

from tms.infra.models import Course
from tms.infra.repositories.course_repository import CourseRepository
from tms.infra.repositories.teacher_repository import TeacherRepository


class CourseService:
    """Service for course management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.course_repo = CourseRepository(db)
        self.teacher_repo = TeacherRepository(db)
    
    def create_course(
        self,
        course_code: str,
        name: str,
        teacher_id: int,
        credits: float,
        capacity: int,
        semester: str,
        description: Optional[str] = None,
        schedule: Optional[str] = None,
        location: Optional[str] = None
    ) -> Optional[Course]:
        """
        Create a new course
        
        Args:
            course_code: Unique course code
            name: Course name
            teacher_id: ID of teaching teacher
            credits: Course credits
            capacity: Maximum student capacity
            semester: Semester (e.g., "2024 Spring")
            description: Course description
            schedule: Course schedule
            location: Class location
            
        Returns:
            Created course or None if failed
        """
        # Check if course code already exists
        if self.course_repo.course_code_exists(course_code):
            return None
        
        # Verify teacher exists
        teacher = self.teacher_repo.get_by_id(teacher_id)
        if not teacher:
            return None
        
        course = Course(
            course_code=course_code,
            name=name,
            teacher_id=teacher_id,
            credits=credits,
            capacity=capacity,
            semester=semester,
            description=description,
            schedule=schedule,
            location=location,
            is_active=True
        )
        
        return self.course_repo.create(course)
    
    def get_course(self, course_id: int) -> Optional[Course]:
        """Get course by ID"""
        return self.course_repo.get_by_id(course_id)
    
    def get_course_by_code(self, course_code: str) -> Optional[Course]:
        """Get course by course code"""
        return self.course_repo.get_by_course_code(course_code)
    
    def list_courses(
        self,
        skip: int = 0,
        limit: int = 100,
        teacher_id: Optional[int] = None,
        semester: Optional[str] = None,
        active_only: bool = False
    ) -> List[Course]:
        """
        List courses with optional filters
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            teacher_id: Filter by teacher
            semester: Filter by semester
            active_only: Only return active courses
            
        Returns:
            List of courses
        """
        if teacher_id:
            return self.course_repo.get_by_teacher(teacher_id, skip, limit)
        elif semester:
            return self.course_repo.get_by_semester(semester, skip, limit)
        elif active_only:
            return self.course_repo.get_active_courses(skip, limit)
        else:
            return self.course_repo.get_all(skip, limit)
    
    def search_courses(self, name: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """Search courses by name"""
        return self.course_repo.search_by_name(name, skip, limit)
    
    def update_course(
        self,
        course_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        credits: Optional[float] = None,
        capacity: Optional[int] = None,
        schedule: Optional[str] = None,
        location: Optional[str] = None,
        teacher_id: Optional[int] = None
    ) -> Optional[Course]:
        """
        Update course information
        
        Args:
            course_id: Course ID
            name: New course name
            description: New description
            credits: New credits
            capacity: New capacity
            schedule: New schedule
            location: New location
            teacher_id: New teacher ID
            
        Returns:
            Updated course or None
        """
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None
        
        if name is not None:
            course.name = name
        if description is not None:
            course.description = description
        if credits is not None:
            course.credits = credits
        if capacity is not None:
            course.capacity = capacity
        if schedule is not None:
            course.schedule = schedule
        if location is not None:
            course.location = location
        if teacher_id is not None:
            # Verify teacher exists
            teacher = self.teacher_repo.get_by_id(teacher_id)
            if teacher:
                course.teacher_id = teacher_id
        
        self.db.commit()
        self.db.refresh(course)
        return course
    
    def deactivate_course(self, course_id: int) -> bool:
        """Deactivate a course"""
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False
        
        course.is_active = False
        self.db.commit()
        return True
    
    def activate_course(self, course_id: int) -> bool:
        """Activate a course"""
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return False
        
        course.is_active = True
        self.db.commit()
        return True
    
    def delete_course(self, course_id: int) -> bool:
        """Delete a course"""
        return self.course_repo.delete(course_id)
    
    def get_enrolled_students(self, course_id: int):
        """Get all students enrolled in a course"""
        course = self.course_repo.get_with_enrollments(course_id)
        if not course:
            return []
        return [enrollment.student for enrollment in course.enrollments]
    
    def check_capacity(self, course_id: int) -> dict:
        """
        Check course capacity status
        
        Returns:
            Dict with capacity, current_enrollment, available_slots
        """
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None
        
        current_enrollment = self.course_repo.get_enrollment_count(course_id)
        
        return {
            "capacity": course.capacity,
            "current_enrollment": current_enrollment,
            "available_slots": course.capacity - current_enrollment,
            "is_full": current_enrollment >= course.capacity
        }

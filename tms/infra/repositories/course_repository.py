"""
Course Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Course


class CourseRepository(BaseRepository[Course]):
    """Repository for Course entity"""
    
    def __init__(self, db: Session):
        super().__init__(Course, db)
    
    def get_by_course_code(self, course_code: str) -> Optional[Course]:
        """Get course by course code"""
        return self.find_one_by(course_code=course_code)
    
    def get_by_teacher(self, teacher_id: int, skip: int = 0, limit: int = 100) -> List[Course]:
        """Get courses taught by a specific teacher"""
        return self.find_by(teacher_id=teacher_id)[skip:skip+limit]
    
    def get_by_semester(self, semester: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """Get courses for a specific semester"""
        return self.find_by(semester=semester)[skip:skip+limit]
    
    def get_active_courses(self, skip: int = 0, limit: int = 100) -> List[Course]:
        """Get all active courses"""
        return self.find_by(is_active=True)[skip:skip+limit]
    
    def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[Course]:
        """Search courses by name"""
        return (
            self.db.query(Course)
            .filter(Course.name.ilike(f"%{name}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_with_enrollments(self, course_id: int) -> Optional[Course]:
        """Get course with all enrolled students"""
        return (
            self.db.query(Course)
            .options(joinedload(Course.enrollments))
            .filter(Course.id == course_id)
            .first()
        )
    
    def course_code_exists(self, course_code: str) -> bool:
        """Check if course code already exists"""
        return self.exists(course_code=course_code)
    
    def get_enrollment_count(self, course_id: int) -> int:
        """Get current enrollment count for a course"""
        course = self.get_with_enrollments(course_id)
        return len(course.enrollments) if course else 0

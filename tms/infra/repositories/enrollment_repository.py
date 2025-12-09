"""
Enrollment Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Enrollment, Course


class EnrollmentRepository(BaseRepository[Enrollment]):
    """Repository for Enrollment entity"""
    
    def __init__(self, db: Session):
        super().__init__(Enrollment, db)
    
    def get_by_student_and_course(
        self, student_id: int, course_id: int
    ) -> Optional[Enrollment]:
        """Get enrollment by student and course"""
        return (
            self.db.query(Enrollment)
            .filter(
                and_(
                    Enrollment.student_id == student_id,
                    Enrollment.course_id == course_id
                )
            )
            .first()
        )
    
    def get_student_enrollments(
        self, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """Get all enrollments for a student"""
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.course))
            .filter(Enrollment.student_id == student_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_course_enrollments(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Enrollment]:
        """Get all enrollments for a course"""
        return (
            self.db.query(Enrollment)
            .options(joinedload(Enrollment.student))
            .filter(Enrollment.course_id == course_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def is_enrolled(self, student_id: int, course_id: int) -> bool:
        """Check if student is enrolled in course"""
        return self.get_by_student_and_course(student_id, course_id) is not None
    
    def get_student_course_schedules(self, student_id: int) -> List[str]:
        """Get all course schedules for a student"""
        enrollments = self.get_student_enrollments(student_id)
        return [e.course.schedule for e in enrollments if e.course.schedule]
    
    def count_enrollments_for_course(self, course_id: int) -> int:
        """Count total enrollments for a course"""
        return self.db.query(Enrollment).filter(Enrollment.course_id == course_id).count()

"""
Student Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Student, StudentStatus


class StudentRepository(BaseRepository[Student]):
    """Repository for Student entity"""
    
    def __init__(self, db: Session):
        super().__init__(Student, db)
    
    def get_by_student_number(self, student_number: str) -> Optional[Student]:
        """Get student by student number"""
        return self.find_one_by(student_number=student_number)
    
    def get_by_user_id(self, user_id: int) -> Optional[Student]:
        """Get student by user ID"""
        return self.find_one_by(user_id=user_id)
    
    def get_with_enrollments(self, student_id: int) -> Optional[Student]:
        """Get student with enrolled courses"""
        return (
            self.db.query(Student)
            .options(joinedload(Student.enrollments))
            .filter(Student.id == student_id)
            .first()
        )
    
    def get_by_status(self, status: StudentStatus, skip: int = 0, limit: int = 100) -> List[Student]:
        """Get students by status"""
        return self.find_by(status=status)[skip:skip+limit]
    
    def student_number_exists(self, student_number: str) -> bool:
        """Check if student number already exists"""
        return self.exists(student_number=student_number)

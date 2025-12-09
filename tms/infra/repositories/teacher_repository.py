"""
Teacher Repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Teacher


class TeacherRepository(BaseRepository[Teacher]):
    """Repository for Teacher entity"""
    
    def __init__(self, db: Session):
        super().__init__(Teacher, db)
    
    def get_by_employee_number(self, employee_number: str) -> Optional[Teacher]:
        """Get teacher by employee number"""
        return self.find_one_by(employee_number=employee_number)
    
    def get_by_user_id(self, user_id: int) -> Optional[Teacher]:
        """Get teacher by user ID"""
        return self.find_one_by(user_id=user_id)
    
    def get_with_courses(self, teacher_id: int) -> Optional[Teacher]:
        """Get teacher with all courses"""
        return (
            self.db.query(Teacher)
            .options(joinedload(Teacher.courses))
            .filter(Teacher.id == teacher_id)
            .first()
        )
    
    def get_by_department(self, department: str, skip: int = 0, limit: int = 100) -> List[Teacher]:
        """Get teachers by department"""
        return self.find_by(department=department)[skip:skip+limit]
    
    def employee_number_exists(self, employee_number: str) -> bool:
        """Check if employee number already exists"""
        return self.exists(employee_number=employee_number)

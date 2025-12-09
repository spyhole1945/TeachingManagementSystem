"""
Grade Repository
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Grade


class GradeRepository(BaseRepository[Grade]):
    """Repository for Grade entity"""
    
    def __init__(self, db: Session):
        super().__init__(Grade, db)
    
    def get_by_student_and_course(
        self, student_id: int, course_id: int
    ) -> Optional[Grade]:
        """Get grade for a student in a specific course"""
        return (
            self.db.query(Grade)
            .filter(
                and_(
                    Grade.student_id == student_id,
                    Grade.course_id == course_id
                )
            )
            .first()
        )
    
    def get_by_student(
        self, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a student"""
        return self.find_by(student_id=student_id)[skip:skip+limit]
    
    def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a course"""
        return self.find_by(course_id=course_id)[skip:skip+limit]
    
    def get_course_statistics(self, course_id: int) -> Dict[str, float]:
        """
        Get statistical information for grades in a course
        Returns: Dict with avg, max, min, pass_rate
        """
        grades = self.get_by_course(course_id)
        
        if not grades:
            return {
                "average": 0.0,
                "maximum": 0.0,
                "minimum": 0.0,
                "pass_rate": 0.0,
                "total_students": 0
            }
        
        scores = [g.score for g in grades]
        passing_threshold = 60.0
        passing_count = sum(1 for score in scores if score >= passing_threshold)
        
        return {
            "average": sum(scores) / len(scores),
            "maximum": max(scores),
            "minimum": min(scores),
            "pass_rate": (passing_count / len(scores)) * 100,
            "total_students": len(scores)
        }
    
    def calculate_student_gpa(self, student_id: int) -> float:
        """Calculate GPA for a student (simple average)"""
        grades = self.get_by_student(student_id)
        if not grades:
            return 0.0
        
        total_score = sum(g.score for g in grades)
        return total_score / len(grades)

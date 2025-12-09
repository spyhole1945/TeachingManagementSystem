"""
Grade Service
Handles grade management and statistics
"""
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from datetime import datetime

from tms.infra.models import Grade
from tms.infra.repositories.grade_repository import GradeRepository
from tms.infra.repositories.student_repository import StudentRepository
from tms.infra.repositories.course_repository import CourseRepository


class GradeService:
    """Service for grade management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.grade_repo = GradeRepository(db)
        self.student_repo = StudentRepository(db)
        self.course_repo = CourseRepository(db)
    
    def record_grade(
        self,
        student_id: int,
        course_id: int,
        score: float,
        letter_grade: Optional[str] = None,
        comments: Optional[str] = None
    ) -> Optional[Grade]:
        """
        Record or update a grade for a student in a course
        
        Args:
            student_id: Student ID
            course_id: Course ID
            score: Numeric score
            letter_grade: Letter grade (A, B, C, etc.)
            comments: Teacher comments
            
        Returns:
            Grade record or None if failed
        """
        # Verify student and course exist
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None
        
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None
        
        # Validate score
        if score < 0 or score > 100:
            return None
        
        # Check if grade already exists
        existing_grade = self.grade_repo.get_by_student_and_course(
            student_id, course_id
        )
        
        if existing_grade:
            # Update existing grade
            existing_grade.score = score
            existing_grade.letter_grade = letter_grade or self._calculate_letter_grade(score)
            existing_grade.comments = comments
            existing_grade.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_grade)
            return existing_grade
        else:
            # Create new grade
            grade = Grade(
                student_id=student_id,
                course_id=course_id,
                score=score,
                letter_grade=letter_grade or self._calculate_letter_grade(score),
                comments=comments,
                recorded_at=datetime.utcnow()
            )
            return self.grade_repo.create(grade)
    
    def _calculate_letter_grade(self, score: float) -> str:
        """Calculate letter grade from numeric score"""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"
    
    def get_grade(
        self,
        student_id: int,
        course_id: int
    ) -> Optional[Grade]:
        """Get grade for a student in a specific course"""
        return self.grade_repo.get_by_student_and_course(student_id, course_id)
    
    def get_student_grades(
        self,
        student_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a student"""
        return self.grade_repo.get_by_student(student_id, skip, limit)
    
    def get_course_grades(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Grade]:
        """Get all grades for a course"""
        return self.grade_repo.get_by_course(course_id, skip, limit)
    
    def get_course_statistics(self, course_id: int) -> Dict[str, float]:
        """
        Get statistical information for a course
        
        Returns:
            Dict with average, maximum, minimum, pass_rate, total_students
        """
        return self.grade_repo.get_course_statistics(course_id)
    
    def calculate_student_gpa(self, student_id: int) -> float:
        """Calculate GPA for a student"""
        return self.grade_repo.calculate_student_gpa(student_id)
    
    def update_grade(
        self,
        grade_id: int,
        score: Optional[float] = None,
        letter_grade: Optional[str] = None,
        comments: Optional[str] = None
    ) -> Optional[Grade]:
        """Update an existing grade"""
        grade = self.grade_repo.get_by_id(grade_id)
        if not grade:
            return None
        
        if score is not None:
            if score < 0 or score > 100:
                return None
            grade.score = score
            # Recalculate letter grade if not provided
            if letter_grade is None:
                grade.letter_grade = self._calculate_letter_grade(score)
        
        if letter_grade is not None:
            grade.letter_grade = letter_grade
        
        if comments is not None:
            grade.comments = comments
        
        grade.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(grade)
        return grade
    
    def delete_grade(self, grade_id: int) -> bool:
        """Delete a grade record"""
        return self.grade_repo.delete(grade_id)

"""
Assignment and Submission Repositories
"""
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from datetime import datetime

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Assignment, Submission


class AssignmentRepository(BaseRepository[Assignment]):
    """Repository for Assignment entity"""
    
    def __init__(self, db: Session):
        super().__init__(Assignment, db)
    
    def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Assignment]:
        """Get all assignments for a course"""
        return self.find_by(course_id=course_id)[skip:skip+limit]
    
    def get_with_submissions(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment with all submissions"""
        return (
            self.db.query(Assignment)
            .options(joinedload(Assignment.submissions))
            .filter(Assignment.id == assignment_id)
            .first()
        )
    
    def get_upcoming(
        self, course_id: int, days: int = 7
    ) -> List[Assignment]:
        """Get upcoming assignments for a course within specified days"""
        now = datetime.utcnow()
        return (
            self.db.query(Assignment)
            .filter(Assignment.course_id == course_id)
            .filter(Assignment.due_date >= now)
            .order_by(Assignment.due_date)
            .all()
        )


class SubmissionRepository(BaseRepository[Submission]):
    """Repository for Submission entity"""
    
    def __init__(self, db: Session):
        super().__init__(Submission, db)
    
    def get_by_student_and_assignment(
        self, student_id: int, assignment_id: int
    ) -> Optional[Submission]:
        """Get submission by student and assignment"""
        return (
            self.db.query(Submission)
            .filter(Submission.student_id == student_id)
            .filter(Submission.assignment_id == assignment_id)
            .first()
        )
    
    def get_by_assignment(
        self, assignment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get all submissions for an assignment"""
        return (
            self.db.query(Submission)
            .options(joinedload(Submission.student))
            .filter(Submission.assignment_id == assignment_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_student(
        self, student_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get all submissions by a student"""
        return (
            self.db.query(Submission)
            .options(joinedload(Submission.assignment))
            .filter(Submission.student_id == student_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def has_submitted(self, student_id: int, assignment_id: int) -> bool:
        """Check if student has submitted assignment"""
        return self.get_by_student_and_assignment(student_id, assignment_id) is not None
    
    def get_ungraded_submissions(
        self, assignment_id: int, skip: int = 0, limit: int = 100
    ) -> List[Submission]:
        """Get all ungraded submissions for an assignment"""
        return (
            self.db.query(Submission)
            .filter(Submission.assignment_id == assignment_id)
            .filter(Submission.score == None)
            .offset(skip)
            .limit(limit)
            .all()
        )

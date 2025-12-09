"""
Assignment Service
Handles assignments and student submissions
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime
import os

from tms.infra.models import Assignment, Submission
from tms.infra.repositories.assignment_repository import (
    AssignmentRepository,
    SubmissionRepository
)
from tms.infra.repositories.course_repository import CourseRepository
from tms.infra.repositories.student_repository import StudentRepository
from tms.application.services.notification_service import NotificationService
from tms.config import config


class AssignmentService:
    """Service for assignment and submission management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.assignment_repo = AssignmentRepository(db)
        self.submission_repo = SubmissionRepository(db)
        self.course_repo = CourseRepository(db)
        self.student_repo = StudentRepository(db)
        self.notification_service = NotificationService(db)
        self.upload_dir = config.UPLOAD_DIR
        
        os.makedirs(self.upload_dir, exist_ok=True)
    
    # Assignment Management
    
    def create_assignment(
        self,
        course_id: int,
        title: str,
        due_date: datetime,
        description: Optional[str] = None,
        total_points: float = 100.0
    ) -> Optional[Assignment]:
        """
        Create a new assignment
        
        Args:
            course_id: Course ID
            title: Assignment title
            due_date: Due date
            description: Assignment description
            total_points: Total points possible
            
        Returns:
            Created assignment or None
        """
        # Verify course exists
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None
        
        assignment = Assignment(
            course_id=course_id,
            title=title,
            description=description,
            due_date=due_date,
            total_points=total_points,
            created_at=datetime.utcnow()
        )
        
        created_assignment = self.assignment_repo.create(assignment)
        
        # Notify students about new assignment
        if created_assignment:
            # Get all enrolled students
            # Note: This might be expensive for large courses, consider async task in production
            from tms.infra.repositories.enrollment_repository import EnrollmentRepository
            enrollment_repo = EnrollmentRepository(self.db)
            enrollments = enrollment_repo.find_by(course_id=course_id)
            
            student_user_ids = []
            for enrollment in enrollments:
                student = self.student_repo.get_by_id(enrollment.student_id)
                if student:
                    student_user_ids.append(student.user_id)
            
            if student_user_ids:
                self.notification_service.notify_new_assignment(
                    created_assignment.id,
                    course.name,
                    created_assignment.title,
                    student_user_ids
                )
                
        return created_assignment
    
    def get_assignment(self, assignment_id: int) -> Optional[Assignment]:
        """Get assignment by ID"""
        return self.assignment_repo.get_by_id(assignment_id)
    
    def get_course_assignments(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Assignment]:
        """Get all assignments for a course"""
        return self.assignment_repo.get_by_course(course_id, skip, limit)
    
    def get_upcoming_assignments(
        self,
        course_id: int,
        days: int = 7
    ) -> List[Assignment]:
        """Get upcoming assignments for a course"""
        return self.assignment_repo.get_upcoming(course_id, days)
    
    def update_assignment(
        self,
        assignment_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        due_date: Optional[datetime] = None,
        total_points: Optional[float] = None
    ) -> Optional[Assignment]:
        """Update an assignment"""
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return None
        
        if title is not None:
            assignment.title = title
        if description is not None:
            assignment.description = description
        if due_date is not None:
            assignment.due_date = due_date
        if total_points is not None:
            assignment.total_points = total_points
        
        self.db.commit()
        self.db.refresh(assignment)
        return assignment
    
    def delete_assignment(self, assignment_id: int) -> bool:
        """Delete an assignment"""
        return self.assignment_repo.delete(assignment_id)
    
    # Submission Management
    
    async def submit_assignment(
        self,
        assignment_id: int,
        student_id: int,
        content: Optional[str] = None,
        file_content: Optional[bytes] = None,
        filename: Optional[str] = None
    ) -> Optional[Submission]:
        """
        Submit an assignment
        
        Args:
            assignment_id: Assignment ID
            student_id: Student ID
            content: Text submission content
            file_content: File binary content
            filename: Original filename
            
        Returns:
            Created/updated submission or None
        """
        # Verify assignment and student exist
        assignment = self.assignment_repo.get_by_id(assignment_id)
        if not assignment:
            return None
        
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None
        
        # Handle file upload if provided
        file_path = None
        if file_content and filename:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"assignment_{assignment_id}_student_{student_id}_{timestamp}_{filename}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            try:
                import aiofiles
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(file_content)
            except Exception:
                return None
        
        # Check if student has already submitted
        existing_submission = self.submission_repo.get_by_student_and_assignment(
            student_id, assignment_id
        )
        
        if existing_submission:
            # Update existing submission
            existing_submission.content = content
            if file_path:
                # Delete old file if exists
                if existing_submission.file_path and os.path.exists(existing_submission.file_path):
                    try:
                        os.remove(existing_submission.file_path)
                    except:
                        pass
                existing_submission.file_path = file_path
            existing_submission.submitted_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_submission)
            return existing_submission
        else:
            # Create new submission
            submission = Submission(
                assignment_id=assignment_id,
                student_id=student_id,
                content=content,
                file_path=file_path,
                submitted_at=datetime.utcnow()
            )
            return self.submission_repo.create(submission)
    
    def get_submission(
        self,
        student_id: int,
        assignment_id: int
    ) -> Optional[Submission]:
        """Get submission by student and assignment"""
        return self.submission_repo.get_by_student_and_assignment(
            student_id, assignment_id
        )
    
    def get_assignment_submissions(
        self,
        assignment_id: int,
        skip: int = 0,
        limit: int = 100,
        ungraded_only: bool = False
    ) -> List[Submission]:
        """Get all submissions for an assignment"""
        if ungraded_only:
            return self.submission_repo.get_ungraded_submissions(
                assignment_id, skip, limit
            )
        return self.submission_repo.get_by_assignment(assignment_id, skip, limit)
    
    def get_student_submissions(
        self,
        student_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Submission]:
        """Get all submissions by a student"""
        return self.submission_repo.get_by_student(student_id, skip, limit)
    
    def grade_submission(
        self,
        submission_id: int,
        score: float,
        feedback: Optional[str] = None
    ) -> Optional[Submission]:
        """
        Grade a submission
        
        Args:
            submission_id: Submission ID
            score: Score awarded
            feedback: Teacher feedback
            
        Returns:
            Updated submission or None
        """
        submission = self.submission_repo.get_by_id(submission_id)
        if not submission:
            return None
        
        # Validate score
        assignment = submission.assignment
        if score < 0 or score > assignment.total_points:
            return None
        
        submission.score = score
        submission.feedback = feedback
        submission.graded_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(submission)
        
        # Trigger notification
        student = self.student_repo.get_by_id(submission.student_id)
        if student:
            self.notification_service.notify_assignment_graded(
                student.user_id,
                assignment.title,
                score
            )
            
        return submission
    
    def is_late_submission(self, submission: Submission) -> bool:
        """Check if a submission was submitted late"""
        assignment = submission.assignment
        return submission.submitted_at > assignment.due_date


"""
Enrollment Service
Handles course enrollment, withdrawal, and conflict detection
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from tms.infra.models import Enrollment
from tms.infra.repositories.enrollment_repository import EnrollmentRepository
from tms.infra.repositories.course_repository import CourseRepository
from tms.infra.repositories.student_repository import StudentRepository


class EnrollmentService:
    """Service for enrollment management operations"""
    
    def __init__(self, db: Session):
        self.db = db
        self.enrollment_repo = EnrollmentRepository(db)
        self.course_repo = CourseRepository(db)
        self.student_repo = StudentRepository(db)
    
    def enroll_student(
        self,
        student_id: int,
        course_id: int
    ) -> tuple[Optional[Enrollment], Optional[str]]:
        """
        Enroll a student in a course with validation
        
        Args:
            student_id: Student ID
            course_id: Course ID
            
        Returns:
            Tuple of (Enrollment or None, error_message or None)
        """
        # Verify student exists
        student = self.student_repo.get_by_id(student_id)
        if not student:
            return None, "Student not found"
        
        # Verify course exists and is active
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None, "Course not found"
        
        if not course.is_active:
            return None, "Course is not active"
        
        # Check if already enrolled
        if self.enrollment_repo.is_enrolled(student_id, course_id):
            return None, "Student is already enrolled in this course"
        
        # Check course capacity
        current_enrollment = self.enrollment_repo.count_enrollments_for_course(course_id)
        if current_enrollment >= course.capacity:
            return None, "Course is at full capacity"
        
        # Check for schedule conflicts
        if course.schedule:
            conflict = self.check_schedule_conflict(student_id, course.schedule)
            if conflict:
                return None, f"Schedule conflict with course: {conflict.name}"
        
        # Create enrollment
        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
            enrolled_at=datetime.utcnow()
        )
        
        created_enrollment = self.enrollment_repo.create(enrollment)
        return created_enrollment, None
    
    def withdraw_student(
        self,
        student_id: int,
        course_id: int
    ) -> tuple[bool, Optional[str]]:
        """
        Withdraw a student from a course
        
        Args:
            student_id: Student ID
            course_id: Course ID
            
        Returns:
            Tuple of (success, error_message)
        """
        enrollment = self.enrollment_repo.get_by_student_and_course(
            student_id, course_id
        )
        
        if not enrollment:
            return False, "Enrollment not found"
        
        success = self.enrollment_repo.delete(enrollment.id)
        return success, None if success else "Failed to withdraw"
    
    def check_schedule_conflict(
        self,
        student_id: int,
        new_schedule: str
    ) -> Optional:
        """
        Check if a new course schedule conflicts with student's existing schedules
        
        Args:
            student_id: Student ID
            new_schedule: Schedule string to check
            
        Returns:
            Conflicting course if found, None otherwise
            
        Note:
            This is a simple string-based conflict detection.
            For production, you'd want more sophisticated time parsing.
        """
        # Get student's current course schedules
        schedules = self.enrollment_repo.get_student_course_schedules(student_id)
        
        # Simple conflict detection: if any existing schedule contains
        # the same day/time pattern as the new schedule
        # This is a simplified version - in reality you'd parse times properly
        for existing_schedule in schedules:
            if self._schedules_overlap(existing_schedule, new_schedule):
                # Find the conflicting course
                enrollments = self.enrollment_repo.get_student_enrollments(student_id)
                for enrollment in enrollments:
                    if enrollment.course.schedule == existing_schedule:
                        return enrollment.course
        
        return None
    
    def _schedules_overlap(self, schedule1: str, schedule2: str) -> bool:
        """
        Simple schedule overlap detection
        
        Example schedules: "Mon/Wed 10:00-11:30", "Tue/Thu 14:00-15:30"
        
        This is a simplified version that checks if they share common days.
        For production, you'd want proper time parsing and overlap detection.
        """
        if not schedule1 or not schedule2:
            return False
        
        # Extract days from schedules
        days1 = self._extract_days(schedule1)
        days2 = self._extract_days(schedule2)
        
        # Check if they share any common days
        common_days = days1.intersection(days2)
        
        if not common_days:
            return False
        
        # If they share days, there's a potential conflict
        # In a real system, you'd also check time ranges
        return True
    
    def _extract_days(self, schedule: str) -> set:
        """Extract days from schedule string"""
        days_map = {
            "mon": "Monday",
            "tue": "Tuesday", 
            "wed": "Wednesday",
            "thu": "Thursday",
            "fri": "Friday",
            "sat": "Saturday",
            "sun": "Sunday"
        }
        
        schedule_lower = schedule.lower()
        found_days = set()
        
        for abbr, full in days_map.items():
            if abbr in schedule_lower:
                found_days.add(full)
        
        return found_days
    
    def get_student_enrollments(
        self,
        student_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:
        """Get all enrollments for a student"""
        return self.enrollment_repo.get_student_enrollments(student_id, skip, limit)
    
    def get_course_enrollments(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[Enrollment]:
        """Get all enrollments for a course"""
        return self.enrollment_repo.get_course_enrollments(course_id, skip, limit)
    
    def get_enrollment_count(self, course_id: int) -> int:
        """Get total enrollment count for a course"""
        return self.enrollment_repo.count_enrollments_for_course(course_id)

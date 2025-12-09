"""
Notification Service
Handles system notifications and messages
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from tms.infra.models import Notification
from tms.infra.repositories.notification_repository import NotificationRepository
from tms.infra.repositories.user_repository import UserRepository


class NotificationService:
    """Service for notification management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.notification_repo = NotificationRepository(db)
        self.user_repo = UserRepository(db)
    
    def create_notification(
        self,
        user_id: int,
        title: str,
        message: str,
        notification_type: Optional[str] = None
    ) -> Optional[Notification]:
        """
        Create a notification for a user
        
        Args:
            user_id: User ID
            title: Notification title
            message: Notification message
            notification_type: Type (assignment, grade, enrollment, etc.)
            
        Returns:
            Created notification or None
        """
        # Verify user exists
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
        
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        return self.notification_repo.create(notification)
    
    def send_bulk_notification(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        notification_type: Optional[str] = None
    ) -> int:
        """
        Send notification to multiple users
        
        Args:
            user_ids: List of user IDs
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            
        Returns:
            Number of notifications sent
        """
        count = 0
        for user_id in user_ids:
            notification = self.create_notification(
                user_id, title, message, notification_type
            )
            if notification:
                count += 1
        return count
    
    def get_user_notifications(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for a user"""
        if unread_only:
            return self.notification_repo.get_unread(user_id, skip, limit)
        return self.notification_repo.get_by_user(user_id, skip, limit)
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark a notification as read"""
        return self.notification_repo.mark_as_read(notification_id)
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        return self.notification_repo.mark_all_as_read(user_id)
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread notifications"""
        return self.notification_repo.count_unread(user_id)
    
    def delete_notification(self, notification_id: int) -> bool:
        """Delete a notification"""
        return self.notification_repo.delete(notification_id)
    
    # Event-triggered notifications
    
    def notify_new_assignment(
        self,
        assignment_id: int,
        course_name: str,
        assignment_title: str,
        enrolled_student_ids: List[int]
    ) -> int:
        """Notify students about a new assignment"""
        title = f"New Assignment: {assignment_title}"
        message = f"A new assignment has been posted in {course_name}. Check it out!"
        
        return self.send_bulk_notification(
            enrolled_student_ids,
            title,
            message,
            "assignment"
        )
    
    def notify_grade_released(
        self,
        student_id: int,
        course_name: str,
        score: float
    ) -> Optional[Notification]:
        """Notify student about grade release"""
        title = f"成绩发布: {course_name}"
        message = f"您的 {course_name} 课程成绩已发布。分数: {score}"
        
        return self.create_notification(
            student_id,
            title,
            message,
            "grade"
        )
    
    def notify_enrollment_confirmation(
        self,
        student_id: int,
        course_name: str,
        success: bool
    ) -> Optional[Notification]:
        """Notify student about enrollment result"""
        if success:
            title = f"Successfully Enrolled: {course_name}"
            message = f"You have been successfully enrolled in {course_name}"
        else:
            title = f"Enrollment Failed: {course_name}"
            message = f"Failed to enroll in {course_name}. Please check course capacity and schedule."
        
        return self.create_notification(
            student_id,
            title,
            message,
            "enrollment"
        )
    
    def notify_assignment_graded(
        self,
        student_id: int,
        assignment_title: str,
        score: float
    ) -> Optional[Notification]:
        """Notify student that their assignment was graded"""
        title = f"Assignment Graded: {assignment_title}"
        message = f"Your submission for '{assignment_title}' has been graded. Score: {score}"
        
        return self.create_notification(
            student_id,
            title,
            message,
            "assignment"
        )

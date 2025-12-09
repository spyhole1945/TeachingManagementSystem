"""
Notification Repository
"""
from typing import List
from sqlalchemy.orm import Session

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Notification


class NotificationRepository(BaseRepository[Notification]):
    """Repository for Notification entity"""
    
    def __init__(self, db: Session):
        super().__init__(Notification, db)
    
    def get_by_user(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get all notifications for a user"""
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_unread(
        self, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Notification]:
        """Get unread notifications for a user"""
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .filter(Notification.is_read == False)
            .order_by(Notification.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def mark_as_read(self, notification_id: int) -> bool:
        """Mark notification as read"""
        notification = self.get_by_id(notification_id)
        if not notification:
            return False
        
        notification.is_read = True
        self.db.commit()
        return True
    
    def mark_all_as_read(self, user_id: int) -> int:
        """Mark all notifications as read for a user"""
        count = (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .filter(Notification.is_read == False)
            .update({"is_read": True})
        )
        self.db.commit()
        return count
    
    def count_unread(self, user_id: int) -> int:
        """Count unread notifications for a user"""
        return (
            self.db.query(Notification)
            .filter(Notification.user_id == user_id)
            .filter(Notification.is_read == False)
            .count()
        )

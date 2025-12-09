"""
User Repository
"""
from typing import Optional
from sqlalchemy.orm import Session

from tms.infra.base_repository import BaseRepository
from tms.infra.models import User, UserRole


class UserRepository(BaseRepository[User]):
    """Repository for User entity"""
    
    def __init__(self, db: Session):
        super().__init__(User, db)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.find_one_by(username=username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.find_one_by(email=email)
    
    def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100):
        """Get all users with specific role"""
        return self.find_by(role=role)[skip:skip+limit]
    
    def username_exists(self, username: str) -> bool:
        """Check if username already exists"""
        return self.exists(username=username)
    
    def email_exists(self, email: str) -> bool:
        """Check if email already exists"""
        return self.exists(email=email)

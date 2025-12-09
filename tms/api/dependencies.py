"""
API dependencies for dependency injection
Authentication and database session
"""
from typing import Generator, Optional
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from tms.infra.database import get_db
from tms.infra.models import User, UserRole
from tms.infra.repositories.user_repository import UserRepository


# Simple session-based auth using header
# In production, you'd use JWT or OAuth2
class AuthDependency:
    """Authentication dependency"""
    
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def get_current_user(
        self,
        authorization: Optional[str] = Header(None)
    ) -> User:
        """
        Get current authenticated user from authorization header
        
        Expected format: "Bearer <username>:<user_id>"
        This is a simplified auth for demo purposes
        """
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )
        
        try:
            # Simple format: "Bearer username:user_id"
            if not authorization.startswith("Bearer "):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            token = authorization.replace("Bearer ", "")
            username, user_id = token.split(":")
            user_id = int(user_id)
            
            user = self.user_repo.get_by_id(user_id)
            
            if not user or user.username != username:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials"
                )
            
            if not user.is_active:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User account is inactive"
                )
            
            return user
            
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )


# Dependency instances
def get_current_user(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user"""
    auth = AuthDependency(db)
    return auth.get_current_user(authorization)


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


def require_teacher(current_user: User = Depends(get_current_user)) -> User:
    """Require teacher role (or admin)"""
    if current_user.role not in [UserRole.TEACHER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Teacher privileges required"
        )
    return current_user


def require_student(current_user: User = Depends(get_current_user)) -> User:
    """Require student role (or admin)"""
    if current_user.role not in [UserRole.STUDENT, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student privileges required"
        )
    return current_user

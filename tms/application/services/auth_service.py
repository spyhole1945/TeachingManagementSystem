"""
Authentication Service
Handles user authentication, password management, and session control
"""
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from tms.infra.models import User, UserRole
from tms.infra.repositories.user_repository import UserRepository


# Password hashing context - using pbkdf2_sha256 for better compatibility
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class AuthService:
    """Authentication service for user login/logout and password management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """
        Authenticate user with username and password
        
        Args:
            username: User's username
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.user_repo.get_by_username(username)
        
        if not user:
            return None
        
        if not user.is_active:
            return None
        
        if not self.verify_password(password, user.password_hash):
            return None
        
        return user
    
    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        full_name: str,
        role: UserRole
    ) -> Optional[User]:
        """
        Create a new user
        
        Args:
            username: Unique username
            email: Unique email
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (admin/teacher/student)
            
        Returns:
            Created user or None if username/email exists
        """
        # Check if username or email already exists
        if self.user_repo.username_exists(username):
            return None
        
        if self.user_repo.email_exists(email):
            return None
        
        # Create user with hashed password
        user = User(
            username=username,
            email=email,
            password_hash=self.hash_password(password),
            full_name=full_name,
            role=role,
            is_active=True
        )
        
        return self.user_repo.create(user)
    
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str
    ) -> bool:
        """
        Change user password
        
        Args:
            user_id: User ID
            old_password: Current password
            new_password: New password
            
        Returns:
            True if successful, False otherwise
        """
        user = self.user_repo.get_by_id(user_id)
        
        if not user:
            return False
        
        # Verify old password
        if not self.verify_password(old_password, user.password_hash):
            return False
        
        # Update password
        user.password_hash = self.hash_password(new_password)
        self.db.commit()
        return True
    
    def check_permission(self, user: User, required_role: UserRole) -> bool:
        """
        Check if user has required permission (simple RBAC)
        Admin has all permissions
        
        Args:
            user: User object
            required_role: Required role
            
        Returns:
            True if user has permission
        """
        if user.role == UserRole.ADMIN:
            return True
        
        return user.role == required_role
    
    def update_user(
        self,
        user_id: int,
        username: Optional[str] = None,
        email: Optional[str] = None,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> Optional[User]:
        """
        Update user information
        
        Args:
            user_id: User ID to update
            username: New username (optional)
            email: New email (optional)
            full_name: New full name (optional)
            password: New password (optional, will be hashed)
            role: New role (optional)
            is_active: New active status (optional)
            
        Returns:
            Updated User object or None if failed/duplicate
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None
            
        updates = {}
        
        # Check uniqueness if username/email changes
        if username and username != user.username:
            if self.user_repo.username_exists(username):
                return None
            updates["username"] = username
            
        if email and email != user.email:
            if self.user_repo.email_exists(email):
                return None
            updates["email"] = email
            
        if full_name:
            updates["full_name"] = full_name
            
        if password:
            updates["password_hash"] = self.hash_password(password)
            
        if role:
            updates["role"] = role
            
        if is_active is not None:
            updates["is_active"] = is_active
            
        if not updates:
            return user
            
        return self.user_repo.update(user_id, updates)

    def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def activate_user(self, user_id: int) -> bool:
        """Activate a user account"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        return True

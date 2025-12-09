"""
System Administration Service
Handles system configuration and administrative tasks
"""
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from datetime import datetime
import json
import os

from tms.infra.models import User, UserRole
from tms.infra.repositories.user_repository import UserRepository
from tms.infra.database import engine, Base
from tms.config import config


class SystemService:
    """Service for system administration"""
    
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.config_file = "system_config.json"
    
    # User Management
    
    def freeze_user(self, user_id: int) -> bool:
        """
        Freeze (deactivate) a user account
        
        Args:
            user_id: User ID to freeze
            
        Returns:
            True if successful
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        self.db.commit()
        return True
    
    def unfreeze_user(self, user_id: int) -> bool:
        """
        Unfreeze (activate) a user account
        
        Args:
            user_id: User ID to unfreeze
            
        Returns:
            True if successful
        """
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return False
        
        user.is_active = True
        self.db.commit()
        return True
    
    def list_all_users(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        active_only: bool = False
    ) -> List[User]:
        """List all users with optional filters"""
        if role:
            users = self.user_repo.get_by_role(role, skip, limit)
        else:
            users = self.user_repo.get_all(skip, limit)
        
        if active_only:
            users = [u for u in users if u.is_active]
        
        return users
    
    # System Configuration
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get system configuration
        
        Returns:
            Configuration dictionary
        """
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default system configuration"""
        return {
            "current_semester": "2024 Spring",
            "enrollment_open": True,
            "max_enrollments_per_student": 10,
            "grade_release_enabled": True,
            "maintenance_mode": False,
            "allow_late_submissions": True,
            "late_penalty_percent": 10.0
        }
    
    def update_config(self, config_updates: Dict[str, Any]) -> bool:
        """
        Update system configuration
        
        Args:
            config_updates: Dictionary of config updates
            
        Returns:
            True if successful
        """
        current_config = self.get_config()
        current_config.update(config_updates)
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(current_config, f, indent=2)
            return True
        except Exception:
            return False
    
    def set_current_semester(self, semester: str) -> bool:
        """Set the current semester"""
        return self.update_config({"current_semester": semester})
    
    def toggle_enrollment(self, open: bool) -> bool:
        """Enable or disable enrollment"""
        return self.update_config({"enrollment_open": open})
    
    # Database Backup and Restore
    
    def backup_database(self, backup_path: Optional[str] = None) -> str:
        """
        Create a database backup
        
        Args:
            backup_path: Optional custom backup path
            
        Returns:
            Path to backup file
        """
        if not backup_path:
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_{timestamp}.db"
        
        # For SQLite, simply copy the database file
        import shutil
        
        if "sqlite" in config.DATABASE_URL:
            db_path = config.DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            return backup_path
        else:
            # For other databases, you'd use database-specific backup commands
            return "Backup not implemented for non-SQLite databases"
    
    def restore_database(self, backup_path: str) -> bool:
        """
        Restore database from backup
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if successful
        """
        if not os.path.exists(backup_path):
            return False
        
        import shutil
        
        if "sqlite" in config.DATABASE_URL:
            db_path = config.DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(backup_path, db_path)
            return True
        else:
            return False
    
    # Statistics and Reporting
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get system-wide statistics"""
        from tms.infra.repositories.student_repository import StudentRepository
        from tms.infra.repositories.teacher_repository import TeacherRepository
        from tms.infra.repositories.course_repository import CourseRepository
        from tms.infra.repositories.enrollment_repository import EnrollmentRepository
        
        student_repo = StudentRepository(self.db)
        teacher_repo = TeacherRepository(self.db)
        course_repo = CourseRepository(self.db)
        enrollment_repo = EnrollmentRepository(self.db)
        
        return {
            "total_users": self.user_repo.count(),
            "total_students": student_repo.count(),
            "total_teachers": teacher_repo.count(),
            "total_courses": course_repo.count(),
            "total_enrollments": enrollment_repo.count(),
            "active_users": len([u for u in self.user_repo.get_all() if u.is_active]),
            "current_semester": self.get_config().get("current_semester", "N/A")
        }
    
    # Audit Logging
    
    def log_action(
        self,
        user_id: int,
        action: str,
        details: Optional[str] = None
    ) -> bool:
        """
        Log an administrative action
        
        Args:
            user_id: User performing the action
            action: Action description
            details: Additional details
            
        Returns:
            True if successful
        """
        # In a real system, you'd write to a dedicated audit log table
        # For now, we'll just write to a file
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "action": action,
            "details": details
        }
        
        try:
            with open("audit_log.txt", "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            return True
        except Exception:
            return False

"""
Material Service
Handles course materials and file management
"""
from typing import Optional, List
from sqlalchemy.orm import Session
import os
import aiofiles
from datetime import datetime

from tms.infra.models import Material
from tms.infra.repositories.material_repository import MaterialRepository
from tms.infra.repositories.course_repository import CourseRepository
from tms.infra.repositories.enrollment_repository import EnrollmentRepository
from tms.config import config


class MaterialService:
    """Service for course material management"""
    
    def __init__(self, db: Session):
        self.db = db
        self.material_repo = MaterialRepository(db)
        self.course_repo = CourseRepository(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.upload_dir = config.UPLOAD_DIR
        
        # Ensure upload directory exists
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload_material(
        self,
        course_id: int,
        title: str,
        file_content: bytes,
        filename: str,
        description: Optional[str] = None
    ) -> Optional[Material]:
        """
        Upload a course material
        
        Args:
            course_id: Course ID
            title: Material title
            file_content: File binary content
            filename: Original filename
            description: Material description
            
        Returns:
            Created material record or None
        """
        # Verify course exists
        course = self.course_repo.get_by_id(course_id)
        if not course:
            return None
        
        # Check file size
        if len(file_content) > config.MAX_UPLOAD_SIZE:
            return None
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        _, ext = os.path.splitext(filename)
        unique_filename = f"course_{course_id}_{timestamp}_{filename}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        # Save file
        try:
            async with aiofiles.open(file_path, 'wb') as f:
                await f.write(file_content)
        except Exception as e:
            return None
        
        # Determine file type
        file_type = self._get_file_type(ext)
        
        # Create material record
        material = Material(
            course_id=course_id,
            title=title,
            description=description,
            file_path=file_path,
            file_type=file_type,
            file_size=len(file_content),
            uploaded_at=datetime.utcnow()
        )
        
        return self.material_repo.create(material)
    
    def _get_file_type(self, extension: str) -> str:
        """Determine file type from extension"""
        extension = extension.lower()
        
        if extension in ['.pdf']:
            return 'pdf'
        elif extension in ['.doc', '.docx']:
            return 'document'
        elif extension in ['.ppt', '.pptx']:
            return 'presentation'
        elif extension in ['.xls', '.xlsx']:
            return 'spreadsheet'
        elif extension in ['.mp4', '.avi', '.mov']:
            return 'video'
        elif extension in ['.mp3', '.wav']:
            return 'audio'
        elif extension in ['.jpg', '.jpeg', '.png', '.gif']:
            return 'image'
        elif extension in ['.zip', '.rar']:
            return 'archive'
        else:
            return 'other'
    
    def get_material(self, material_id: int) -> Optional[Material]:
        """Get material by ID"""
        return self.material_repo.get_by_id(material_id)
    
    def get_course_materials(
        self,
        course_id: int,
        skip: int = 0,
        limit: int = 100,
        file_type: Optional[str] = None
    ) -> List[Material]:
        """Get all materials for a course"""
        if file_type:
            return self.material_repo.get_by_type(course_id, file_type, skip, limit)
        return self.material_repo.get_by_course(course_id, skip, limit)
    
    def search_materials(
        self,
        course_id: int,
        title: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """Search materials by title"""
        return self.material_repo.search_by_title(course_id, title, skip, limit)
    
    def check_access_permission(
        self,
        student_id: int,
        material_id: int
    ) -> bool:
        """
        Check if a student has permission to access a material
        (student must be enrolled in the course)
        
        Args:
            student_id: Student ID
            material_id: Material ID
            
        Returns:
            True if student has access
        """
        material = self.material_repo.get_by_id(material_id)
        if not material:
            return False
        
        # Check if student is enrolled in the course
        return self.enrollment_repo.is_enrolled(student_id, material.course_id)
    
    async def delete_material(self, material_id: int) -> bool:
        """
        Delete a material and its associated file
        
        Args:
            material_id: Material ID
            
        Returns:
            True if successful
        """
        material = self.material_repo.get_by_id(material_id)
        if not material:
            return False
        
        # Delete file from filesystem
        try:
            if os.path.exists(material.file_path):
                os.remove(material.file_path)
        except Exception:
            pass  # Continue even if file deletion fails
        
        # Delete database record
        return self.material_repo.delete(material_id)
    
    def get_file_path(self, material_id: int) -> Optional[str]:
        """Get the file path for a material"""
        material = self.material_repo.get_by_id(material_id)
        if not material:
            return None
        return material.file_path

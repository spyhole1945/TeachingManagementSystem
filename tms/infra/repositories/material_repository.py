"""
Material Repository
"""
from typing import List
from sqlalchemy.orm import Session

from tms.infra.base_repository import BaseRepository
from tms.infra.models import Material


class MaterialRepository(BaseRepository[Material]):
    """Repository for Material entity"""
    
    def __init__(self, db: Session):
        super().__init__(Material, db)
    
    def get_by_course(
        self, course_id: int, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """Get all materials for a course"""
        return self.find_by(course_id=course_id)[skip:skip+limit]
    
    def get_by_type(
        self, course_id: int, file_type: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """Get materials by file type for a course"""
        return (
            self.db.query(Material)
            .filter(Material.course_id == course_id)
            .filter(Material.file_type == file_type)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def search_by_title(
        self, course_id: int, title: str, skip: int = 0, limit: int = 100
    ) -> List[Material]:
        """Search materials by title within a course"""
        return (
            self.db.query(Material)
            .filter(Material.course_id == course_id)
            .filter(Material.title.ilike(f"%{title}%"))
            .offset(skip)
            .limit(limit)
            .all()
        )

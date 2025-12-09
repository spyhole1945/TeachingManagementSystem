"""
Base Repository Pattern Implementation
Generic CRUD operations for all entities
"""
from typing import Generic, TypeVar, Type, List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from tms.infra.database import Base

# Generic type for model
ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """
    Base repository with common CRUD operations
    All specific repositories should inherit from this
    """
    
    def __init__(self, model: Type[ModelType], db: Session):
        """
        Initialize repository with model class and database session
        
        Args:
            model: SQLAlchemy model class
            db: Database session
        """
        self.model = model
        self.db = db
    
    def create(self, obj: ModelType) -> ModelType:
        """
        Create a new record
        
        Args:
            obj: Model instance to create
            
        Returns:
            Created model instance
        """
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def get_by_id(self, id: int) -> Optional[ModelType]:
        """
        Get record by ID
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return self.db.query(self.model).filter(self.model.id == id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """
        Get all records with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of model instances
        """
        return self.db.query(self.model).offset(skip).limit(limit).all()
    
    def update(self, id: int, data: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update a record
        
        Args:
            id: Record ID
            data: Dictionary of fields to update
            
        Returns:
            Updated model instance or None
        """
        obj = self.get_by_id(id)
        if not obj:
            return None
        
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        
        self.db.commit()
        self.db.refresh(obj)
        return obj
    
    def delete(self, id: int) -> bool:
        """
        Delete a record
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        obj = self.get_by_id(id)
        if not obj:
            return False
        
        self.db.delete(obj)
        self.db.commit()
        return True
    
    def count(self) -> int:
        """
        Count total records
        
        Returns:
            Total number of records
        """
        return self.db.query(self.model).count()
    
    def find_by(self, **filters) -> List[ModelType]:
        """
        Find records by arbitrary filters
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            List of matching model instances
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.all()
    
    def find_one_by(self, **filters) -> Optional[ModelType]:
        """
        Find single record by filters
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            Model instance or None
        """
        query = self.db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first()
    
    def exists(self, **filters) -> bool:
        """
        Check if record exists with given filters
        
        Args:
            **filters: Field-value pairs to filter by
            
        Returns:
            True if exists, False otherwise
        """
        return self.find_one_by(**filters) is not None

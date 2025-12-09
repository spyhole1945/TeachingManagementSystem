"""
Teacher routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from tms.infra.database import get_db
from tms.infra.models import User
from tms.api.dependencies import get_current_user, require_admin
from tms.api.schemas.common import TeacherCreate, TeacherResponse
from tms.application.services.teacher_service import TeacherService

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post("/", response_model=TeacherResponse, dependencies=[Depends(require_admin)])
def create_teacher(teacher: TeacherCreate, db: Session = Depends(get_db)):
    """Create a new teacher (Admins only)"""
    teacher_service = TeacherService(db)
    
    created_teacher = teacher_service.create_teacher(
        username=teacher.username,
        email=teacher.email,
        password=teacher.password,
        full_name=teacher.full_name,
        employee_number=teacher.employee_number,
        department=teacher.department,
        title=teacher.title,
        phone=teacher.phone,
        office=teacher.office
    )
    
    if not created_teacher:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee number or username/email already exists"
        )
    
    return TeacherResponse.model_validate(created_teacher)


@router.get("/", response_model=List[TeacherResponse])
def list_teachers(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    department: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all teachers"""
    teacher_service = TeacherService(db)
    teachers = teacher_service.list_teachers(skip=skip, limit=limit, department=department)
    return [TeacherResponse.model_validate(t) for t in teachers]


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get teacher by ID"""
    teacher_service = TeacherService(db)
    teacher = teacher_service.get_teacher(teacher_id)
    
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return TeacherResponse.model_validate(teacher)


@router.get("/{teacher_id}/courses")
def get_teacher_courses(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all courses taught by a teacher"""
    teacher_service = TeacherService(db)
    courses = teacher_service.get_teaching_courses(teacher_id)
    
    from tms.api.schemas.common import CourseResponse
    return [CourseResponse.model_validate(c) for c in courses]


@router.delete("/{teacher_id}", dependencies=[Depends(require_admin)])
def delete_teacher(teacher_id: int, db: Session = Depends(get_db)):
    """Delete a teacher (Admins only)"""
    teacher_service = TeacherService(db)
    success = teacher_service.delete_teacher(teacher_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher not found"
        )
    
    return {"message": "Teacher deleted successfully"}

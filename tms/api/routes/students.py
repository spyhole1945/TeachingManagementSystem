"""
Student routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from tms.infra.database import get_db
from tms.infra.models import User
from tms.api.dependencies import get_current_user, require_admin
from tms.api.schemas.common import StudentCreate, StudentResponse
from tms.application.services.student_service import StudentService

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, dependencies=[Depends(require_admin)])
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student (Admins only)"""
    student_service = StudentService(db)
    
    created_student = student_service.create_student(
        username=student.username,
        email=student.email,
        password=student.password,
        full_name=student.full_name,
        student_number=student.student_number,
        grade=student.grade,
        major=student.major,
        phone=student.phone
    )
    
    if not created_student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student number or username/email already exists"
        )
    
    return StudentResponse.model_validate(created_student)


@router.get("/", response_model=List[StudentResponse])
def list_students(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all students"""
    student_service = StudentService(db)
    students = student_service.list_students(skip=skip, limit=limit)
    return [StudentResponse.model_validate(s) for s in students]


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get student by ID"""
    student_service = StudentService(db)
    student = student_service.get_student(student_id)
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    return StudentResponse.model_validate(student)

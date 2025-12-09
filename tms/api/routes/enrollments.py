"""
Enrollment routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from tms.infra.database import get_db
from tms.infra.models import User
from tms.api.dependencies import get_current_user
from tms.api.schemas.common import EnrollmentCreate, EnrollmentResponse
from tms.application.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("/", response_model=EnrollmentResponse)
def enroll_in_course(
    enrollment: EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Enroll a student in a course"""
    enrollment_service = EnrollmentService(db)
    
    created_enrollment, error = enrollment_service.enroll_student(
        enrollment.student_id,
        enrollment.course_id
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return EnrollmentResponse.model_validate(created_enrollment)


@router.delete("/{enrollment_id}")
def withdraw_from_course(
    enrollment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Withdraw from a course"""
    from tms.infra.repositories.enrollment_repository import EnrollmentRepository
    
    enrollment_repo = EnrollmentRepository(db)
    enrollment = enrollment_repo.get_by_id(enrollment_id)
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found"
        )
    
    enrollment_service = EnrollmentService(db)
    success, error = enrollment_service.withdraw_student(
        enrollment.student_id,
        enrollment.course_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error or "Failed to withdraw"
        )
    
    return {"message": "Successfully withdrawn from course"}


@router.get("/student/{student_id}", response_model=List[EnrollmentResponse])
def get_student_enrollments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all enrollments for a student"""
    enrollment_service = EnrollmentService(db)
    enrollments = enrollment_service.get_student_enrollments(student_id)
    return [EnrollmentResponse.model_validate(e) for e in enrollments]

"""
Assignment and Submission routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from tms.infra.database import get_db
from tms.infra.models import User, UserRole
from tms.api.dependencies import get_current_user, require_teacher
from tms.api.schemas.common import AssignmentCreate, AssignmentResponse, SubmissionResponse, GradeSubmissionRequest
from tms.application.services.assignment_service import AssignmentService

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("/", response_model=AssignmentResponse, dependencies=[Depends(require_teacher)])
def create_assignment(
    assignment: AssignmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new assignment (Teachers and Admins only)"""
    assignment_service = AssignmentService(db)
    
    created_assignment = assignment_service.create_assignment(
        course_id=assignment.course_id,
        title=assignment.title,
        due_date=assignment.due_date,
        description=assignment.description,
        total_points=assignment.total_points
    )
    
    if not created_assignment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course not found"
        )
    
    return AssignmentResponse.model_validate(created_assignment)


@router.get("/course/{course_id}", response_model=List[AssignmentResponse])
def get_course_assignments(
    course_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all assignments for a course"""
    assignment_service = AssignmentService(db)
    assignments = assignment_service.get_course_assignments(course_id, skip, limit)
    return [AssignmentResponse.model_validate(a) for a in assignments]


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get assignment by ID"""
    assignment_service = AssignmentService(db)
    assignment = assignment_service.get_assignment(assignment_id)
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return AssignmentResponse.model_validate(assignment)


@router.post("/{assignment_id}/submit")
async def submit_assignment(
    assignment_id: int,
    student_id: int = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Submit an assignment"""
    assignment_service = AssignmentService(db)
    
    # Read file if provided
    file_content = None
    filename = None
    if file:
        file_content = await file.read()
        filename = file.filename
    
    submission = await assignment_service.submit_assignment(
        assignment_id=assignment_id,
        student_id=student_id,
        content=content,
        file_content=file_content,
        filename=filename
    )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit assignment"
        )
    
    return SubmissionResponse.model_validate(submission)


@router.get("/{assignment_id}/submissions", response_model=List[SubmissionResponse])
def get_assignment_submissions(
    assignment_id: int,
    ungraded_only: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_teacher)
):
    """Get all submissions for an assignment (Teachers and Admins only)"""
    assignment_service = AssignmentService(db)
    submissions = assignment_service.get_assignment_submissions(
        assignment_id, skip, limit, ungraded_only
    )
    return [SubmissionResponse.model_validate(s) for s in submissions]


@router.put("/submissions/{submission_id}/grade", dependencies=[Depends(require_teacher)])
def grade_submission(
    submission_id: int,
    grade_data: GradeSubmissionRequest,
    db: Session = Depends(get_db)
):
    """Grade a submission (Teachers and Admins only)"""
    assignment_service = AssignmentService(db)
    
    submission = assignment_service.grade_submission(
        submission_id=submission_id,
        score=grade_data.score,
        feedback=grade_data.feedback
    )
    
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Submission not found or invalid score"
        )
    
    return SubmissionResponse.model_validate(submission)


@router.delete("/{assignment_id}", dependencies=[Depends(require_teacher)])
def delete_assignment(assignment_id: int, db: Session = Depends(get_db)):
    """Delete an assignment (Teachers and Admins only)"""
    assignment_service = AssignmentService(db)
    success = assignment_service.delete_assignment(assignment_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    return {"message": "Assignment deleted successfully"}

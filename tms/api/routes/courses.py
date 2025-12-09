"""
Course routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from tms.infra.database import get_db
from tms.infra.models import User
from tms.api.dependencies import get_current_user, require_teacher, require_admin
from tms.api.schemas.common import CourseCreate, CourseResponse
from tms.application.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("/", response_model=CourseResponse, dependencies=[Depends(require_teacher)])
def create_course(course: CourseCreate, db: Session = Depends(get_db)):
    """Create a new course (Teachers and Admins only)"""
    course_service = CourseService(db)
    
    created_course = course_service.create_course(
        course_code=course.course_code,
        name=course.name,
        teacher_id=course.teacher_id,
        credits=course.credits,
        capacity=course.capacity,
        semester=course.semester,
        description=course.description,
        schedule=course.schedule,
        location=course.location
    )
    
    if not created_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course code already exists or teacher not found"
        )
    
    return CourseResponse.model_validate(created_course)


@router.get("/", response_model=List[CourseResponse])
def list_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    teacher_id: Optional[int] = None,
    semester: Optional[str] = None,
    active_only: bool = False,
    db: Session = Depends(get_db)
):
    """List all courses with optional filters"""
    course_service = CourseService(db)
    
    courses = course_service.list_courses(
        skip=skip,
        limit=limit,
        teacher_id=teacher_id,
        semester=semester,
        active_only=active_only
    )
    
    return [CourseResponse.model_validate(c) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get course by ID"""
    course_service = CourseService(db)
    course = course_service.get_course(course_id)
    
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return CourseResponse.model_validate(course)


@router.get("/search/by-name")
def search_courses(
    name: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Search courses by name"""
    course_service = CourseService(db)
    courses = course_service.search_courses(name, skip, limit)
    return [CourseResponse.model_validate(c) for c in courses]


@router.get("/{course_id}/capacity")
def check_capacity(course_id: int, db: Session = Depends(get_db)):
    """Check course capacity status"""
    course_service = CourseService(db)
    capacity_info = course_service.check_capacity(course_id)
    
    if not capacity_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return capacity_info


@router.delete("/{course_id}", dependencies=[Depends(require_admin)])
def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete a course (Admins only)"""
    course_service = CourseService(db)
    success = course_service.delete_course(course_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )
    
    return {"message": "Course deleted successfully"}

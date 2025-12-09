"""
Material routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os

from tms.infra.database import get_db
from tms.infra.models import User, UserRole
from tms.api.dependencies import get_current_user, require_teacher
from tms.api.schemas.common import MaterialResponse
from tms.application.services.material_service import MaterialService

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.post("/", response_model=MaterialResponse, dependencies=[Depends(require_teacher)])
async def upload_material(
    course_id: int = Form(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a course material (Teachers and Admins only)"""
    material_service = MaterialService(db)
    
    # Read file content
    file_content = await file.read()
    
    material = await material_service.upload_material(
        course_id=course_id,
        title=title,
        file_content=file_content,
        filename=file.filename,
        description=description
    )
    
    if not material:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to upload material. Course not found or file too large."
        )
    
    return MaterialResponse.model_validate(material)


@router.get("/course/{course_id}", response_model=List[MaterialResponse])
def get_course_materials(
    course_id: int,
    file_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all materials for a course"""
    material_service = MaterialService(db)
    materials = material_service.get_course_materials(course_id, skip, limit, file_type)
    return [MaterialResponse.model_validate(m) for m in materials]


@router.get("/{material_id}")
def download_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download a material file"""
    material_service = MaterialService(db)
    
    # Check if user is a student and has access
    if current_user.role == UserRole.STUDENT:
        from tms.infra.repositories.student_repository import StudentRepository
        student_repo = StudentRepository(db)
        student = student_repo.get_by_user_id(current_user.id)
        
        if student and not material_service.check_access_permission(student.id, material_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be enrolled in the course to access this material"
            )
    
    # Get file path
    file_path = material_service.get_file_path(material_id)
    
    if not file_path or not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return FileResponse(
        file_path,
        filename=os.path.basename(file_path)
    )


@router.delete("/{material_id}", dependencies=[Depends(require_teacher)])
async def delete_material(material_id: int, db: Session = Depends(get_db)):
    """Delete a material (Teachers and Admins only)"""
    material_service = MaterialService(db)
    success = await material_service.delete_material(material_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found"
        )
    
    return {"message": "Material deleted successfully"}

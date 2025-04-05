from typing import Any, List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_verified_user
from app.crud.base import CRUDBase
from app.db.models.scholarship import Scholarship
from app.schemas.scholarship import (
    ScholarshipCreate, 
    ScholarshipUpdate, 
    ScholarshipInDB
)

router = APIRouter()
scholarship_crud = CRUDBase(Scholarship)


@router.get("/", response_model=List[ScholarshipInDB])
def read_scholarships(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    country: Optional[str] = None,
    education_level: Optional[str] = None,
) -> Any:
    """
    Retrieve scholarships with optional filtering.
    """
    query = db.query(Scholarship).filter(Scholarship.is_active == True)
    
    if country:
        query = query.filter(Scholarship.country == country)
    
    if education_level:
        query = query.filter(Scholarship.education_level == education_level)
    
    scholarships = query.offset(skip).limit(limit).all()
    return scholarships


@router.post("/", response_model=ScholarshipInDB)
def create_scholarship(
    *,
    db: Session = Depends(get_db),
    scholarship_in: ScholarshipCreate,
    current_user = Depends(get_current_verified_user),
) -> Any:
    """
    Create new scholarship.
    """
    scholarship = Scholarship(
        **scholarship_in.dict(),
        user_id=current_user.id
    )
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    return scholarship


@router.get("/{scholarship_id}", response_model=ScholarshipInDB)
def read_scholarship(
    *,
    db: Session = Depends(get_db),
    scholarship_id: int,
) -> Any:
    """
    Get scholarship by ID.
    """
    scholarship = scholarship_crud.get(db, id=scholarship_id)
    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found"
        )
    return scholarship


@router.put("/{scholarship_id}", response_model=ScholarshipInDB)
def update_scholarship(
    *,
    db: Session = Depends(get_db),
    scholarship_id: int,
    scholarship_in: ScholarshipUpdate,
    current_user = Depends(get_current_verified_user),
) -> Any:
    """
    Update a scholarship.
    """
    scholarship = db.query(Scholarship).filter(
        Scholarship.id == scholarship_id,
        Scholarship.user_id == current_user.id
    ).first()
    
    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found or you don't have permission to modify it"
        )
    
    for field, value in scholarship_in.dict(exclude_unset=True).items():
        setattr(scholarship, field, value)
    
    db.add(scholarship)
    db.commit()
    db.refresh(scholarship)
    return scholarship


@router.delete("/{scholarship_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scholarship(
    *,
    db: Session = Depends(get_db),
    scholarship_id: int,
    current_user = Depends(get_current_verified_user),
) -> None:
    """
    Delete a scholarship.
    """
    scholarship = db.query(Scholarship).filter(
        Scholarship.id == scholarship_id,
        Scholarship.user_id == current_user.id
    ).first()
    
    if not scholarship:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholarship not found or you don't have permission to delete it"
        )
    
    db.delete(scholarship)
    db.commit()
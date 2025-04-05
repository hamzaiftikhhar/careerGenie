from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_verified_user
from app.crud.base import CRUDBase
from app.db.models.counseling import CounselingSession, SessionStatus
from app.schemas.counseling import (
    CounselingSessionCreate, 
    CounselingSessionUpdate, 
    CounselingSessionInDB
)

router = APIRouter()
counseling_crud = CRUDBase(CounselingSession)


@router.get("/", response_model=List[CounselingSessionInDB])
def read_counseling_sessions(
    *,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_verified_user),
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Retrieve counseling sessions for current user.
    """
    sessions = db.query(CounselingSession).filter(
        CounselingSession.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return sessions


@router.post("/", response_model=CounselingSessionInDB)
def create_counseling_session(
    *,
    db: Session = Depends(get_db),
    session_in: CounselingSessionCreate,
    current_user = Depends(get_current_verified_user),
) -> Any:
    """
    Create new counseling session request.
    """
    session = CounselingSession(
        **session_in.dict(),
        user_id=current_user.id,
        status=SessionStatus.PENDING
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/{session_id}", response_model=CounselingSessionInDB)
def read_counseling_session(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    current_user = Depends(get_current_verified_user),
) -> Any:
    """
    Get specific counseling session.
    """
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id,
        CounselingSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling session not found"
        )
    
    return session


@router.put("/{session_id}", response_model=CounselingSessionInDB)
def update_counseling_session(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    session_in: CounselingSessionUpdate,
    current_user = Depends(get_current_verified_user),
) -> Any:
    """
    Update a counseling session.
    """
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id,
        CounselingSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling session not found or you don't have permission to modify it"
        )
    
    # Prevent updating already completed or cancelled sessions
    if session.status in [SessionStatus.COMPLETED, SessionStatus.CANCELLED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot update a session with {session.status.value} status"
        )
    
    for field, value in session_in.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancel_counseling_session(
    *,
    db: Session = Depends(get_db),
    session_id: int,
    current_user = Depends(get_current_verified_user),
) -> None:
    """
    Cancel a counseling session.
    """
    session = db.query(CounselingSession).filter(
        CounselingSession.id == session_id,
        CounselingSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Counseling session not found or you don't have permission to cancel it"
        )
    
    # Instead of deleting, mark as cancelled
    session.status = SessionStatus.CANCELLED
    db.add(session)
    db.commit()
from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import (
    get_db, 
    get_current_active_user, 
    get_current_verified_user, 
    get_current_superuser
)
from app.crud import user
from app.schemas.user import User, UserUpdate, UserCreate
from app.db.models.user import User as UserModel

router = APIRouter()


@router.get("/me", response_model=User)
def read_user_me(
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.put("/me", response_model=User)
def update_user_me(
    *,
    db: Session = Depends(get_db),
    user_in: UserUpdate,
    current_user: UserModel = Depends(get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    updated_user = user.update(db, db_obj=current_user, obj_in=user_in)
    return updated_user


@router.get("/{user_id}", response_model=User)
def read_user_by_id(
    user_id: int,
    current_user: UserModel = Depends(get_current_superuser),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    Admin access required.
    """
    db_user = user.get(db, id=user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user


@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(get_current_superuser),
) -> Any:
    """
    Retrieve users.
    Admin access required.
    """
    users = user.get_multi(db, skip=skip, limit=limit)
    return users
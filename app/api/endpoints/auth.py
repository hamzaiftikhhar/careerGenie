from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.core.security import create_access_token
from app.crud.user import user
from app.db.models.user import User
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserInDB
from app.crud.verification import verification as verification_crud
from app.utils.email_utils import send_verification_email

router = APIRouter()


@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    db_user = user.get_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create the user
    new_user = user.create(db, obj_in=user_in)
    
    # Create verification token
    verification_token = verification_crud.create_verification_token(db, user_id=new_user.id)
    
    # Send verification email
    send_verification_email(
        email_to=new_user.email, 
        token=verification_token.token,
        username=f"{new_user.first_name} {new_user.last_name}"
    )
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    db_user = user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )
    if not user.is_active(db_user):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=db_user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/verify-email/{token}", response_model=UserInDB)
def verify_email(
    *,
    db: Session = Depends(get_db),
    token: str,
) -> Any:
    """
    Verify user email with token.
    """
    verification = verification_crud.get_by_token(db, token=token)
    if not verification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Verification token not found",
        )
    
    if verification_crud.is_expired(verification):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification token has expired",
        )
    
    # Mark user as verified
    db_user = user.mark_verified(db, user_id=verification.user_id)
    
    # Remove the verification token
    verification_crud.remove(db, id=verification.id)
    
    return db_user


@router.post("/request-password-reset", status_code=status.HTTP_202_ACCEPTED)
def request_password_reset(
    email: str = Body(..., embed=True),
    db: Session = Depends(get_db),
) -> Any:
    """
    Request a password reset for a user.
    """
    db_user = user.get_by_email(db, email=email)
    if db_user:
        # Create password reset token
        reset_token = verification_crud.create_password_reset_token(db, user_id=db_user.id)
        
        # Send password reset email
        send_password_reset_email(
            email_to=db_user.email,
            token=reset_token.token,
            username=f"{db_user.first_name} {db_user.last_name}"
        )
    
    # Always return success to prevent email enumeration attacks
    return None


@router.post("/reset-password/{token}", response_model=UserInDB)
def reset_password(
    *,
    db: Session = Depends(get_db),
    token: str,
    new_password: str = Body(..., embed=True),
) -> Any:
    """
    Reset user password with token.
    """
    verification = verification_crud.get_by_token(db, token=token)
    if not verification or verification.type != "password_reset":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Password reset token not found",
        )
    
    if verification_crud.is_expired(verification):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password reset token has expired",
        )
    
    # Update password
    db_user = user.get(db, id=verification.user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    user.update(db, db_obj=db_user, obj_in={"password": new_password})
    
    # Remove the verification token
    verification_crud.remove(db, id=verification.id)
    
    return db_user
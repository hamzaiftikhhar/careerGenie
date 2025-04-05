from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import create_access_token, get_password_hash
from app.core.email import send_verification_email, send_reset_password_email
from app.crud import user, verification
from app.db.models.verification import VerificationType
from app.db.models.user import User
from app.schemas.auth import (
    Token, EmailVerificationRequest, PasswordResetRequest, 
    PasswordResetConfirm, VerifySession
)
from app.schemas.user import UserCreate, User as UserSchema

router = APIRouter()


@router.post("/register", response_model=UserSchema)
def register(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    Register a new user.
    """
    existing_user = user.get_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )
    
    # Create user
    new_user = user.create(db, obj_in=user_in)
    
    # Create email verification token
    email_verification = verification.create_email_verification(db, user_id=new_user.id)
    
    # Send verification email
    send_verification_email(new_user.email, email_verification.token)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    Get access token for user.
    """
    authenticated_user = user.authenticate(
        db, email=form_data.username, password=form_data.password
    )
    if not authenticated_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active(authenticated_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=authenticated_user.id, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/verify-email", response_model=UserSchema)
def verify_email(
    *,
    db: Session = Depends(get_db),
    verification_data: EmailVerificationRequest = Body(...),
) -> Any:
    """
    Verify user email with token.
    """
    verification_record = verification.verify_token(
        db, 
        token=verification_data.token,
        verification_type=VerificationType.EMAIL_VERIFICATION
    )
    
    if not verification_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token",
        )
    
    # Mark user as verified
    verified_user = user.mark_verified(db, user_id=verification_record.user_id)
    
    # Mark verification token as used
    verification.mark_as_used(db, verification_id=verification_record.id)
    
    return verified_user


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
def forgot_password(
    *,
    db: Session = Depends(get_db),
    reset_request: PasswordResetRequest = Body(...),
) -> Any:
    """
    Send password reset email.
    """
    existing_user = user.get_by_email(db, email=reset_request.email)
    if existing_user:
        # Create password reset token
        reset_token = verification.create_password_reset(db, user_id=existing_user.id)
        
        # Send password reset email
        send_reset_password_email(existing_user.email, reset_token.token)
    
    # Always return success to prevent email enumeration
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password", response_model=UserSchema)
def reset_password(
    *,
    db: Session = Depends(get_db),
    reset_data: PasswordResetConfirm = Body(...),
) -> Any:
    """
    Reset user password with token.
    """
    verification_record = verification.verify_token(
        db, 
        token=reset_data.token,
        verification_type=VerificationType.PASSWORD_RESET
    )
    
    if not verification_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )
    
    # Update user password
    db_user = user.get(db, id=verification_record.user_id)
    update_data = {"password": reset_data.new_password}
    updated_user = user.update(db, db_obj=db_user, obj_in=update_data)
    
    # Mark verification token as used
    verification.mark_as_used(db, verification_id=verification_record.id)
    
    return updated_user


@router.post("/verify-session", response_model=UserSchema)
def verify_session(
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    Verify user's active session.
    """
    return current_user
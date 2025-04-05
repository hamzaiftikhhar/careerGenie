from typing import Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.db.models.verification import Verification, VerificationType
from app.core.config import settings
from app.core.security import generate_verification_token


class CRUDVerification(CRUDBase[Verification, None, None]):
    def create_email_verification(self, db: Session, *, user_id: int) -> Verification:
        token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS)
        
        db_obj = Verification(
            token=token,
            verification_type=VerificationType.EMAIL_VERIFICATION,
            expires_at=expires_at,
            user_id=user_id
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def create_password_reset(self, db: Session, *, user_id: int) -> Verification:
        token = generate_verification_token()
        expires_at = datetime.utcnow() + timedelta(hours=settings.PASSWORD_RESET_TOKEN_EXPIRE_HOURS)
        
        db_obj = Verification(
            token=token,
            verification_type=VerificationType.PASSWORD_RESET,
            expires_at=expires_at,
            user_id=user_id
        )
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_token(self, db: Session, *, token: str) -> Optional[Verification]:
        return db.query(Verification).filter(Verification.token == token).first()
    
    def verify_token(self, db: Session, *, token: str, verification_type: VerificationType) -> Optional[Verification]:
        verification = db.query(Verification).filter(
            Verification.token == token,
            Verification.verification_type == verification_type,
            Verification.is_used == False,
            Verification.expires_at > datetime.utcnow()
        ).first()
        
        return verification
    
    def mark_as_used(self, db: Session, *, verification_id: int) -> Verification:
        verification = self.get(db, id=verification_id)
        if verification:
            verification.is_used = True
            db.add(verification)
            db.commit()
            db.refresh(verification)
        return verification


verification = CRUDVerification(Verification)
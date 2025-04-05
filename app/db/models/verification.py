from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base


class VerificationType(enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class Verification(Base):
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, index=True, nullable=False)
    verification_type = Column(Enum(VerificationType), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("user.id"))
    
    # Relationships
    user = relationship("User", back_populates="verifications")
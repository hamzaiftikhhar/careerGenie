from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base


class Scholarship(Base):
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    eligibility = Column(Text, nullable=False)
    amount = Column(Float)
    deadline = Column(DateTime)
    is_active = Column(Boolean, default=True)
    source_url = Column(String)
    country = Column(String)
    institution = Column(String)
    education_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign keys
    user_id = Column(Integer, ForeignKey("user.id"))
    
    # Relationships
    user = relationship("User", back_populates="scholarships")
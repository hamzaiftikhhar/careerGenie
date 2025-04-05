from typing import Optional
from datetime import datetime
from pydantic import BaseModel, HttpUrl


# Shared properties
class ScholarshipBase(BaseModel):
    title: str
    description: str
    eligibility: str
    amount: Optional[float] = None
    deadline: Optional[datetime] = None
    country: Optional[str] = None
    institution: Optional[str] = None
    education_level: Optional[str] = None
    source_url: Optional[str] = None
    is_active: bool = True


# Properties to receive via API on creation
class ScholarshipCreate(ScholarshipBase):
    pass


# Properties to receive via API on update
class ScholarshipUpdate(ScholarshipBase):
    title: Optional[str] = None
    description: Optional[str] = None
    eligibility: Optional[str] = None


# Properties stored in DB
class ScholarshipInDBBase(ScholarshipBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


# Properties returned by API
class ScholarshipInDB(ScholarshipInDBBase):
    pass
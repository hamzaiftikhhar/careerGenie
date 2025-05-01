from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class SessionStatusEnum(str, Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled" 
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Shared properties
class CounselingSessionBase(BaseModel):
    title: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    counselor_name: Optional[str] = None
    counselor_email: Optional[str] = None
    meeting_link: Optional[str] = None
    notes: Optional[str] = None


# Properties to receive via API on creation
class CounselingSessionCreate(CounselingSessionBase):
    pass


# Properties to receive via API on update
class CounselingSessionUpdate(CounselingSessionBase):
    title: Optional[str] = None
    status: Optional[SessionStatusEnum] = None


# Properties stored in DB
class CounselingSessionInDBBase(CounselingSessionBase):
    id: int
    user_id: int
    status: SessionStatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Properties returned by API
class CounselingSessionInDB(CounselingSessionInDBBase):
    pass
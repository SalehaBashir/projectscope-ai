from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class ProjectCreate(BaseModel):
    title: str
    description: str
    budget: Optional[str] = None
    platform: Optional[str] = None


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str
    budget: Optional[str] = None
    platform: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
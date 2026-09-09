from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


class FeedbackCreate(BaseModel):
    task_id: Optional[UUID] = None
    estimated_hours: Optional[float] = Field(None, ge=0)
    actual_hours: float = Field(..., gt=0)
    notes: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: UUID
    project_id: UUID
    user_id: Optional[UUID] = None
    task_id: Optional[UUID] = None
    estimated_hours: Optional[float] = None
    actual_hours: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class FeedbackSummary(BaseModel):
    project_id: UUID
    total_feedback_count: int
    total_estimated_hours: Optional[float] = None
    total_actual_hours: float
    average_deviation_percent: Optional[float] = None

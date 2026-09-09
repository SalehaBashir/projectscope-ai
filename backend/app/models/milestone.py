from sqlalchemy import Column, String, DateTime, Float, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)

    order_index = Column(Float, nullable=False, default=0)
    estimated_hours = Column(Float, nullable=True)
    timeline_weeks = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
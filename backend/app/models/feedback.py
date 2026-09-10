from sqlalchemy import Column, DateTime, Float, Text, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    task_id = Column(UUID(as_uuid=True), nullable=True)

    estimated_hours = Column(Float, nullable=True)
    actual_hours = Column(Float, nullable=False)

    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )
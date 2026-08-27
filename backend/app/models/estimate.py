from sqlalchemy import Column, String, DateTime, Float, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base


class Estimate(Base):
    __tablename__ = "estimates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    min_hours = Column(Float, nullable=True)
    expected_hours = Column(Float, nullable=True)
    max_hours = Column(Float, nullable=True)
    min_cost = Column(Float, nullable=True)
    expected_cost = Column(Float, nullable=True)
    max_cost = Column(Float, nullable=True)
    timeline_weeks = Column(Float, nullable=True)
    complexity_score = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
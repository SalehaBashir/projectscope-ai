from sqlalchemy import Column, String, DateTime, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feature_id = Column(UUID(as_uuid=True), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    role_id = Column(UUID(as_uuid=True), nullable=True)

    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    base_hours = Column(Float, default=0.0)

    # Phase 11: dependency-aware scheduling
    depends_on = Column(UUID(as_uuid=True), nullable=True)

    # Phase 11: scheduled timeline
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
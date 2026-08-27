from sqlalchemy import Column, String, DateTime, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base


class Feature(Base):
    __tablename__ = "features"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    canonical_name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(String, default="medium")
    complexity = Column(String, default="medium")
    confidence = Column(Float, default=1.0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, String, DateTime, Text, Float, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base


class Risk(Base):
    __tablename__ = "risks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    category = Column(String, nullable=False, default="technical")
    severity = Column(String, nullable=False, default="medium")
    risk_score = Column(Float, nullable=False, default=4.0)
    description = Column(Text, nullable=False)
    probability = Column(String, default="medium")
    impact = Column(String, default="medium")
    mitigation = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
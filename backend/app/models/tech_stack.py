from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
import uuid
from app.database.connection import Base


class TechStackRecommendation(Base):
    __tablename__ = "tech_stack_recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    stack = Column(JSONB, nullable=False)      # list of {category, recommendation, reason}
    summary = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
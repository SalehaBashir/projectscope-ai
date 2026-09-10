from sqlalchemy import Column, String, DateTime, Float, Text, JSON, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class LLMRequest(Base):
    __tablename__ = "llm_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False)

    provider = Column(String, nullable=False)
    model = Column(String, nullable=False)

    prompt_tokens = Column(Float, nullable=True)
    completion_tokens = Column(Float, nullable=True)
    latency_ms = Column(Float, nullable=True)

    status = Column(String, nullable=False, default="success")
    error_message = Column(Text, nullable=True)

    metadata_json = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
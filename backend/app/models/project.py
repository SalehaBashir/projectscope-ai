from sqlalchemy import Column, String, DateTime, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.database.connection import Base
import uuid


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), nullable=False)
    owner_id = Column(UUID(as_uuid=True), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    budget = Column(String, nullable=True)
    platform = Column(String, nullable=True)
    status = Column(String, default="draft")  
    assumptions = Column(JSONB, nullable=False, default=list)
    missing_information = Column(JSONB, nullable=False, default=list)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
from sqlalchemy import Column, String, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base


class ThemeSelection(Base):
    __tablename__ = "theme_selections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False, unique=True)
    organization_id = Column(UUID(as_uuid=True), nullable=False)

    theme_id = Column(String, nullable=False)   # references THEME_PRESETS[i]["id"], e.g. "vibrant_marketplace"
    source = Column(String, nullable=False, default="ai_suggested")  # "ai_suggested" | "user_selected"

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
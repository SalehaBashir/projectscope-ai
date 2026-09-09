from sqlalchemy import Column, String, DateTime, Float, JSON, func
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.database.connection import Base


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)

    model_name = Column(String, nullable=False)
    model_version = Column(String, nullable=True)

    predicted_hours = Column(Float, nullable=True)
    confidence = Column(Float, nullable=True)

    input_features = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
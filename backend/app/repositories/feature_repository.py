from sqlalchemy.orm import Session
from app.models.feature import Feature
import uuid


def create_features(db: Session, project_id: uuid.UUID, features: list):
    """features: list of dicts with 'canonical_name', 'description', 'priority', 'complexity', 'confidence'"""
    created = []
    for feat in features:
        new_feat = Feature(
            project_id=project_id,
            canonical_name=feat["canonical_name"],
            description=feat["description"],
            priority=feat["priority"],
            complexity=feat["complexity"],
            confidence=feat["confidence"],
        )
        db.add(new_feat)
        created.append(new_feat)
    db.commit()
    for f in created:
        db.refresh(f)
    return created


def list_features(db: Session, project_id: uuid.UUID):
    return db.query(Feature).filter(Feature.project_id == project_id).all()
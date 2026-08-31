from sqlalchemy.orm import Session
from app.models.tech_stack import TechStackRecommendation
import uuid


def save_recommendation(db: Session, project_id: uuid.UUID, stack: list, summary: str):
    existing = db.query(TechStackRecommendation).filter(
        TechStackRecommendation.project_id == project_id
    ).first()

    if existing:
        existing.stack = stack
        existing.summary = summary
        db.commit()
        db.refresh(existing)
        return existing

    new_rec = TechStackRecommendation(project_id=project_id, stack=stack, summary=summary)
    db.add(new_rec)
    db.commit()
    db.refresh(new_rec)
    return new_rec


def get_recommendation(db: Session, project_id: uuid.UUID):
    return db.query(TechStackRecommendation).filter(
        TechStackRecommendation.project_id == project_id
    ).first()
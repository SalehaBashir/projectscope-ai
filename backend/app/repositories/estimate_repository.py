from sqlalchemy.orm import Session
from app.models.estimate import Estimate
import uuid


def save_estimate(db: Session, project_id: uuid.UUID, min_hours: float, expected_hours: float, max_hours: float, complexity_score: float):
    # Check if an estimate already exists for this project — if so, update it
    existing = db.query(Estimate).filter(Estimate.project_id == project_id).first()

    if existing:
        existing.min_hours = min_hours
        existing.expected_hours = expected_hours
        existing.max_hours = max_hours
        existing.complexity_score = complexity_score
        db.commit()
        db.refresh(existing)
        return existing

    new_estimate = Estimate(
        project_id=project_id,
        min_hours=min_hours,
        expected_hours=expected_hours,
        max_hours=max_hours,
        complexity_score=complexity_score,
    )
    db.add(new_estimate)
    db.commit()
    db.refresh(new_estimate)
    return new_estimate


def get_estimate(db: Session, project_id: uuid.UUID):
    return db.query(Estimate).filter(Estimate.project_id == project_id).first()
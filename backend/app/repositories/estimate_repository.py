from sqlalchemy.orm import Session
from app.models.estimate import Estimate
from app.models.project import Project
import uuid


def save_estimate(
    db: Session,
    project_id: uuid.UUID,
    min_hours: float,
    expected_hours: float,
    max_hours: float,
    complexity_score: float,
    min_cost: float,
    expected_cost: float,
    max_cost: float,
    timeline_weeks: float,
):
    project = db.get(Project, project_id)

    if not project:
        raise ValueError("Project not found")

    organization_id = project.organization_id

    existing = (
        db.query(Estimate)
        .filter(Estimate.project_id == project_id)
        .first()
    )

    if existing:
        existing.organization_id = organization_id
        existing.min_hours = min_hours
        existing.expected_hours = expected_hours
        existing.max_hours = max_hours
        existing.complexity_score = complexity_score
        existing.min_cost = min_cost
        existing.expected_cost = expected_cost
        existing.max_cost = max_cost
        existing.timeline_weeks = timeline_weeks

        db.commit()
        db.refresh(existing)
        return existing

    new_estimate = Estimate(
        project_id=project_id,
        organization_id=organization_id,
        min_hours=min_hours,
        expected_hours=expected_hours,
        max_hours=max_hours,
        complexity_score=complexity_score,
        min_cost=min_cost,
        expected_cost=expected_cost,
        max_cost=max_cost,
        timeline_weeks=timeline_weeks,
    )

    db.add(new_estimate)
    db.commit()
    db.refresh(new_estimate)

    return new_estimate


def get_estimate(db: Session, project_id: uuid.UUID):
    return (
        db.query(Estimate)
        .filter(Estimate.project_id == project_id)
        .first()
    )
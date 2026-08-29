from sqlalchemy.orm import Session
from app.models.requirement import Requirement
import uuid


def create_requirements(db: Session, project_id: uuid.UUID, requirements: list):
    """requirements: list of dicts with 'category', 'text' (from LLM output)"""
    created = []
    for req in requirements:
        new_req = Requirement(
            project_id=project_id,
            category=req["category"],
            description=req["text"],
            priority="medium",
        )
        db.add(new_req)
        created.append(new_req)
    db.commit()
    for r in created:
        db.refresh(r)
    return created


def list_requirements(db: Session, project_id: uuid.UUID):
    return db.query(Requirement).filter(Requirement.project_id == project_id).all()
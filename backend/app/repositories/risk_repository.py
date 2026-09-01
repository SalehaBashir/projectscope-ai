from sqlalchemy.orm import Session
from app.models.risk import Risk
import uuid


def clear_risks(db: Session, project_id: uuid.UUID):
    db.query(Risk).filter(Risk.project_id == project_id).delete()
    db.commit()


def create_risks(db: Session, project_id: uuid.UUID, risks: list):
    created = []
    for r in risks:
        new_risk = Risk(
            project_id=project_id,
            description=r["description"],
            probability=r["probability"],
            impact=r["impact"],
            mitigation=r["mitigation"],
        )
        db.add(new_risk)
        created.append(new_risk)
    db.commit()
    for r in created:
        db.refresh(r)
    return created


def list_risks(db: Session, project_id: uuid.UUID):
    return db.query(Risk).filter(Risk.project_id == project_id).all()
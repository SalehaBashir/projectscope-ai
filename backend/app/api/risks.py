from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.risk_service import generate_risks_for_project
import uuid

router = APIRouter(prefix="/projects", tags=["Risks"])


@router.post("/{project_id}/risks")
def generate_risks(project_id: uuid.UUID, db: Session = Depends(get_db)):
    risks = generate_risks_for_project(db, project_id)
    return [
        {
            "id": r.id,
            "description": r.description,
            "probability": r.probability,
            "impact": r.impact,
            "mitigation": r.mitigation,
        }
        for r in risks
    ]
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.risk_service import generate_risks_for_project
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["Risks"])


@router.post("/{project_id}/risks")
def generate_risks(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    risks = generate_risks_for_project(db, project_id)
    return [
        {
            "id": r.id,
            "description": r.description,
            "probability": r.probability,
            "impact": r.impact,
            "mitigation": r.mitigation,
            "category": r.category,
            "severity": r.severity,
            "risk_score": r.risk_score,
        }
        for r in risks
    ]

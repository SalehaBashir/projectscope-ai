from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.mvp_service import generate_mvp_recommendation
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["MVP Recommendation"])


@router.get("/{project_id}/mvp")
def get_mvp_recommendation(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    return generate_mvp_recommendation(db, project_id)

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.tech_stack_service import recommend_tech_stack, TechStackError
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["Tech Stack"])


@router.post("/{project_id}/tech-stack")
def get_tech_stack(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        result = recommend_tech_stack(db, project_id)
        return result
    except TechStackError as e:
        raise HTTPException(status_code=502, detail=str(e))

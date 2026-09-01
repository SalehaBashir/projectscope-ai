from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.tech_stack_service import recommend_tech_stack, TechStackError
import uuid

router = APIRouter(prefix="/projects", tags=["Tech Stack"])


@router.post("/{project_id}/tech-stack")
def get_tech_stack(project_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        result = recommend_tech_stack(db, project_id)
        return result
    except TechStackError as e:
        raise HTTPException(status_code=502, detail=str(e))
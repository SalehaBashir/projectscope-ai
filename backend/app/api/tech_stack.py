from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.tech_stack_service import recommend_stack
from app.schemas.tech_stack import TechStackRequest
from app.repositories import project_repository
import uuid

router = APIRouter(prefix="/projects", tags=["Tech Stack"])


@router.post("/{project_id}/tech-stack")
def get_tech_stack(project_id: uuid.UUID, payload: TechStackRequest, db: Session = Depends(get_db)):
    project = project_repository.get_project(db, project_id)
    result = recommend_stack(db, project_id, project.title, payload.preferred_language)

    return {
        "stack": result.stack,
        "summary": result.summary,
    }
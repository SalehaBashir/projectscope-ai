from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services import project_service
import uuid

router = APIRouter(prefix="/projects", tags=["Projects"])

# Temporary placeholder values until real auth (Day 22) is built
TEMP_ORG_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TEMP_USER_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")


@router.post("/", response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_new_project(db, project, TEMP_ORG_ID, TEMP_USER_ID)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    project = project_service.get_project_by_id(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return project_service.get_all_projects(db)
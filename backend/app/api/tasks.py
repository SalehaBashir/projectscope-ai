from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.task_service import generate_tasks_for_project
import uuid

router = APIRouter(prefix="/projects", tags=["Tasks"])


@router.post("/{project_id}/generate-tasks")
def generate_tasks(project_id: uuid.UUID, db: Session = Depends(get_db)):
    tasks = generate_tasks_for_project(db, project_id)
    return [
        {
            "id": t.id,
            "title": t.title,
            "role_id": t.role_id,
            "base_hours": t.base_hours,
        }
        for t in tasks
    ]
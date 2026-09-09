from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.task_service import generate_tasks_for_project
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["Tasks"])


@router.post("/{project_id}/generate-tasks")
def generate_tasks(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
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

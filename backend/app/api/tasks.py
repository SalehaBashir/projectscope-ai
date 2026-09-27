from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.task_service import generate_tasks_for_project
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
from app.models.feature import Feature
from app.models.role import Role

import uuid


router = APIRouter(
    prefix="/projects",
    tags=["Tasks"],
)


@router.post("/{project_id}/generate-tasks")
def generate_tasks(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(
        project_id,
        db,
        current_user,
    )

    tasks = generate_tasks_for_project(
        db,
        project_id,
    )

    response = []

    for task in tasks:

        feature = None

        if task.feature_id:
            feature = db.get(
                Feature,
                task.feature_id,
            )

        role = None

        if task.role_id:
            role = db.get(
                Role,
                task.role_id,
            )

        response.append(
            {
                "id": task.id,
                "title": task.title,
                "feature_id": task.feature_id,
                "feature_name": (
                    feature.canonical_name
                    if feature
                    else None
                ),
                "role_id": task.role_id,
                "role_name": (
                    role.name
                    if role
                    else None
                ),
                "base_hours": task.base_hours,
            }
        )

    return response
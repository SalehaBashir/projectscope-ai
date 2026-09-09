import uuid

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.services import project_service
from app.services.recalculation_service import (
    recalculate_project,
    RecalculationError,
)
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "/",
    response_model=ProjectResponse,
)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return project_service.create_new_project(
        db,
        project,
        current_user.organization_id,
        current_user.id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = project_service.get_project_by_id(
        db,
        project_id,
    )

    if not project:
        raise HTTPException(
            status_code=404,
            detail="Project not found",
        )

    if project.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this project",
        )

    return project


@router.get(
    "/",
    response_model=list[ProjectResponse],
)
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    projects = project_service.get_all_projects(db)

    return [
        project
        for project in projects
        if project.organization_id == current_user.organization_id
    ]


@router.patch(
    "/{project_id}",
    response_model=ProjectResponse,
)
def update_project(
    project_id: uuid.UUID,
    update: ProjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)

    updated = project_service.update_existing_project(
        db,
        project_id,
        title=update.title,
        description=update.description,
        budget=update.budget,
        platform=update.platform,
    )
    return updated


@router.delete(
    "/{project_id}",
)
def delete_project(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)

    deleted = project_service.delete_existing_project(db, project_id)
    if not deleted:
        raise HTTPException(
            status_code=400,
            detail="Could not delete project",
        )
    return {"detail": "Project deleted successfully"}


@router.post(
    "/{project_id}/recalculate",
)
def recalculate(
    project_id: uuid.UUID,
    update: ProjectUpdate = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)

    try:
        result = recalculate_project(
            db,
            project_id,
            description=update.description if update else None,
            budget=update.budget if update else None,
            platform=update.platform if update else None,
        )
    except RecalculationError as e:
        raise HTTPException(
            status_code=502,
            detail=str(e),
        )

    estimate = result["estimate"]
    return {
        "project": {
            "id": result["project"].id,
            "title": result["project"].title,
            "description": result["project"].description,
            "budget": result["project"].budget,
            "platform": result["project"].platform,
            "status": result["project"].status,
        },
        "estimate": {
            "min_hours": estimate["min_hours"],
            "expected_hours": estimate["expected_hours"],
            "max_hours": estimate["max_hours"],
            "expected_cost": estimate["expected_cost"],
            "min_cost": estimate["min_cost"],
            "max_cost": estimate["max_cost"],
            "timeline_weeks_expected": estimate["timeline_weeks_expected"],
            "complexity_score": estimate["complexity_score"],
            "task_count": estimate["task_count"],
            "schedule": estimate["schedule"],
        },
    }
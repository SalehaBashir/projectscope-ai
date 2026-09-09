from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.security.security import get_current_user
from app.models.user import User
from app.models.project import Project
import uuid


def require_project_access(
    project_id: uuid.UUID,
    db: Session,
    current_user: User,
) -> Project:
    """Verify the current user has access to the given project.

    Returns the project if access is granted.
    Raises HTTPException 404 if project doesn't exist,
    or 403 if the user belongs to a different organization.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
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

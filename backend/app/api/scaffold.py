from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.scaffold_service import build_scaffold_zip
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["Start Building"])


@router.post("/{project_id}/start-building")
def start_building(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        zip_path = build_scaffold_zip(db, project_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    return FileResponse(
        path=zip_path,
        media_type="application/zip",
        filename="project_starter.zip",
    )

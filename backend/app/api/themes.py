from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.theme import ThemeSelectRequest
from app.services.theme_service import (
    list_all_themes,
    suggest_theme_for_project,
    select_theme,
    get_selected_theme,
    ThemeError,
)
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(tags=["Themes"])


@router.get("/themes")
def get_themes():
    return list_all_themes()


@router.post("/projects/{project_id}/theme-suggestion")
def get_theme_suggestion(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    theme = suggest_theme_for_project(db, project_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Project not found")
    return theme


@router.post("/projects/{project_id}/theme")
def choose_theme(
    project_id: uuid.UUID,
    request: ThemeSelectRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        return select_theme(db, project_id, request.theme_id)
    except ThemeError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/projects/{project_id}/theme")
def get_saved_theme(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    theme = get_selected_theme(db, project_id)
    if not theme:
        raise HTTPException(
            status_code=404, detail="No theme selected for this project yet"
        )
    return theme

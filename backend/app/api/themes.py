from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.theme_service import list_all_themes, suggest_theme_for_project
import uuid

router = APIRouter(tags=["Themes"])


@router.get("/themes")
def get_themes():
    return list_all_themes()


@router.post("/projects/{project_id}/theme-suggestion")
def get_theme_suggestion(project_id: uuid.UUID, db: Session = Depends(get_db)):
    theme = suggest_theme_for_project(db, project_id)
    if not theme:
        raise HTTPException(status_code=404, detail="Project not found")
    return theme
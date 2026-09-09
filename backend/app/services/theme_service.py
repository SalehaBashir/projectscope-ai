from sqlalchemy.orm import Session
from app.ai.themes import THEME_PRESETS, suggest_theme_for_project_type, get_theme_by_id
from app.models.project import Project
from app.repositories import feature_repository, theme_repository
import uuid


class ThemeError(Exception):
    pass


def list_all_themes():
    return THEME_PRESETS


def suggest_theme_for_project(db: Session, project_id: uuid.UUID):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    features = feature_repository.list_features(db, project_id)
    feature_text = " ".join(f.canonical_name + " " + (f.description or "") for f in features)

    combined_text = project.description + " " + feature_text
    return suggest_theme_for_project_type(combined_text)


def select_theme(db: Session, project_id: uuid.UUID, theme_id: str = None):
    """
    Save the theme for this project.
    - theme_id given  -> user manually picked it ("user_selected")
    - theme_id omitted -> fall back to the AI suggestion ("ai_suggested")
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ThemeError("Project not found")

    if theme_id:
        theme = get_theme_by_id(theme_id)
        if not theme:
            raise ThemeError(f"Unknown theme id: {theme_id}")
        source = "user_selected"
    else:
        theme = suggest_theme_for_project(db, project_id)
        source = "ai_suggested"

    theme_repository.save_selection(db, project_id, theme["id"], source)
    return theme


def get_selected_theme(db: Session, project_id: uuid.UUID):
    """
    Returns the previously saved theme for this project, or None if the
    project hasn't gone through theme selection yet.
    """
    selection = theme_repository.get_selection(db, project_id)
    if not selection:
        return None
    return get_theme_by_id(selection.theme_id)
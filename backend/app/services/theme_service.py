from sqlalchemy.orm import Session
from app.ai.themes import THEME_PRESETS, suggest_theme_for_project_type
from app.models.project import Project
from app.repositories import feature_repository
import uuid


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
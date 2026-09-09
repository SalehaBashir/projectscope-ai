from sqlalchemy.orm import Session
from app.models.theme import ThemeSelection
import uuid


def save_selection(db: Session, project_id: uuid.UUID, theme_id: str, source: str):
    existing = db.query(ThemeSelection).filter(
        ThemeSelection.project_id == project_id
    ).first()

    if existing:
        existing.theme_id = theme_id
        existing.source = source
        db.commit()
        db.refresh(existing)
        return existing

    new_selection = ThemeSelection(project_id=project_id, theme_id=theme_id, source=source)
    db.add(new_selection)
    db.commit()
    db.refresh(new_selection)
    return new_selection


def get_selection(db: Session, project_id: uuid.UUID):
    return db.query(ThemeSelection).filter(
        ThemeSelection.project_id == project_id
    ).first()
from sqlalchemy.orm import Session
from app.repositories import project_repository
from app.schemas.project import ProjectCreate
import uuid


def create_new_project(db: Session, project_data: ProjectCreate, organization_id: uuid.UUID, owner_id: uuid.UUID):
    # Business rules go here later (e.g. validation, triggering AI analysis)
    return project_repository.create_project(db, project_data, organization_id, owner_id)


def get_project_by_id(db: Session, project_id: uuid.UUID):
    project = project_repository.get_project(db, project_id)
    if not project:
        return None
    return project


def get_all_projects(db: Session):
    return project_repository.list_projects(db)
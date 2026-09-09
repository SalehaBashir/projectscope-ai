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


def update_existing_project(
    db: Session,
    project_id: uuid.UUID,
    title: str = None,
    description: str = None,
    budget: str = None,
    platform: str = None,
):
    return project_repository.update_project(
        db,
        project_id,
        title=title,
        description=description,
        budget=budget,
        platform=platform,
    )


def delete_existing_project(db: Session, project_id: uuid.UUID):
    return project_repository.delete_project(db, project_id)


def _get_owned_project_or_none(db: Session, project_id, organization_id):
    project = project_repository.get_project(db, project_id)
    if not project:
        return None
    if project.organization_id != organization_id:
        return None
    return project
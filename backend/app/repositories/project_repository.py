from sqlalchemy.orm import Session
from app.models.project import Project
from app.schemas.project import ProjectCreate
import uuid


def create_project(db: Session, project_data: ProjectCreate, organization_id: uuid.UUID, owner_id: uuid.UUID):
    new_project = Project(
        organization_id=organization_id,
        owner_id=owner_id,
        title=project_data.title,
        description=project_data.description,
        budget=project_data.budget,
        platform=project_data.platform,
        status="draft",
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


def get_project(db: Session, project_id: uuid.UUID):
    return db.query(Project).filter(Project.id == project_id).first()


def list_projects(db: Session):
    return db.query(Project).all()


def update_project(
    db: Session,
    project_id: uuid.UUID,
    title: str = None,
    description: str = None,
    budget: str = None,
    platform: str = None,
):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None

    if title is not None:
        project.title = title
    if description is not None:
        project.description = description
    if budget is not None:
        project.budget = budget
    if platform is not None:
        project.platform = platform

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project_id: uuid.UUID):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return False
    db.delete(project)
    db.commit()
    return True
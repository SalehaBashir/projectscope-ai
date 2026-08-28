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
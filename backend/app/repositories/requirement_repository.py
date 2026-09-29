from sqlalchemy.orm import Session

from app.models.requirement import Requirement

import uuid


def create_requirements(
    db: Session,
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    requirements: list,
):
    """Create AI-generated requirements for a project."""

    created = []

    for req in requirements:
        new_req = Requirement(
            project_id=project_id,
            organization_id=organization_id,
            category=req["category"],
            description=req["text"],
            priority="medium",
        )

        db.add(new_req)
        created.append(new_req)

    db.commit()

    for requirement in created:
        db.refresh(requirement)

    return created


def delete_requirements(
    db: Session,
    project_id: uuid.UUID,
):
    """Delete all existing AI-generated requirements for a project."""

    db.query(Requirement).filter(
        Requirement.project_id == project_id
    ).delete(
        synchronize_session=False
    )


def list_requirements(
    db: Session,
    project_id: uuid.UUID,
):
    """Return all requirements belonging to a project."""

    return (
        db.query(Requirement)
        .filter(
            Requirement.project_id == project_id
        )
        .all()
    )
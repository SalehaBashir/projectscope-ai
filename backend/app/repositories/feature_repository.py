from sqlalchemy.orm import Session

from app.models.feature import Feature

import uuid


def create_features(
    db: Session,
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    features: list,
):
    """Create AI-generated features for a project."""

    created = []

    for feat in features:
        new_feat = Feature(
            project_id=project_id,
            organization_id=organization_id,
            canonical_name=feat["canonical_name"],
            description=feat["description"],
            priority=feat["priority"],
            complexity=feat["complexity"],
            confidence=feat["confidence"],
        )

        db.add(new_feat)
        created.append(new_feat)

    db.commit()

    for feature in created:
        db.refresh(feature)

    return created


def delete_features(
    db: Session,
    project_id: uuid.UUID,
):
    """Delete all features belonging to a project."""

    db.query(Feature).filter(
        Feature.project_id == project_id
    ).delete(
        synchronize_session=False
    )


def list_features(
    db: Session,
    project_id: uuid.UUID,
):
    """Return all features belonging to a project."""

    return (
        db.query(Feature)
        .filter(
            Feature.project_id == project_id
        )
        .all()
    )
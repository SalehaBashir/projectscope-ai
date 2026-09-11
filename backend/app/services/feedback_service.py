from sqlalchemy.orm import Session
from app.repositories import feedback_repository, project_repository
from app.models.task import Task
from app.models.feature import Feature
from app.models.feedback import Feedback
from sqlalchemy import func as sa_func
import uuid


class FeedbackError(Exception):
    pass


def build_ml_training_rows(db: Session):
    """
    Builds ML training rows from real projects that have submitted feedback,
    matching the schema used by the effort-estimation dataset pipeline.

    Each row mirrors the feature columns consumed by
    `app.ml.predictor.predict_effort_hours`, with `actual_hours`
    aggregated from the project's feedback as the target.

    Returns a list of dicts ready to be written to a CSV for retraining.
    """
    projects_with_feedback = (
        db.query(Feedback.project_id)
        .distinct()
        .all()
    )

    rows = []

    for (project_id,) in projects_with_feedback:
        features = (
            db.query(Feature)
            .filter(Feature.project_id == project_id)
            .all()
        )
        feature_names = [f.canonical_name for f in features]
        feature_ids = [f.id for f in features]

        task_count = (
            db.query(sa_func.count(Task.id))
            .filter(Task.feature_id.in_(feature_ids))
            .scalar()
            if feature_ids
            else 0
        )

        role_count = (
            db.query(sa_func.count(sa_func.distinct(Task.role_id)))
            .filter(Task.feature_id.in_(feature_ids))
            .filter(Task.role_id.isnot(None))
            .scalar()
            if feature_ids
            else 0
        )

        integration_names = [
            "PAYMENT", "MESSAGING", "SEARCH", "MAP", "NOTIFICATION"
        ]
        integration_count = sum(
            1
            for n in feature_names
            if any(k in n for k in integration_names)
        )

        complexity_values = {"low": 20, "medium": 50, "high": 85}
        complexity_score = (
            sum(
                complexity_values.get(f.complexity, 50)
                for f in features
            )
            / len(features)
            if features
            else 0.0
        )

        actual_hours = (
            db.query(sa_func.sum(Feedback.actual_hours))
            .filter(Feedback.project_id == project_id)
            .scalar()
        )

        if not actual_hours:
            continue

        rows.append(
            {
                "num_features": len(features),
                "num_tasks": int(task_count or 0),
                "num_roles": int(role_count or 0),
                "has_payment": 1 if any("PAYMENT" in n for n in feature_names) else 0,
                "has_admin": (
                    1
                    if any("ADMIN" in n or "DASHBOARD" in n for n in feature_names)
                    else 0
                ),
                "has_mobile": 1 if any("MOBILE" in n for n in feature_names) else 0,
                "has_realtime": (
                    1
                    if any("REAL_TIME" in n or "TRACKING" in n for n in feature_names)
                    else 0
                ),
                "num_integrations": integration_count,
                "complexity_score": round(complexity_score, 1),
                "actual_hours": round(float(actual_hours), 1),
            }
        )

    return rows


def submit_feedback(
    db: Session,
    project_id: uuid.UUID,
    user_id: uuid.UUID,
    organization_id: uuid.UUID,
    actual_hours: float,
    task_id: uuid.UUID = None,
    estimated_hours: float = None,
    notes: str = None,
):
    project = project_repository.get_project(db, project_id)
    if not project:
        raise FeedbackError("Project not found")

    if task_id:
        task = db.query(Task).filter(Task.id == task_id).first()
        if not task:
            raise FeedbackError("Task not found")
        feature = db.query(Feature).filter(Feature.id == task.feature_id).first()
        if not feature or feature.project_id != project_id:
            raise FeedbackError("Task does not belong to this project")
        if estimated_hours is None:
            estimated_hours = task.base_hours

    if estimated_hours is not None and estimated_hours < 0:
        raise FeedbackError("Estimated hours cannot be negative")

    if actual_hours <= 0:
        raise FeedbackError("Actual hours must be greater than zero")

    feedback = feedback_repository.create_feedback(
        db=db,
        project_id=project_id,
        organization_id=organization_id,
        actual_hours=actual_hours,
        user_id=user_id,
        task_id=task_id,
        estimated_hours=estimated_hours,
        notes=notes,
    )

    return feedback


def get_project_feedback(db: Session, project_id: uuid.UUID):
    project = project_repository.get_project(db, project_id)
    if not project:
        raise FeedbackError("Project not found")

    return feedback_repository.list_feedback_by_project(db, project_id)


def get_task_feedback(db: Session, task_id: uuid.UUID):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise FeedbackError("Task not found")

    return feedback_repository.list_feedback_by_task(db, task_id)


def get_feedback_detail(db: Session, feedback_id: uuid.UUID):
    feedback = feedback_repository.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise FeedbackError("Feedback not found")
    return feedback


def get_project_feedback_summary(db: Session, project_id: uuid.UUID):
    project = project_repository.get_project(db, project_id)
    if not project:
        raise FeedbackError("Project not found")

    return feedback_repository.get_feedback_summary(db, project_id)


def delete_feedback_item(db: Session, feedback_id: uuid.UUID):
    feedback = feedback_repository.get_feedback_by_id(db, feedback_id)
    if not feedback:
        raise FeedbackError("Feedback not found")

    deleted = feedback_repository.delete_feedback(db, feedback_id)
    if not deleted:
        raise FeedbackError("Failed to delete feedback")
    return True

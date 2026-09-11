from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from app.models.feedback import Feedback
import uuid


def create_feedback(
    db: Session,
    project_id: uuid.UUID,
    actual_hours: float,
    organization_id: uuid.UUID,
    user_id: uuid.UUID = None,
    task_id: uuid.UUID = None,
    estimated_hours: float = None,
    notes: str = None,
):
    new_feedback = Feedback(
        project_id=project_id,
        organization_id=organization_id,
        user_id=user_id,
        task_id=task_id,
        estimated_hours=estimated_hours,
        actual_hours=actual_hours,
        notes=notes,
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


def list_feedback_by_project(db: Session, project_id: uuid.UUID):
    return (
        db.query(Feedback)
        .filter(Feedback.project_id == project_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


def list_feedback_by_task(db: Session, task_id: uuid.UUID):
    return (
        db.query(Feedback)
        .filter(Feedback.task_id == task_id)
        .order_by(Feedback.created_at.desc())
        .all()
    )


def get_feedback_by_id(db: Session, feedback_id: uuid.UUID):
    return db.query(Feedback).filter(Feedback.id == feedback_id).first()


def get_feedback_summary(db: Session, project_id: uuid.UUID):
    result = (
        db.query(
            sa_func.count(Feedback.id).label("total_feedback_count"),
            sa_func.sum(Feedback.estimated_hours).label("total_estimated_hours"),
            sa_func.sum(Feedback.actual_hours).label("total_actual_hours"),
        )
        .filter(Feedback.project_id == project_id)
        .first()
    )

    total_count = result.total_feedback_count or 0
    total_estimated = (
        float(result.total_estimated_hours)
        if result.total_estimated_hours
        else None
    )
    total_actual = (
        float(result.total_actual_hours)
        if result.total_actual_hours
        else 0.0
    )

    avg_deviation = None
    if total_estimated and total_estimated > 0 and total_count > 0:
        avg_deviation = round(
            ((total_actual - total_estimated) / total_estimated) * 100,
            2,
        )

    return {
        "project_id": project_id,
        "total_feedback_count": total_count,
        "total_estimated_hours": total_estimated,
        "total_actual_hours": total_actual,
        "average_deviation_percent": avg_deviation,
    }


def delete_feedback(db: Session, feedback_id: uuid.UUID):
    feedback = db.query(Feedback).filter(Feedback.id == feedback_id).first()
    if feedback:
        db.delete(feedback)
        db.commit()
        return True
    return False

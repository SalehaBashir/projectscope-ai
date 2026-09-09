from sqlalchemy.orm import Session
import uuid

from app.models import (
    Requirement,
    Feature,
    Task,
    Risk,
    Estimate,
)
from app.services import (
    ai_analysis_service,
    task_service,
    risk_service,
    estimation_service,
)
from app.repositories import estimate_repository


class RecalculationError(Exception):
    pass


def _clear_project_artifacts(db: Session, project_id: uuid.UUID):
    """Remove previously generated analysis artifacts so a recalculation
    starts from a clean slate. The project record itself is preserved."""
    db.query(Estimate).filter(Estimate.project_id == project_id).delete()

    task_ids = [
        t.id
        for t in db.query(Task)
        .join(Feature, Feature.id == Task.feature_id)
        .filter(Feature.project_id == project_id)
        .all()
    ]
    db.query(Task).filter(Task.id.in_(task_ids)).delete(
        synchronize_session=False
    ) if task_ids else None

    feature_ids = [
        f.id
        for f in db.query(Feature).filter(Feature.project_id == project_id).all()
    ]
    db.query(Feature).filter(Feature.id.in_(feature_ids)).delete(
        synchronize_session=False
    ) if feature_ids else None

    db.query(Risk).filter(Risk.project_id == project_id).delete()
    db.query(Requirement).filter(Requirement.project_id == project_id).delete()

    db.commit()


def recalculate_project(
    db: Session,
    project_id: uuid.UUID,
    description: str = None,
    budget: str = None,
    platform: str = None,
):
    """
    Re-run the full analysis pipeline for a revised project.

    Optionally accepts a new description/budget/platform. When provided they
    update the project record before re-analysis, enabling the guide's
    'revise requirements and recalculate' workflow.
    """
    from app.repositories import project_repository

    project = project_repository.get_project(db, project_id)
    if not project:
        raise RecalculationError("Project not found")

    if description is not None:
        project.description = description
    if budget is not None:
        project.budget = budget
    if platform is not None:
        project.platform = platform
    db.commit()
    db.refresh(project)

    _clear_project_artifacts(db, project_id)

    try:
        ai_analysis_service.analyze_and_save(
            db,
            project_id=project_id,
            description=project.description,
            budget=project.budget,
            platform=project.platform,
        )
        task_service.generate_tasks_for_project(db, project_id)
        risk_service.generate_risks_for_project(db, project_id)
        estimate_result = estimation_service.calculate_estimate(db, project_id)
        estimate_repository.save_estimate(
            db,
            project_id,
            estimate_result["min_hours"],
            estimate_result["expected_hours"],
            estimate_result["max_hours"],
            estimate_result["complexity_score"],
            estimate_result["min_cost"],
            estimate_result["expected_cost"],
            estimate_result["max_cost"],
            estimate_result["timeline_weeks_expected"],
        )
    except Exception as e:
        db.rollback()
        raise RecalculationError(f"Recalculation failed: {e}")

    return {
        "project": project,
        "estimate": estimate_result,
    }

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services.estimation_service import calculate_estimate
from app.repositories import estimate_repository
import uuid

router = APIRouter(prefix="/projects", tags=["Estimation"])


@router.post("/{project_id}/estimate")
def estimate_project(project_id: uuid.UUID, db: Session = Depends(get_db)):
    result = calculate_estimate(db, project_id)

    saved = estimate_repository.save_estimate(
        db,
        project_id,
        result["min_hours"],
        result["expected_hours"],
        result["max_hours"],
        result["complexity_score"],
        result["min_cost"],
        result["expected_cost"],
        result["max_cost"],
        result["timeline_weeks_expected"],
    )

    return {
        "min_hours": saved.min_hours,
        "expected_hours": saved.expected_hours,
        "max_hours": saved.max_hours,
        "ml_predicted_hours": result["ml_predicted_hours"],
        "hybrid_expected_hours": result["hybrid_expected_hours"],
        "complexity_score": saved.complexity_score,
        "complexity_explanation": result["complexity_explanation"],
        "min_cost": saved.min_cost,
        "expected_cost": saved.expected_cost,
        "max_cost": saved.max_cost,
        "timeline_weeks_min": result["timeline_weeks_min"],
        "timeline_weeks_expected": saved.timeline_weeks,
        "timeline_weeks_max": result["timeline_weeks_max"],
        "task_count": result["task_count"],
    }
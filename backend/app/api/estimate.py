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
    )

    return {
        "min_hours": saved.min_hours,
        "expected_hours": saved.expected_hours,
        "max_hours": saved.max_hours,
        "complexity_score": saved.complexity_score,
        "task_count": result["task_count"],
    }
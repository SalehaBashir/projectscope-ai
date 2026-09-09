from sqlalchemy.orm import Session
import uuid

from app.estimation.risk_engine import generate_project_risks
from app.estimation.risk_rules import get_complexity_risk
from app.repositories import risk_repository
from app.services.estimation_service import calculate_estimate


def generate_risks_for_project(db: Session, project_id: uuid.UUID):
    # Calculate current project complexity
    estimate_result = calculate_estimate(db, project_id)

    complexity_score = estimate_result.get("complexity_score", 0)

    # Generate risks using the centralized risk engine
    risks_to_create = generate_project_risks(
        db=db,
        project_id=project_id,
        complexity_score=complexity_score,
    )

    # Replace previous risks with the latest generated risks
    risk_repository.clear_risks(db, project_id)

    return risk_repository.create_risks(
        db,
        project_id,
        risks_to_create,
    )
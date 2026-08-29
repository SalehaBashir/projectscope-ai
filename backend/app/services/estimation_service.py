from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.feature import Feature
from app.models.requirement import Requirement
from app.estimation.rules import (
    get_complexity_multiplier,
    get_integration_multiplier,
    get_scale_multiplier,
)
import uuid


def calculate_estimate(db: Session, project_id: uuid.UUID):
    features = db.query(Feature).filter(Feature.project_id == project_id).all()
    feature_ids = [f.id for f in features]
    complexity_by_feature = {f.id: f.complexity for f in features}

    tasks = db.query(Task).filter(Task.feature_id.in_(feature_ids)).all()

    # Count integrations from features (rough proxy: features containing "PAYMENT", "MESSAGING", etc.)
    integration_features = [
        f for f in features
        if any(k in f.canonical_name for k in ["PAYMENT", "MESSAGING", "SEARCH", "MAP", "NOTIFICATION"])
    ]
    integration_multiplier = get_integration_multiplier(len(integration_features))

    # Look up the "scale" answer if the user provided one
    scale_requirement = (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .filter(Requirement.description.like("ANSWER[scale]%"))
        .first()
    )
    scale_text = scale_requirement.description if scale_requirement else ""
    scale_multiplier = get_scale_multiplier(scale_text)

    total_expected_hours = 0.0
    total_min_hours = 0.0
    total_max_hours = 0.0

    for task in tasks:
        complexity = complexity_by_feature.get(task.feature_id, "medium")
        complexity_mult = get_complexity_multiplier(complexity)

        expected = task.base_hours * complexity_mult * integration_multiplier * scale_multiplier
        min_hours = task.base_hours * 1.0  # best case: no extra multipliers
        max_hours = expected * 1.25  # worst case buffer

        total_expected_hours += expected
        total_min_hours += min_hours
        total_max_hours += max_hours

    # Simple complexity score out of 100, based on feature complexity distribution
    complexity_values = {"low": 20, "medium": 50, "high": 85}
    if features:
        complexity_score = sum(complexity_values.get(f.complexity, 50) for f in features) / len(features)
    else:
        complexity_score = 0

    return {
        "min_hours": round(total_min_hours, 1),
        "expected_hours": round(total_expected_hours, 1),
        "max_hours": round(total_max_hours, 1),
        "complexity_score": round(complexity_score, 1),
        "task_count": len(tasks),
    }
from sqlalchemy.orm import Session
from app.models.task import Task
from app.models.feature import Feature
from app.models.requirement import Requirement
from app.models.role import Role
from app.estimation.rules import (
    get_complexity_multiplier,
    get_integration_multiplier,
    get_scale_multiplier,
)
from app.ml.predictor import predict_effort_hours
import uuid

WEEKLY_HOURS_PER_ROLE = 30


def calculate_estimate(db: Session, project_id: uuid.UUID):
    features = db.query(Feature).filter(Feature.project_id == project_id).all()
    feature_ids = [f.id for f in features]
    complexity_by_feature = {f.id: f.complexity for f in features}
    feature_names = {f.canonical_name for f in features}

    tasks = db.query(Task).filter(Task.feature_id.in_(feature_ids)).all()

    integration_features = [
        f for f in features
        if any(k in f.canonical_name for k in ["PAYMENT", "MESSAGING", "SEARCH", "MAP", "NOTIFICATION"])
    ]
    integration_multiplier = get_integration_multiplier(len(integration_features))

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

    total_expected_cost = 0.0
    total_min_cost = 0.0
    total_max_cost = 0.0

    roles_used = set()

    for task in tasks:
        complexity = complexity_by_feature.get(task.feature_id, "medium")
        complexity_mult = get_complexity_multiplier(complexity)

        expected = task.base_hours * complexity_mult * integration_multiplier * scale_multiplier
        min_hours = task.base_hours * 1.0
        max_hours = expected * 1.25

        total_expected_hours += expected
        total_min_hours += min_hours
        total_max_hours += max_hours

        role = db.query(Role).filter(Role.id == task.role_id).first() if task.role_id else None
        hourly_rate = role.hourly_rate if role else 12.0

        if role:
            roles_used.add(role.id)

        total_expected_cost += expected * hourly_rate
        total_min_cost += min_hours * hourly_rate
        total_max_cost += max_hours * hourly_rate

    complexity_values = {"low": 20, "medium": 50, "high": 85}
    if features:
        complexity_score = sum(complexity_values.get(f.complexity, 50) for f in features) / len(features)
    else:
        complexity_score = 0

    team_size = max(len(roles_used), 1)
    weekly_capacity = team_size * WEEKLY_HOURS_PER_ROLE

    timeline_weeks_expected = total_expected_hours / weekly_capacity
    timeline_weeks_min = total_min_hours / weekly_capacity
    timeline_weeks_max = total_max_hours / weekly_capacity

    ml_features = {
        "num_features": len(features),
        "num_tasks": len(tasks),
        "num_roles": len(roles_used),
        "has_payment": 1 if any("PAYMENT" in n for n in feature_names) else 0,
        "has_admin": 1 if any("ADMIN" in n or "DASHBOARD" in n for n in feature_names) else 0,
        "has_mobile": 1 if any("MOBILE" in n for n in feature_names) else 0,
        "has_realtime": 1 if any("REAL_TIME" in n or "TRACKING" in n for n in feature_names) else 0,
        "num_integrations": len(integration_features),
        "complexity_score": complexity_score,
    }

    try:
        ml_predicted_hours = predict_effort_hours(ml_features)
    except Exception:
        ml_predicted_hours = None

    if ml_predicted_hours is not None:
        hybrid_expected_hours = round((0.6 * total_expected_hours) + (0.4 * ml_predicted_hours), 1)
    else:
        hybrid_expected_hours = round(total_expected_hours, 1)

    return {
        "min_hours": round(total_min_hours, 1),
        "expected_hours": round(total_expected_hours, 1),
        "max_hours": round(total_max_hours, 1),
        "ml_predicted_hours": ml_predicted_hours,
        "hybrid_expected_hours": hybrid_expected_hours,
        "min_cost": round(total_min_cost, 2),
        "expected_cost": round(total_expected_cost, 2),
        "max_cost": round(total_max_cost, 2),
        "timeline_weeks_min": round(timeline_weeks_min, 1),
        "timeline_weeks_expected": round(timeline_weeks_expected, 1),
        "timeline_weeks_max": round(timeline_weeks_max, 1),
        "complexity_score": round(complexity_score, 1),
        "task_count": len(tasks),
    }
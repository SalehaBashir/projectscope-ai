from app.estimation.risk_engine import generate_project_risks
from app.estimation.timeline import calculate_task_schedule
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

RULE_WEIGHT = 0.6
ML_WEIGHT = 0.4
MODEL_VERSION = "v1"


def calculate_complexity_score(
    features,
    feature_names,
    integration_features,
    requirements,
    roles_used,
):
    """
    Phase 12:
    Transparent rule-based project complexity score from 0-100.

    Factors:
    - Feature count
    - Feature complexity
    - Development/user roles
    - External integrations
    - Payment
    - Real-time functionality
    - Mobile platform
    - Security
    - Database complexity
    - Scalability
    - AI/ML
    """

    # Combine available structured project information.
    project_text = " ".join(
        [
            str(f.canonical_name or "")
            + " "
            + str(f.description or "")
            for f in features
        ]
        + [
            str(r.description or "")
            for r in requirements
        ]
    ).upper()

    score = 0.0
    reasons = []

    # ---------------------------------------------------------
    # 1. Number of features: 0-15 points
    # ---------------------------------------------------------
    feature_count = len(features)

    if feature_count >= 20:
        feature_points = 15
    elif feature_count >= 15:
        feature_points = 12
    elif feature_count >= 10:
        feature_points = 9
    elif feature_count >= 5:
        feature_points = 5
    else:
        feature_points = feature_count

    score += feature_points

    if feature_count > 0:
        reasons.append(f"{feature_count} features")

    # ---------------------------------------------------------
    # 2. Feature complexity: 0-20 points
    # ---------------------------------------------------------
    complexity_values = {
        "low": 20,
        "medium": 50,
        "high": 85,
    }

    if features:
        average_feature_complexity = (
            sum(
                complexity_values.get(
                    f.complexity,
                    50,
                )
                for f in features
            )
            / len(features)
        )
    else:
        average_feature_complexity = 0

    complexity_points = (average_feature_complexity / 100) * 20
    score += complexity_points

    if average_feature_complexity >= 70:
        reasons.append("high feature complexity")
    elif average_feature_complexity >= 40:
        reasons.append("medium feature complexity")

    # ---------------------------------------------------------
    # 3. Development/user roles: 0-10 points
    # ---------------------------------------------------------
    role_count = len(roles_used)

    if role_count >= 8:
        role_points = 10
    elif role_count >= 5:
        role_points = 8
    elif role_count >= 3:
        role_points = 5
    elif role_count >= 2:
        role_points = 3
    else:
        role_points = 0

    score += role_points

    if role_count > 1:
        reasons.append(f"{role_count} development roles")

    # ---------------------------------------------------------
    # 4. External integrations: 0-10 points
    # ---------------------------------------------------------
    integration_count = len(integration_features)

    if integration_count >= 5:
        integration_points = 10
    elif integration_count >= 3:
        integration_points = 7
    elif integration_count >= 1:
        integration_points = 4
    else:
        integration_points = 0

    score += integration_points

    if integration_count > 0:
        reasons.append(
            f"{integration_count} external integration-related features"
        )

    # ---------------------------------------------------------
    # 5. Payment: 10 points
    # ---------------------------------------------------------
    has_payment = "PAYMENT" in project_text

    if has_payment:
        score += 10
        reasons.append("payment processing")

    # ---------------------------------------------------------
    # 6. Real-time functionality: 8 points
    # ---------------------------------------------------------
    realtime_keywords = [
        "REAL_TIME",
        "REAL-TIME",
        "REAL TIME",
        "WEBSOCKET",
        "LIVE TRACKING",
        "LIVE LOCATION",
        "CHAT",
        "MESSAGING",
        "NOTIFICATION",
    ]

    has_realtime = any(
        keyword in project_text
        for keyword in realtime_keywords
    )

    if has_realtime:
        score += 8
        reasons.append("real-time or live functionality")

    # ---------------------------------------------------------
    # 7. Mobile platform: 7 points
    # ---------------------------------------------------------
    has_mobile = (
        "MOBILE" in project_text
        or "IOS" in project_text
        or "ANDROID" in project_text
    )

    if has_mobile:
        score += 7
        reasons.append("mobile application support")

    # ---------------------------------------------------------
    # 8. Security: 7 points
    # ---------------------------------------------------------
    security_keywords = [
        "SECURITY",
        "SECURE",
        "AUTHENTICATION",
        "AUTHORIZATION",
        "ENCRYPTION",
        "PCI",
        "GDPR",
        "2FA",
        "MFA",
        "PASSWORD",
        "ROLE-BASED ACCESS",
    ]

    has_security = any(
        keyword in project_text
        for keyword in security_keywords
    )

    if has_security:
        score += 7
        reasons.append("security/authentication requirements")

    # ---------------------------------------------------------
    # 9. Database complexity: 5 points
    # ---------------------------------------------------------
    database_keywords = [
        "DATABASE",
        "POSTGRES",
        "MYSQL",
        "MONGODB",
        "RELATIONAL",
        "DATA MODEL",
        "TRANSACTION",
        "MULTIPLE ENTITIES",
    ]

    has_database_complexity = any(
        keyword in project_text
        for keyword in database_keywords
    )

    if has_database_complexity:
        score += 5
        reasons.append("database/data complexity")

    # ---------------------------------------------------------
    # 10. Scalability: 5 points
    # ---------------------------------------------------------
    scalability_keywords = [
        "SCALE",
        "SCALABILITY",
        "HIGH TRAFFIC",
        "MILLIONS OF USERS",
        "LARGE SCALE",
        "CONCURRENT USERS",
        "PERFORMANCE",
    ]

    has_scalability = any(
        keyword in project_text
        for keyword in scalability_keywords
    )

    if has_scalability:
        score += 5
        reasons.append("scalability requirements")

    # ---------------------------------------------------------
    # 11. AI/ML: 3 points
    # ---------------------------------------------------------
    ai_keywords = [
        "AI",
        "ARTIFICIAL INTELLIGENCE",
        "MACHINE LEARNING",
        "ML",
        "LLM",
        "GPT",
        "GENAI",
        "PREDICTION",
        "RECOMMENDATION",
        "COMPUTER VISION",
    ]

    has_ai_ml = any(
        keyword in project_text
        for keyword in ai_keywords
    )

    if has_ai_ml:
        score += 3
        reasons.append("AI/ML functionality")

    # ---------------------------------------------------------
    # Final score: always 0-100
    # ---------------------------------------------------------
    score = min(round(score, 1), 100.0)

    if score >= 70:
        complexity_level = "high"
    elif score >= 40:
        complexity_level = "medium"
    else:
        complexity_level = "low"

    if reasons:
        explanation = (
            f"Complexity is {complexity_level} with a score of "
            f"{score}/100 because the project has "
            + ", ".join(reasons)
            + "."
        )
    else:
        explanation = (
            f"Complexity is {complexity_level} with a score of "
            f"{score}/100 based on the available project information."
        )

    return score, explanation


def calculate_estimate(db: Session, project_id: uuid.UUID):
    features = (
        db.query(Feature)
        .filter(Feature.project_id == project_id)
        .all()
    )

    feature_ids = [f.id for f in features]

    complexity_by_feature = {
        f.id: f.complexity
        for f in features
    }

    feature_names = {
        f.canonical_name.upper()
        for f in features
    }

    requirements = (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .all()
    )

    tasks = (
        db.query(Task)
        .filter(Task.feature_id.in_(feature_ids))
        .all()
    )

    integration_features = [
        f
        for f in features
        if any(
            k in f.canonical_name.upper()
            for k in [
                "PAYMENT",
                "MESSAGING",
                "SEARCH",
                "MAP",
                "NOTIFICATION",
            ]
        )
    ]

    integration_multiplier = get_integration_multiplier(
        len(integration_features)
    )

    scale_requirement = (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .filter(
            Requirement.description.like("ANSWER[scale]%")
        )
        .first()
    )

    scale_text = (
        scale_requirement.description
        if scale_requirement
        else ""
    )

    scale_multiplier = get_scale_multiplier(scale_text)

    total_expected_hours = 0.0
    total_min_hours = 0.0
    total_max_hours = 0.0

    total_expected_cost = 0.0
    total_min_cost = 0.0
    total_max_cost = 0.0

    roles_used = set()

    for task in tasks:
        complexity = complexity_by_feature.get(
            task.feature_id,
            "medium",
        )

        complexity_mult = get_complexity_multiplier(
            complexity
        )

        expected = (
            task.base_hours
            * complexity_mult
            * integration_multiplier
            * scale_multiplier
        )

        min_hours = task.base_hours * 1.0
        max_hours = expected * 1.25

        total_expected_hours += expected
        total_min_hours += min_hours
        total_max_hours += max_hours

        role = (
            db.query(Role)
            .filter(Role.id == task.role_id)
            .first()
            if task.role_id
            else None
        )

        hourly_rate = (
            role.hourly_rate
            if role
            else 12.0
        )

        if role:
            roles_used.add(role.id)

        total_expected_cost += (
            expected * hourly_rate
        )

        total_min_cost += (
            min_hours * hourly_rate
        )

        total_max_cost += (
            max_hours * hourly_rate
        )

    # ---------------------------------------------------------
    # Phase 12: Multi-factor complexity scoring
    # ---------------------------------------------------------
    complexity_score, complexity_explanation = (
        calculate_complexity_score(
            features=features,
            feature_names=feature_names,
            integration_features=integration_features,
            requirements=requirements,
            roles_used=roles_used,
        )
    )

    # ---------------------------------------------------------
    # Phase 11: dependency-aware task scheduling
    # ---------------------------------------------------------
    schedule = calculate_task_schedule(
        db=db,
        tasks=tasks,
    )

    # ---------------------------------------------------------
    # Team capacity
    # ---------------------------------------------------------
    team_size = max(
        len(roles_used),
        1,
    )

    weekly_capacity = (
        team_size * WEEKLY_HOURS_PER_ROLE
    )

    # ---------------------------------------------------------
    # ML prediction features
    # ---------------------------------------------------------
    project_text = " ".join(
        [
            str(f.canonical_name or "")
            + " "
            + str(f.description or "")
            for f in features
        ]
        + [
            str(r.description or "")
            for r in requirements
        ]
    ).upper()

    ml_features = {
        "num_features": len(features),
        "num_tasks": len(tasks),
        "num_roles": len(roles_used),
        "has_payment": (
            1
            if "PAYMENT" in project_text
            else 0
        ),
        "has_admin": (
            1
            if (
                "ADMIN" in project_text
                or "DASHBOARD" in project_text
            )
            else 0
        ),
        "has_mobile": (
            1
            if (
                "MOBILE" in project_text
                or "IOS" in project_text
                or "ANDROID" in project_text
            )
            else 0
        ),
        "has_realtime": (
            1
            if (
                "REAL_TIME" in project_text
                or "REAL-TIME" in project_text
                or "TRACKING" in project_text
                or "WEBSOCKET" in project_text
                or "MESSAGING" in project_text
            )
            else 0
        ),
        "num_integrations": len(
            integration_features
        ),
        "complexity_score": complexity_score,
    }

    try:
        ml_predicted_hours = predict_effort_hours(
            ml_features
        )
    except Exception:
        ml_predicted_hours = None

    if ml_predicted_hours is not None:
        hybrid_expected_hours = round(
            (RULE_WEIGHT * total_expected_hours)
            + (ML_WEIGHT * ml_predicted_hours),
            1,
        )
    else:
        hybrid_expected_hours = round(
            total_expected_hours,
            1,
        )

    # ---------------------------------------------------------
    # Timeline
    # ---------------------------------------------------------
    timeline_weeks_min = (
        total_min_hours / weekly_capacity
    )

    timeline_weeks_max = (
        total_max_hours / weekly_capacity
    )

    timeline_weeks_expected = (
        hybrid_expected_hours / weekly_capacity
    )
    risks = generate_project_risks(
    db=db,
    project_id=project_id,
    complexity_score=complexity_score,
    )

    return {
        "min_hours": round(
            total_min_hours,
            1,
        ),
        "expected_hours": hybrid_expected_hours,
        "max_hours": round(
            total_max_hours,
            1,
        ),
        "ml_predicted_hours": ml_predicted_hours,
        "hybrid_expected_hours": hybrid_expected_hours,
        "min_cost": round(
            total_min_cost,
            2,
        ),
        "expected_cost": round(
            total_expected_cost,
            2,
        ),
        "max_cost": round(
            total_max_cost,
            2,
        ),
        "timeline_weeks_min": round(
            timeline_weeks_min,
            1,
        ),
        "timeline_weeks_expected": round(
            timeline_weeks_expected,
            1,
        ),
        "timeline_weeks_max": round(
            timeline_weeks_max,
            1,
        ),
        "complexity_score": complexity_score,
        "complexity_explanation": complexity_explanation,
        "task_count": len(tasks),
        "schedule": schedule,
        "risks": risks,
    }
from sqlalchemy.orm import Session
from app.repositories import feature_repository, requirement_repository, risk_repository
from app.estimation.risk_rules import (
    RISK_TEMPLATES,
    GENERIC_RISKS,
    get_integration_risk,
    get_scale_risk,
    get_complexity_risk,
)
from app.services.estimation_service import calculate_estimate
import uuid


def generate_risks_for_project(db: Session, project_id: uuid.UUID):
    features = feature_repository.list_features(db, project_id)
    feature_names = {f.canonical_name for f in features}

    risks_to_create = []
    matched_keywords = set()

# Feature-based risks (avoid duplicate risks with the same description)
    seen_descriptions = set()
    for template in RISK_TEMPLATES:
        if template["description"] in seen_descriptions:
            continue
        if any(template["keyword"] in name for name in feature_names):
            risks_to_create.append({
                "description": template["description"],
                "probability": template["probability"],
                "impact": template["impact"],
                "mitigation": template["mitigation"],
            })
            seen_descriptions.add(template["description"])

    # Integration risk
    integration_features = [
        f for f in features
        if any(k in f.canonical_name for k in ["PAYMENT", "MESSAGING", "SEARCH", "MAP", "NOTIFICATION"])
    ]
    integration_risk = get_integration_risk(len(integration_features))
    if integration_risk:
        risks_to_create.append(integration_risk)

    # Scale risk (from Day 5 follow-up answer)
    scale_requirement = (
        db.query(requirement_repository.Requirement)
        .filter(requirement_repository.Requirement.project_id == project_id)
        .filter(requirement_repository.Requirement.description.like("ANSWER[scale]%"))
        .first()
    )
    scale_text = scale_requirement.description if scale_requirement else ""
    scale_risk = get_scale_risk(scale_text)
    if scale_risk:
        risks_to_create.append(scale_risk)

    # Complexity risk (uses the estimate calculation from Day 7-8)
    estimate_result = calculate_estimate(db, project_id)
    complexity_risk = get_complexity_risk(estimate_result["complexity_score"])
    if complexity_risk:
        risks_to_create.append(complexity_risk)

    # Always include generic project risks
    risks_to_create.extend(GENERIC_RISKS)

    risk_repository.clear_risks(db, project_id)
    return risk_repository.create_risks(db, project_id, risks_to_create)
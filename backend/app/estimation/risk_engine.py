from sqlalchemy.orm import Session

from app.models.feature import Feature
from app.models.requirement import Requirement

from app.estimation.risk_rules import (
    RISK_TEMPLATES,
    GENERIC_RISKS,
    get_integration_risk,
    get_scale_risk,
    get_complexity_risk,
)


PROBABILITY_VALUES = {"low": 1, "medium": 2, "high": 3}
IMPACT_VALUES = {"low": 1, "medium": 2, "high": 3}


def severity_for_score(risk_score: float) -> str:
    if risk_score <= 2:
        return "low"
    if risk_score <= 4:
        return "medium"
    return "high"


def category_for_description(description: str) -> str:
    text = (description or "").upper()
    if any(k in text for k in ("PAYMENT", "FRAUD", "CHARG", "PCI")):
        return "payment"
    if any(k in text for k in ("SECURITY", "ACCESS CONTROL", "MISCONFIGUR")):
        return "security"
    if any(k in text for k in ("SCALE", "CONCURRENT", "LOAD")):
        return "scalability"
    if any(k in text for k in ("INTEGRATION", "THIRD-PARTY", "EXTERNAL", "PROVIDER")):
        return "integration"
    if any(k in text for k in ("COMPLEXITY", "SCHEDULE", "BUDGET", "OVERRUN")):
        return "complexity"
    if any(k in text for k in ("REQUIREMENT", "SCOPE", "STAKEHOLDER", "EVOLVE")):
        return "requirements"
    return "technical"


def enrich_risk(risk: dict) -> dict:
    probability_value = PROBABILITY_VALUES.get(
        (risk.get("probability") or "").lower(), 2
    )
    impact_value = IMPACT_VALUES.get((risk.get("impact") or "").lower(), 2)
    risk_score = probability_value * impact_value

    return {
        "description": risk["description"],
        "probability": risk["probability"],
        "impact": risk["impact"],
        "mitigation": risk["mitigation"],
        "category": category_for_description(risk["description"]),
        "severity": severity_for_score(risk_score),
        "risk_score": risk_score,
    }


def generate_project_risks(
    db: Session,
    project_id,
    complexity_score: float = 0,
):
    features = (
        db.query(Feature)
        .filter(Feature.project_id == project_id)
        .all()
    )

    requirements = (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .all()
    )

    project_text_parts = []

    for feature in features:
        project_text_parts.append(feature.canonical_name or "")
        project_text_parts.append(feature.description or "")

    for requirement in requirements:
        project_text_parts.append(requirement.description or "")

    project_text = " ".join(project_text_parts).upper()

    risks = []

    # Keyword-based risks
    for template in RISK_TEMPLATES:
        keyword = template["keyword"]

        if keyword in project_text:
            risks.append(
                {
                    "description": template["description"],
                    "probability": template["probability"],
                    "impact": template["impact"],
                    "mitigation": template["mitigation"],
                }
            )

    # Integration risk
    integration_keywords = [
        "PAYMENT",
        "MESSAGING",
        "SEARCH",
        "MAP",
        "NOTIFICATION",
        "INTEGRATION",
    ]

    integration_count = sum(
        1
        for feature in features
        if any(
            keyword in (feature.canonical_name or "").upper()
            for keyword in integration_keywords
        )
    )

    integration_risk = get_integration_risk(integration_count)

    if integration_risk:
        risks.append(integration_risk)

    # Scale risk
    scale_text = " ".join(
        requirement.description or ""
        for requirement in requirements
        if "ANSWER[scale]" in (requirement.description or "")
    )

    scale_risk = get_scale_risk(scale_text)

    if scale_risk:
        risks.append(scale_risk)

    # Complexity risk
    complexity_risk = get_complexity_risk(complexity_score)

    if complexity_risk:
        risks.append(complexity_risk)

    # Generic risk
    risks.extend(GENERIC_RISKS)

    # Remove duplicate risks
    unique_risks = []
    seen = set()

    for risk in risks:
        key = risk["description"]

        if key not in seen:
            seen.add(key)
            unique_risks.append(risk)

    return [enrich_risk(risk) for risk in unique_risks]
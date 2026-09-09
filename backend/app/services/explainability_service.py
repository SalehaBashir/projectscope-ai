"""
Phase 18 - Explainable AI

Generates grounded "Why?" explanations from structured project facts.
No explanation is generated from unsupported assumptions.
"""


def build_estimation_explanation(
    rule_hours: float,
    ml_hours: float | None,
    llm_hours: float | None,
    final_hours: float,
    confidence: float,
    task_count: int,
    feature_count: int,
    role_count: int,
    complexity_score: float,
):
    sources = []

    if rule_hours is not None:
        sources.append(
            f"rule-based estimate is {rule_hours:.1f} hours"
        )

    if ml_hours is not None:
        sources.append(
            f"ML estimate is {ml_hours:.1f} hours"
        )

    if llm_hours is not None:
        sources.append(
            f"LLM advisory estimate is {llm_hours:.1f} hours"
        )

    return {
        "why": (
            f"The final estimate is {final_hours:.1f} hours because "
            + ", ".join(sources)
            + ". The reconciliation policy gives priority to the "
            "deterministic baseline and only uses available model "
            "signals when their quality is acceptable."
        ),
        "factors": [
            f"{feature_count} features",
            f"{task_count} development tasks",
            f"{role_count} development roles",
            f"complexity score {complexity_score}/100",
        ],
        "confidence_why": (
            f"Confidence is {confidence:.3f} based on the available "
            "structured project data and model reliability."
        ),
    }
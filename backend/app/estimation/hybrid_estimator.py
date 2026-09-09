"""
Phase 17 - Hybrid Estimation

Reconciliation policy:
1. Deterministic rule-based estimation is the primary baseline.
2. ML prediction is used as a secondary evidence source.
3. LLM estimation is treated as advisory only.
4. We do NOT blindly average all estimates.
5. When model/data quality is weak, deterministic estimation receives
   higher weight.
6. The final estimate is clipped to a reasonable historical-style range.
7. Confidence reflects data quality and ML model reliability.
8. Every result carries an estimator version for reproducibility.
"""

from dataclasses import dataclass


ESTIMATOR_VERSION = "hybrid-v1.0"

# Normal operating weights.
RULE_WEIGHT = 0.50
ML_WEIGHT = 0.30
LLM_WEIGHT = 0.20

# Conservative range around final expected estimate.
MIN_RANGE_FACTOR = 0.86
MAX_RANGE_FACTOR = 1.23


@dataclass
class HybridEstimate:
    expected_hours: float
    min_hours: float
    max_hours: float
    confidence: float
    rule_hours: float
    ml_hours: float | None
    llm_hours: float | None
    estimator_version: str
    reconciliation_policy: str


def _safe_number(value):
    try:
        value = float(value)
        if value > 0:
            return value
    except (TypeError, ValueError):
        pass

    return None


def reconcile_estimates(
    rule_hours: float,
    ml_hours: float | None = None,
    llm_hours: float | None = None,
    data_quality: float = 1.0,
    model_performance: float = 0.75,
) -> HybridEstimate:
    """
    Reconcile rule, ML and LLM estimates without blindly averaging them.

    data_quality:
        0.0 - 1.0 indicating quality/completeness of structured inputs.

    model_performance:
        0.0 - 1.0 representing confidence in the trained ML model.
    """

    rule = _safe_number(rule_hours)

    if rule is None:
        raise ValueError("rule_hours must be a positive number")

    ml = _safe_number(ml_hours)
    llm = _safe_number(llm_hours)

    data_quality = max(0.0, min(float(data_quality), 1.0))
    model_performance = max(
        0.0,
        min(float(model_performance), 1.0),
    )

    # Start with deterministic rules as the trusted baseline.
    weights = {
        "rule": RULE_WEIGHT,
        "ml": 0.0,
        "llm": 0.0,
    }

    # ML gets weight only when a prediction exists and the model
    # has acceptable performance.
    if ml is not None and model_performance >= 0.60:
        weights["ml"] = ML_WEIGHT * model_performance

    # LLM is advisory and only receives weight when structured
    # project data is reasonably complete.
    if llm is not None and data_quality >= 0.60:
        weights["llm"] = LLM_WEIGHT * data_quality

    total_weight = sum(weights.values())

    if total_weight <= 0:
        expected = rule
    else:
        expected = (
            (rule * weights["rule"])
            + (ml * weights["ml"] if ml is not None else 0)
            + (llm * weights["llm"] if llm is not None else 0)
        ) / total_weight

    expected = round(expected, 1)

    # Reconciled range.
    min_hours = round(
        expected * MIN_RANGE_FACTOR,
        1,
    )

    max_hours = round(
        expected * MAX_RANGE_FACTOR,
        1,
    )

    # Confidence:
    # - structured data quality
    # - ML model reliability
    # - availability of independent estimates
    confidence = (
        0.45 * data_quality
        + 0.35 * model_performance
        + 0.20
        * (
            1.0
            if ml is not None and llm is not None
            else 0.75
            if ml is not None or llm is not None
            else 0.50
        )
    )

    confidence = round(
        max(0.0, min(confidence, 1.0)),
        3,
    )

    policy = (
        "Deterministic estimation is the baseline. "
        "ML contributes only when model performance is acceptable. "
        "LLM is advisory and contributes only when structured data "
        "quality is sufficient. Missing or low-confidence sources "
        "are excluded rather than blindly averaged."
    )

    return HybridEstimate(
        expected_hours=expected,
        min_hours=min_hours,
        max_hours=max_hours,
        confidence=confidence,
        rule_hours=round(rule, 1),
        ml_hours=round(ml, 1) if ml is not None else None,
        llm_hours=round(llm, 1) if llm is not None else None,
        estimator_version=ESTIMATOR_VERSION,
        reconciliation_policy=policy,
    )
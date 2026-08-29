# Deterministic multipliers — no LLM involvement, pure business rules

COMPLEXITY_MULTIPLIER = {
    "low": 1.0,
    "medium": 1.3,
    "high": 1.7,
}

# Extra % added per external integration beyond the first
INTEGRATION_EXTRA_PER_UNIT = 0.05  # +5% per integration

# Scale keywords → extra multiplier (checked against the "scale" follow-up answer)
SCALE_KEYWORDS = {
    "million": 0.3,
    "thousand": 0.15,
    "hundred": 0.0,
}


def get_complexity_multiplier(complexity: str) -> float:
    return COMPLEXITY_MULTIPLIER.get(complexity, 1.3)  # default to medium


def get_integration_multiplier(integration_count: int) -> float:
    return 1.0 + (INTEGRATION_EXTRA_PER_UNIT * max(0, integration_count - 1))


def get_scale_multiplier(scale_answer: str) -> float:
    if not scale_answer:
        return 1.0
    scale_lower = scale_answer.lower()
    for keyword, extra in SCALE_KEYWORDS.items():
        if keyword in scale_lower:
            return 1.0 + extra
    return 1.0
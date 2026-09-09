MODEL_PRICING_PER_1M = {
    "openai/gpt-oss-120b": {
        "input": 0.15,
        "output": 0.60,
    },
    "openai/gpt-oss-20b": {
        "input": 0.075,
        "output": 0.30,
    },
}


def calculate_ai_cost(
    model: str,
    prompt_tokens: int | float | None,
    completion_tokens: int | float | None,
) -> float | None:
    """Calculate estimated LLM cost in USD."""

    if prompt_tokens is None or completion_tokens is None:
        return None

    pricing = MODEL_PRICING_PER_1M.get(model)

    if pricing is None:
        return None

    input_cost = (float(prompt_tokens) / 1_000_000) * pricing["input"]
    output_cost = (
        float(completion_tokens) / 1_000_000
    ) * pricing["output"]

    return round(input_cost + output_cost, 8)
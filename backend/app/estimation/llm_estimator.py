import json

from app.ai.groq_client import GroqProvider


LLM_ESTIMATOR_VERSION = "llm-v1.0"


SYSTEM_PROMPT = """
You are a software project estimation assistant.

Estimate development effort in hours for the provided project.

Rules:
- Return JSON only.
- Give a realistic expected development effort.
- Do not include project management overhead.
- Do not blindly assume every possible feature.
- Base the estimate only on the provided project information.
- This estimate is advisory and will be reconciled with deterministic
  and ML estimates by another system.

Required JSON format:
{
  "estimated_hours": number,
  "reason": "short explanation"
}
"""


def estimate_with_llm(
    description: str,
    budget: str | None = None,
    platform: str | None = None,
):
    user_prompt = f"""
Project description:
{description}

Budget:
{budget or "Not provided"}

Platform:
{platform or "Not provided"}

Provide the estimated development effort.
"""
    ai_provider = GroqProvider()
    raw_response = ai_provider.generate(
        SYSTEM_PROMPT,
        user_prompt,
    )

    parsed = json.loads(raw_response)

    estimated_hours = float(
        parsed["estimated_hours"]
    )

    if estimated_hours <= 0:
        raise ValueError(
            "LLM returned an invalid effort estimate"
        )

    return {
        "estimated_hours": round(
            estimated_hours,
            1,
        ),
        "reason": str(
            parsed.get(
                "reason",
                "",
            )
        ),
        "version": LLM_ESTIMATOR_VERSION,
    }
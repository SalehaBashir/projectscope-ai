import json
from app.ai.groq_client import call_llm
from app.ai.prompts import REQUIREMENT_ANALYZER_SYSTEM_PROMPT, build_user_prompt
from app.schemas.requirement_analysis import RequirementAnalysisResult
from pydantic import ValidationError


class AIAnalysisError(Exception):
    pass


def analyze_project_description(description: str, budget: str = None, platform: str = None) -> RequirementAnalysisResult:
    user_prompt = build_user_prompt(description, budget, platform)

    last_error = None
    for attempt in range(2):  # try once, retry once on failure
        try:
            raw_response = call_llm(REQUIREMENT_ANALYZER_SYSTEM_PROMPT, user_prompt)
            parsed = json.loads(raw_response)
            validated = RequirementAnalysisResult(**parsed)
            return validated
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            continue

    raise AIAnalysisError(f"LLM failed to return valid structured output after retries: {last_error}")
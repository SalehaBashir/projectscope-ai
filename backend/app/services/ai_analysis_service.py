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

import json
from app.ai.groq_client import call_llm
from app.ai.prompts import REQUIREMENT_ANALYZER_SYSTEM_PROMPT, build_user_prompt
from app.schemas.requirement_analysis import RequirementAnalysisResult
from app.repositories import requirement_repository, feature_repository
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uuid


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


def analyze_and_save(db: Session, project_id: uuid.UUID, description: str, budget: str = None, platform: str = None):
    result = analyze_project_description(description, budget, platform)

    saved_requirements = requirement_repository.create_requirements(
        db, project_id, [r.model_dump() for r in result.requirements]
    )
    saved_features = feature_repository.create_features(
        db, project_id, [f.model_dump() for f in result.features]
    )

    return {
        "project_type": result.project_type,
        "users": result.users,
        "requirements": saved_requirements,
        "features": saved_features,
    }
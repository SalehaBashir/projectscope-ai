import json
from app.ai.groq_client import call_llm
from app.ai.prompts import TECH_STACK_SYSTEM_PROMPT, build_tech_stack_prompt
from app.schemas.tech_stack import TechStackResult
from app.repositories import requirement_repository, feature_repository, tech_stack_repository
from pydantic import ValidationError
from sqlalchemy.orm import Session
import uuid


class TechStackError(Exception):
    pass


def recommend_stack(db: Session, project_id: uuid.UUID, project_description: str, preferred_language: str = None):
    requirements = requirement_repository.list_requirements(db, project_id)
    features = feature_repository.list_features(db, project_id)

    user_prompt = build_tech_stack_prompt(project_description, requirements, features, preferred_language)

    last_error = None
    for attempt in range(2):
        try:
            raw_response = call_llm(TECH_STACK_SYSTEM_PROMPT, user_prompt)
            parsed = json.loads(raw_response)
            validated = TechStackResult(**parsed)
            return tech_stack_repository.save_recommendation(
                db, project_id, [s.model_dump() for s in validated.stack], validated.summary
            )
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            continue

    raise TechStackError(f"LLM failed to return valid structured output after retries: {last_error}")
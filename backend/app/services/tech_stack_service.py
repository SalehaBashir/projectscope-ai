import json
from sqlalchemy.orm import Session
from app.ai.groq_client import call_llm
from app.ai.prompts import TECH_STACK_SYSTEM_PROMPT, build_tech_stack_prompt
from app.schemas.tech_stack import TechStackResult
from app.models.project import Project
from app.models.requirement import Requirement
from app.repositories import feature_repository
from pydantic import ValidationError
import uuid


class TechStackError(Exception):
    pass


def recommend_tech_stack(db: Session, project_id: uuid.UUID) -> TechStackResult:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise TechStackError("Project not found")

    features = feature_repository.list_features(db, project_id)
    feature_names = [f.canonical_name for f in features]

    scale_requirement = (
        db.query(Requirement)
        .filter(Requirement.project_id == project_id)
        .filter(Requirement.description.like("ANSWER[scale]%"))
        .first()
    )
    scale_text = scale_requirement.description if scale_requirement else ""

    # project_type isn't stored directly on the project, so infer a fallback from title/description
    project_type = project.description[:100]

    prompt = build_tech_stack_prompt(project_type, feature_names, scale_text)

    last_error = None
    for attempt in range(2):
        try:
            raw_response = call_llm(TECH_STACK_SYSTEM_PROMPT, prompt)
            parsed = json.loads(raw_response)
            validated = TechStackResult(**parsed)
            return validated
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            continue

    raise TechStackError(f"LLM failed to return valid tech stack recommendation: {last_error}")
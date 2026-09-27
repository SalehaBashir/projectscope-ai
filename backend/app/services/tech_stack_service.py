
import json
import uuid

from sqlalchemy.orm import Session
from pydantic import ValidationError

from app.ai.groq_client import GroqProvider
from app.ai.prompts import (
    TECH_STACK_SYSTEM_PROMPT,
    build_tech_stack_prompt,
)
from app.schemas.tech_stack import TechStackResult
from app.models.project import Project
from app.models.requirement import Requirement
from app.repositories import feature_repository


class TechStackError(Exception):
    pass


def _normalize_tech_stack_response(parsed: dict) -> dict:
    """
    Normalize the LLM response before Pydantic validation.

    The LLM may occasionally omit optional-looking sections such as
    folder_structure or guidelines. The frontend still expects the
    complete TechStackResult structure, so provide safe defaults.
    """

    if not isinstance(parsed, dict):
        raise ValueError(
            "LLM response must be a JSON object."
        )

    # ------------------------------------------------------------
    # Normalize tech_stack
    # ------------------------------------------------------------

    tech_stack = parsed.get("tech_stack")

    if not isinstance(tech_stack, dict):
        tech_stack = {}

    tech_stack.setdefault(
        "frontend",
        "Next.js",
    )

    tech_stack.setdefault(
        "backend",
        "FastAPI",
    )

    tech_stack.setdefault(
        "database",
        "PostgreSQL",
    )

    tech_stack.setdefault(
        "hosting",
        "Cloud hosting",
    )

    tech_stack.setdefault(
        "reasoning",
        "This stack provides a practical and scalable foundation "
        "for the project's requirements and features.",
    )

    # Replace null values as well.
    for key, default_value in {
        "frontend": "Next.js",
        "backend": "FastAPI",
        "database": "PostgreSQL",
        "hosting": "Cloud hosting",
        "reasoning": (
            "This stack provides a practical and scalable "
            "foundation for the project's requirements "
            "and features."
        ),
    }.items():
        if (
            tech_stack.get(key) is None
            or str(tech_stack.get(key)).strip() == ""
        ):
            tech_stack[key] = default_value

    parsed["tech_stack"] = tech_stack

    # ------------------------------------------------------------
    # Normalize folder structure
    # ------------------------------------------------------------

    folder_structure = parsed.get(
        "folder_structure"
    )

    if not isinstance(folder_structure, list):
        folder_structure = []

    folder_structure = [
        str(item).strip()
        for item in folder_structure
        if item is not None and str(item).strip()
    ]

    if not folder_structure:
        folder_structure = [
            "frontend/",
            "backend/",
            "backend/app/",
            "backend/app/api/",
            "backend/app/models/",
            "backend/app/schemas/",
            "backend/app/services/",
            "backend/app/repositories/",
            "backend/tests/",
        ]

    parsed["folder_structure"] = folder_structure

    # ------------------------------------------------------------
    # Normalize development guidelines
    # ------------------------------------------------------------

    guidelines = parsed.get("guidelines")

    if not isinstance(guidelines, list):
        guidelines = []

    guidelines = [
        str(item).strip()
        for item in guidelines
        if item is not None and str(item).strip()
    ]

    if not guidelines:
        guidelines = [
            "Keep frontend and backend responsibilities separated.",
            "Use API validation for user-provided data.",
            "Keep database access inside repositories or services.",
            "Use environment variables for secrets and configuration.",
            "Write tests for important API and business logic.",
            "Keep the project structure modular and maintainable.",
        ]

    parsed["guidelines"] = guidelines

    return parsed


def recommend_tech_stack(
    db: Session,
    project_id: uuid.UUID,
) -> TechStackResult:

    # ------------------------------------------------------------
    # Get project
    # ------------------------------------------------------------

    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise TechStackError(
            "Project not found"
        )

    # ------------------------------------------------------------
    # Get project features
    # ------------------------------------------------------------

    features = feature_repository.list_features(
        db,
        project_id,
    )

    feature_names = [
        f.canonical_name
        for f in features
        if getattr(f, "canonical_name", None)
    ]

    # ------------------------------------------------------------
    # Get scale requirement if available
    # ------------------------------------------------------------

    scale_requirement = (
        db.query(Requirement)
        .filter(
            Requirement.project_id == project_id
        )
        .filter(
            Requirement.description.like(
                "ANSWER[scale]%"
            )
        )
        .first()
    )

    scale_text = (
        scale_requirement.description
        if scale_requirement
        else ""
    )

    # ------------------------------------------------------------
    # Project type fallback
    # ------------------------------------------------------------

    project_description = (
        project.description or ""
    ).strip()

    project_type = project_description[:100]

    # ------------------------------------------------------------
    # Build AI prompt
    # ------------------------------------------------------------

    prompt = build_tech_stack_prompt(
        project_type,
        feature_names,
        scale_text,
    )

    ai_provider = GroqProvider()

    last_error = None

    # ------------------------------------------------------------
    # Try twice
    # ------------------------------------------------------------

    for attempt in range(2):

        try:
            raw_response = ai_provider.generate(
                TECH_STACK_SYSTEM_PROMPT,
                prompt,
            )

            if not raw_response:
                raise ValueError(
                    "LLM returned an empty response."
                )

            # ----------------------------------------------------
            # Parse JSON
            # ----------------------------------------------------

            parsed = json.loads(
                raw_response
            )

            # ----------------------------------------------------
            # Normalize response before validation
            # ----------------------------------------------------

            parsed = _normalize_tech_stack_response(
                parsed
            )

            # ----------------------------------------------------
            # Validate final structure
            # ----------------------------------------------------

            validated = TechStackResult(
                **parsed
            )

            return validated

        except (
            json.JSONDecodeError,
            ValidationError,
            ValueError,
            TypeError,
        ) as exc:

            last_error = exc

            # On the first failed attempt, explicitly tell the
            # model to return the missing required sections.
            if attempt == 0:
                prompt = f"""
{prompt}

IMPORTANT:
Return ONLY valid JSON.

The JSON MUST contain exactly these top-level sections:

{{
  "tech_stack": {{
    "frontend": "string",
    "backend": "string",
    "database": "string",
    "hosting": "string",
    "reasoning": "string"
  }},
  "folder_structure": [
    "string"
  ],
  "guidelines": [
    "string"
  ]
}}

Do NOT omit folder_structure.
Do NOT omit guidelines.
Do NOT wrap the JSON in markdown code fences.
"""

            continue

        except Exception as exc:
            last_error = exc
            continue

    raise TechStackError(
        "LLM failed to return valid tech stack recommendation: "
        f"{last_error}"
    )

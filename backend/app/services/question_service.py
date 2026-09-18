
from sqlalchemy.orm import Session

from app.repositories import feature_repository, requirement_repository
from app.ai.question_bank import QUESTION_BANK
from app.models.project import Project

import uuid


def get_relevant_questions(
    db: Session,
    project_id: uuid.UUID,
):
    """
    Return both:
    1. AI-generated questions from project.missing_information
    2. Relevant predefined questions from QUESTION_BANK

    Already answered questions are excluded.
    """

    # ---------------------------------------------------------
    # Get project
    # ---------------------------------------------------------
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    # ---------------------------------------------------------
    # Find questions that have already been answered
    # ---------------------------------------------------------
    existing_requirements = (
        requirement_repository.list_requirements(
            db,
            project_id,
        )
    )

    already_answered_ids = set()

    for req in existing_requirements:
        if (
            req.category == "constraint"
            and req.description
            and req.description.startswith("ANSWER[")
        ):
            try:
                question_id = (
                    req.description
                    .split("ANSWER[", 1)[1]
                    .split("]", 1)[0]
                )

                already_answered_ids.add(question_id)

            except (IndexError, AttributeError):
                continue

    relevant = []

    # ---------------------------------------------------------
    # AI-generated questions
    # ---------------------------------------------------------
    if project and project.missing_information:
        for index, item in enumerate(
            project.missing_information
        ):
            if not item:
                continue

            text = str(item).strip()

            if not text:
                continue

            question_id = f"ai_missing_{index}"

            if question_id in already_answered_ids:
                continue

            relevant.append(
                {
                    "id": question_id,
                    "text": text,
                    "category": "ai_generated",
                }
            )

    # ---------------------------------------------------------
    # Existing QUESTION_BANK questions
    # ---------------------------------------------------------
    features = feature_repository.list_features(
        db,
        project_id,
    )

    feature_names = {
        (f.canonical_name or "").upper()
        for f in features
    }

    for question in QUESTION_BANK:
        question_id = question["id"]

        if question_id in already_answered_ids:
            continue

        trigger_keywords = [
            str(keyword).upper()
            for keyword in question.get(
                "trigger_keywords",
                [],
            )
        ]

        keyword_match = any(
            keyword in feature_name
            for feature_name in feature_names
            for keyword in trigger_keywords
        )

        if question.get("always_ask") or keyword_match:
            relevant.append(
                {
                    "id": question_id,
                    "text": question["text"],
                    "category": "follow_up",
                }
            )

    return relevant


def save_answer(
    db: Session,
    project_id: uuid.UUID,
    organization_id: uuid.UUID,
    question_id: str,
    answer_text: str,
):
    """
    Save an answer as a project constraint.

    Supports:
    - predefined QUESTION_BANK questions
    - AI-generated missing-information questions
    """

    answer_text = answer_text.strip()

    if not answer_text:
        raise ValueError(
            "Answer cannot be empty."
        )

    # ---------------------------------------------------------
    # Check predefined QUESTION_BANK
    # ---------------------------------------------------------
    question = next(
        (
            q
            for q in QUESTION_BANK
            if q["id"] == question_id
        ),
        None,
    )

    # ---------------------------------------------------------
    # Check AI-generated question
    # ---------------------------------------------------------
    is_ai_question = question_id.startswith(
        "ai_missing_"
    )

    if not question and not is_ai_question:
        raise ValueError(
            f"Unknown question id: {question_id}"
        )

    # ---------------------------------------------------------
    # Store answer as a project constraint
    # ---------------------------------------------------------
    marker_text = (
        f"ANSWER[{question_id}]: {answer_text}"
    )

    saved = requirement_repository.create_requirements(
        db,
        project_id,
        organization_id,
        [
            {
                "category": "constraint",
                "text": marker_text,
            }
        ],
    )

    return saved[0]

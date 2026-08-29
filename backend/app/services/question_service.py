from sqlalchemy.orm import Session
from app.repositories import feature_repository, requirement_repository
from app.ai.question_bank import QUESTION_BANK
import uuid


def get_relevant_questions(db: Session, project_id: uuid.UUID):
    features = feature_repository.list_features(db, project_id)
    feature_names = {f.canonical_name for f in features}

    existing_requirements = requirement_repository.list_requirements(db, project_id)
    already_answered_ids = set()
    for req in existing_requirements:
        if req.category == "constraint" and req.description.startswith("ANSWER["):
            question_id = req.description.split("ANSWER[")[1].split("]")[0]
            already_answered_ids.add(question_id)
    relevant = []
    for question in QUESTION_BANK:
        if question["id"] in already_answered_ids:
            continue
        keyword_match = any(
            keyword in name
            for name in feature_names
            for keyword in question["trigger_keywords"]
        )
        if question["always_ask"] or keyword_match:
            relevant.append({"id": question["id"], "text": question["text"]})

    return relevant


def save_answer(db: Session, project_id: uuid.UUID, question_id: str, answer_text: str):
    question = next((q for q in QUESTION_BANK if q["id"] == question_id), None)
    if not question:
        raise ValueError(f"Unknown question id: {question_id}")

    marker_text = f"ANSWER[{question_id}]: {answer_text}"

    saved = requirement_repository.create_requirements(
        db,
        project_id,
        [{"category": "constraint", "text": marker_text}],
    )
    return saved[0]
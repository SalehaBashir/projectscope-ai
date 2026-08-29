import json
from sqlalchemy.orm import Session
from app.ai.groq_client import call_llm
from app.ai.prompts import TASK_GENERATION_SYSTEM_PROMPT, build_task_generation_prompt
from app.ai.task_library import get_baseline_tasks
from app.repositories import feature_repository, role_repository
from app.models.task import Task
import uuid


def generate_tasks_for_project(db: Session, project_id: uuid.UUID):
    role_repository.seed_roles(db)
    roles = {r.name: r for r in role_repository.list_roles(db)}

    features = feature_repository.list_features(db, project_id)
    all_created_tasks = []

    for feature in features:
        baseline_tasks = get_baseline_tasks(feature.canonical_name)

        additional_tasks = []
        try:
            prompt = build_task_generation_prompt(
                feature.canonical_name, feature.description, baseline_tasks
            )
            raw_response = call_llm(TASK_GENERATION_SYSTEM_PROMPT, prompt)
            parsed = json.loads(raw_response)
            additional_tasks = parsed.get("additional_tasks", [])
        except Exception:
            additional_tasks = []  # if LLM fails, baseline tasks are still enough

        combined = baseline_tasks + additional_tasks

        for task_data in combined:
            role = roles.get(task_data["role"])
            new_task = Task(
                feature_id=feature.id,
                role_id=role.id if role else None,
                title=task_data["title"],
                base_hours=task_data["base_hours"],
            )
            db.add(new_task)
            all_created_tasks.append(new_task)

    db.commit()
    for t in all_created_tasks:
        db.refresh(t)
    return all_created_tasks
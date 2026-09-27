import json
import uuid

from sqlalchemy.orm import Session

from app.ai.groq_client import GroqProvider
from app.ai.prompts import (
    TASK_GENERATION_SYSTEM_PROMPT,
    build_task_generation_prompt,
)
from app.ai.task_library import get_baseline_tasks
from app.repositories import feature_repository, role_repository
from app.models.project import Project
from app.models.task import Task


def _format_feature_name(canonical_name: str) -> str:
    """
    Convert canonical feature names into readable names.

    Example:
    AUTHENTICATION -> Authentication
    PRODUCT_CATALOG -> Product Catalog
    PAYMENT_PROCESSING -> Payment Processing
    """

    name = str(canonical_name or "").strip()

    if not name:
        return "Feature"

    return " ".join(
        word.capitalize()
        for word in name.replace("_", " ").split()
    )


def _build_task_title(
    task_title: str,
    feature_name: str,
) -> str:
    """
    Make every task clearly identify the feature it belongs to.

    Generic examples:
        Design UI for this feature
            -> Design UI for Authentication

        Implement backend logic
            -> Implement backend logic — Authentication

        Implement frontend UI
            -> Implement frontend UI — Authentication

        Test this feature
            -> Test Authentication

    Specific AI-generated task titles are preserved, but the
    feature name is appended when it is missing.
    """

    title = str(task_title or "").strip()

    if not title:
        return f"Implement {feature_name}"

    normalized = title.casefold().strip()
    normalized_feature = feature_name.casefold()

    # ---------------------------------------------------------
    # Exact generic task titles
    # ---------------------------------------------------------

    if normalized in {
        "design ui for this feature",
        "design ui",
    }:
        return f"Design UI for {feature_name}"

    if normalized in {
        "implement backend logic",
        "implement backend logic for this feature",
    }:
        return f"Implement backend logic — {feature_name}"

    if normalized in {
        "implement frontend ui",
        "implement frontend ui for this feature",
        "build frontend ui",
    }:
        return f"Implement frontend UI — {feature_name}"

    if normalized in {
        "implement this feature",
        "implement feature",
    }:
        return f"Implement {feature_name}"

    if normalized in {
        "develop this feature",
        "develop feature",
    }:
        return f"Develop {feature_name}"

    if normalized in {
        "build this feature",
        "build feature",
    }:
        return f"Build {feature_name}"

    if normalized in {
        "test this feature",
        "test feature",
    }:
        return f"Test {feature_name}"

    if normalized in {
        "document this feature",
        "document feature",
    }:
        return f"Document {feature_name}"

    if normalized in {
        "configure this feature",
        "configure feature",
    }:
        return f"Configure {feature_name}"

    # ---------------------------------------------------------
    # If feature name is already present, keep original title.
    # ---------------------------------------------------------

    if normalized_feature in normalized:
        return title

    # ---------------------------------------------------------
    # Any remaining task gets associated with its feature.
    #
    # Example:
    # Test authentication flows
    # ->
    # Test authentication flows — Authentication
    # ---------------------------------------------------------

    return f"{title.rstrip('.')} — {feature_name}"


def generate_tasks_for_project(
    db: Session,
    project_id: uuid.UUID,
):
    project = db.get(Project, project_id)

    if not project:
        raise ValueError("Project not found")

    organization_id = project.organization_id

    # ---------------------------------------------------------
    # Seed roles
    # ---------------------------------------------------------

    role_repository.seed_roles(db)

    roles = {
        r.name: r
        for r in role_repository.list_roles(db)
    }

    # ---------------------------------------------------------
    # Get all project features
    # ---------------------------------------------------------

    raw_features = feature_repository.list_features(
        db,
        project_id,
    )

    if not raw_features:
        return []

    # ---------------------------------------------------------
    # Remove duplicate features
    # ---------------------------------------------------------

    unique_features = {}

    for feature in raw_features:
        canonical_name = str(
            getattr(feature, "canonical_name", "") or ""
        ).strip()

        if not canonical_name:
            continue

        key = " ".join(
            canonical_name.casefold().split()
        )

        if key not in unique_features:
            unique_features[key] = feature

    features = list(unique_features.values())

    if not features:
        return []

    # ---------------------------------------------------------
    # IMPORTANT:
    # Remove existing generated tasks before regenerating.
    #
    # This prevents old generic tasks from remaining in the DB
    # when the user clicks "Regenerate tasks".
    # ---------------------------------------------------------

    all_feature_ids = [
        feature.id
        for feature in raw_features
        if getattr(feature, "id", None) is not None
    ]

    if all_feature_ids:
        (
            db.query(Task)
            .filter(Task.feature_id.in_(all_feature_ids))
            .delete(synchronize_session=False)
        )

        db.flush()

    # ---------------------------------------------------------
    # Generate new tasks
    # ---------------------------------------------------------

    all_created_tasks = []

    ai_provider = GroqProvider()

    for feature in features:

        feature_name = _format_feature_name(
            feature.canonical_name
        )

        # -----------------------------------------------------
        # Baseline tasks
        # -----------------------------------------------------

        baseline_tasks = get_baseline_tasks(
            feature.canonical_name
        )

        if not isinstance(baseline_tasks, list):
            baseline_tasks = []

        # -----------------------------------------------------
        # AI-generated additional tasks
        # -----------------------------------------------------

        additional_tasks = []

        try:
            prompt = build_task_generation_prompt(
                feature.canonical_name,
                feature.description,
                baseline_tasks,
            )

            raw_response = ai_provider.generate(
                TASK_GENERATION_SYSTEM_PROMPT,
                prompt,
            )

            parsed = json.loads(raw_response)

            additional_tasks = parsed.get(
                "additional_tasks",
                [],
            )

            if not isinstance(additional_tasks, list):
                additional_tasks = []

        except Exception:
            additional_tasks = []

        # -----------------------------------------------------
        # Combine baseline + AI tasks
        # -----------------------------------------------------

        combined = (
            baseline_tasks +
            additional_tasks
        )

        # -----------------------------------------------------
        # Remove duplicate task titles for this feature
        # -----------------------------------------------------

        seen_task_titles = set()

        for task_data in combined:

            if not isinstance(task_data, dict):
                continue

            raw_title = task_data.get(
                "title",
                "",
            )

            title = _build_task_title(
                raw_title,
                feature_name,
            )

            title_key = " ".join(
                title.casefold().split()
            )

            if title_key in seen_task_titles:
                continue

            seen_task_titles.add(title_key)

            # -------------------------------------------------
            # Resolve role
            # -------------------------------------------------

            role_name = task_data.get("role")

            role = roles.get(role_name)

            # -------------------------------------------------
            # Safely parse hours
            # -------------------------------------------------

            try:
                base_hours = float(
                    task_data.get(
                        "base_hours",
                        0,
                    )
                )
            except (
                TypeError,
                ValueError,
            ):
                base_hours = 0

            # -------------------------------------------------
            # Create task
            # -------------------------------------------------

            new_task = Task(
                feature_id=feature.id,
                organization_id=organization_id,
                role_id=role.id if role else None,
                title=title,
                base_hours=base_hours,
            )

            db.add(new_task)

            all_created_tasks.append(
                new_task
            )

    # ---------------------------------------------------------
    # Save everything
    # ---------------------------------------------------------

    db.commit()

    for task in all_created_tasks:
        db.refresh(task)

    return all_created_tasks
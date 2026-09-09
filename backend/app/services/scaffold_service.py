import os
import tempfile
import uuid
import zipfile

from sqlalchemy.orm import Session

from app.ai import scaffold_templates as t
from app.models.project import Project
from app.services.tech_stack_service import recommend_tech_stack
from app.services.theme_service import (
    get_selected_theme,
    suggest_theme_for_project,
)
from app.repositories import feature_repository


def build_scaffold_zip(db: Session, project_id: uuid.UUID) -> str:
    # ---------------------------------------------------------
    # Get project
    # ---------------------------------------------------------
    project = (
        db.query(Project)
        .filter(Project.id == project_id)
        .first()
    )

    if not project:
        raise ValueError("Project not found")

    # ---------------------------------------------------------
    # Get recommended tech stack
    # ---------------------------------------------------------
    tech_result = recommend_tech_stack(db, project_id)
    tech_stack = tech_result.tech_stack.model_dump()

    # ---------------------------------------------------------
    # Get selected theme
    # ---------------------------------------------------------
    theme = get_selected_theme(db, project_id)

    # If user has not selected a theme,
    # use AI suggested theme.
    if not theme:
        theme = suggest_theme_for_project(db, project_id)

    # Final fallback
    if not theme:
        theme = {
            "id": "modern_minimal",
            "name": "Modern Minimal",
            "primary_color": "#2E7D32",
            "secondary_color": "#F5F5F5",
            "font": "Inter",
        }

    # ---------------------------------------------------------
    # Get project features
    # ---------------------------------------------------------
    features = feature_repository.list_features(
        db,
        project_id,
    )

    feature_names = [
        feature.canonical_name
        for feature in features
    ]

    # ---------------------------------------------------------
    # Project name
    # ---------------------------------------------------------
    project_name = project.title or "MyProject"

    safe_project_name = (
        project_name
        .replace(" ", "_")
        .replace("/", "_")
        .replace("\\", "_")
    )

    # ---------------------------------------------------------
    # Temporary ZIP location
    # ---------------------------------------------------------
    tmp_dir = tempfile.mkdtemp()

    zip_path = os.path.join(
        tmp_dir,
        f"{safe_project_name}_starter.zip",
    )

    # =========================================================
    # CREATE ZIP
    # =========================================================

    with zipfile.ZipFile(
        zip_path,
        "w",
        zipfile.ZIP_DEFLATED,
    ) as zf:

        # =====================================================
        # ROOT README
        # =====================================================

        zf.writestr(
            "README.md",
            t.get_readme_template(
                project_name,
                tech_stack,
                theme,
                feature_names,
            ),
        )

        # =====================================================
        # DEVELOPMENT GUIDELINES
        # =====================================================

        guidelines = getattr(
            tech_result,
            "guidelines",
            [],
        )

        guidelines_text = (
            "# Development Guidelines\n\n"
            + "\n".join(
                f"- {guideline}"
                for guideline in guidelines
            )
        )

        zf.writestr(
            "DEVELOPMENT_GUIDELINES.md",
            guidelines_text,
        )

        # =====================================================
        # PROJECT STRUCTURE
        # =====================================================

        structure = """backend/
├── app/
│   ├── api/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
frontend/
├── app/
├── components/
├── hooks/
├── lib/
└── types/
│
mobile/
├── app/
└── src/
    ├── components/
    ├── navigation/
    └── screens/
│
shared/
└── types/
"""

        zf.writestr(
            "PROJECT_STRUCTURE.txt",
            structure,
        )

        # =====================================================
        # BACKEND
        # =====================================================

        zf.writestr(
            "backend/app/main.py",
            t.get_fastapi_main_template(
                project_name
            ),
        )

        zf.writestr(
            "backend/app/api/__init__.py",
            "",
        )

        zf.writestr(
            "backend/app/database/__init__.py",
            "",
        )

        zf.writestr(
            "backend/app/models/__init__.py",
            "",
        )

        zf.writestr(
            "backend/app/schemas/__init__.py",
            "",
        )

        zf.writestr(
            "backend/app/services/__init__.py",
            "",
        )

        zf.writestr(
            "backend/requirements.txt",
            t.get_fastapi_requirements(),
        )

        zf.writestr(
            "backend/README.md",
            t.get_fastapi_readme(),
        )

        zf.writestr(
            "backend/.env.example",
            """DATABASE_URL=
APP_ENV=development
SECRET_KEY=
GROQ_API_KEY=
""",
        )

        # =====================================================
        # FRONTEND
        # =====================================================

        zf.writestr(
            "frontend/package.json",
            t.get_package_json_template(
                project_name
            ),
        )

        zf.writestr(
            "frontend/app/page.tsx",
            t.get_nextjs_page_template(
                project_name,
                theme,
                feature_names,
            ),
        )

        zf.writestr(
            "frontend/app/layout.tsx",
            t.get_nextjs_layout_template(
                project_name,
                theme,
            ),
        )

        zf.writestr(
            "frontend/components/.gitkeep",
            "",
        )

        zf.writestr(
            "frontend/hooks/.gitkeep",
            "",
        )

        zf.writestr(
            "frontend/lib/.gitkeep",
            "",
        )

        zf.writestr(
            "frontend/types/.gitkeep",
            "",
        )

        zf.writestr(
            "frontend/README.md",
            t.get_frontend_readme(),
        )

        # =====================================================
        # MOBILE
        # =====================================================

        zf.writestr(
            "mobile/README.md",
            t.get_mobile_readme(
                project_name
            ),
        )

        zf.writestr(
            "mobile/package.json",
            t.get_mobile_package_json(
                project_name
            ),
        )

        zf.writestr(
            "mobile/app/index.tsx",
            t.get_mobile_app_template(
                project_name,
                theme,
                feature_names,
            ),
        )

        zf.writestr(
            "mobile/src/screens/.gitkeep",
            "",
        )

        zf.writestr(
            "mobile/src/components/.gitkeep",
            "",
        )

        zf.writestr(
            "mobile/src/navigation/.gitkeep",
            "",
        )

        # =====================================================
        # SHARED TYPES
        # =====================================================

        zf.writestr(
            "shared/types/api.d.ts",
            t.get_shared_types_template(),
        )

    # ---------------------------------------------------------
    # Return ZIP path
    # ---------------------------------------------------------

    return zip_path
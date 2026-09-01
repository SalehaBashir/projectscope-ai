import os
import zipfile
import tempfile
from sqlalchemy.orm import Session
from app.services.tech_stack_service import recommend_tech_stack
from app.services.theme_service import suggest_theme_for_project
from app.models.project import Project
from app.ai import scaffold_templates as t
import uuid


def build_scaffold_zip(db: Session, project_id: uuid.UUID) -> str:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    tech_result = recommend_tech_stack(db, project_id)
    tech_stack = tech_result.tech_stack.model_dump()
    theme = suggest_theme_for_project(db, project_id)

    project_name = project.title or "MyProject"

    backend_choice = tech_stack.get("backend", "").lower()
    frontend_choice = tech_stack.get("frontend", "").lower()

    tmp_dir = tempfile.mkdtemp()
    zip_path = os.path.join(tmp_dir, f"{project_name.replace(' ', '_')}_starter.zip")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # Root README
        zf.writestr("README.md", t.get_readme_template(project_name, tech_stack, theme))

        # Backend: default to FastAPI template unless something very different is specified
        zf.writestr("backend/app/main.py", t.get_fastapi_main_template(project_name))
        zf.writestr("backend/requirements.txt", t.get_fastapi_requirements())
        zf.writestr("backend/README.md", t.get_fastapi_readme())
        zf.writestr("backend/.env.example", "DATABASE_URL=\nAPP_ENV=development\n")

        # Frontend: default to Next.js-style template
        zf.writestr("frontend/package.json", t.get_package_json_template(project_name))
        zf.writestr("frontend/app/page.tsx", t.get_nextjs_page_template(project_name, theme))
        zf.writestr("frontend/README.md", t.get_frontend_readme())

        # Folder structure reference file (from Day 10 recommendation)
        structure_text = "\n".join(tech_result.folder_structure)
        zf.writestr("PROJECT_STRUCTURE.txt", structure_text)

        # Development guidelines
        guidelines_text = "\n".join(f"- {g}" for g in tech_result.guidelines)
        zf.writestr("DEVELOPMENT_GUIDELINES.md", "# Development Guidelines\n\n" + guidelines_text)

    return zip_path
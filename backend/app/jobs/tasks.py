from app.database.connection import SessionLocal
from app.services.ai_analysis_service import analyze_and_save


def run_analysis_job(project_id, organization_id, description, budget, platform):
    db = SessionLocal()
    try:
        result = analyze_and_save(
            db, project_id=project_id, organization_id=organization_id,
            description=description, budget=budget, platform=platform,
        )
        return {"status": "completed", "project_id": str(project_id)}
    finally:
        db.close()
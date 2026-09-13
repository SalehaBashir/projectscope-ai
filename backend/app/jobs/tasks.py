from app.database.connection import SessionLocal
from app.services.ai_analysis_service import analyze_and_save


def run_analysis_job(project_id, organization_id, description, budget, platform):
    db = SessionLocal()
    try:
        result = analyze_and_save(
            db, project_id=project_id, organization_id=organization_id,
            description=description, budget=budget, platform=platform,
        )

        # Convert ORM objects to plain dicts before returning — the RQ
        # result is later serialized to JSON by the job-status API
        # endpoint, and the DB session is closed by the time it's read,
        # so returning live ORM instances would fail either way.
        return {
            "project_type": result["project_type"],
            "users": result["users"],
            "assumptions": result["assumptions"],
            "missing_information": result["missing_information"],
            "requirements": [
                {
                    "id": str(r.id),
                    "category": r.category,
                    "description": r.description,
                }
                for r in result["requirements"]
            ],
            "features": [
                {
                    "id": str(f.id),
                    "canonical_name": f.canonical_name,
                    "description": f.description,
                    "priority": f.priority,
                    "complexity": f.complexity,
                    "confidence": f.confidence,
                }
                for f in result["features"]
            ],
        }
    finally:
        db.close()
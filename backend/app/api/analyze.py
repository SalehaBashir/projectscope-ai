from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.requirement_analysis import AnalyzeRequest
from app.services.ai_analysis_service import analyze_and_save, AIAnalysisError
import uuid

router = APIRouter(prefix="/projects", tags=["AI Analysis"])


@router.post("/{project_id}/analyze")
def analyze_project(project_id: uuid.UUID, request: AnalyzeRequest, db: Session = Depends(get_db)):
    try:
        result = analyze_and_save(
            db,
            project_id=project_id,
            description=request.description,
            budget=request.budget,
            platform=request.platform,
        )
        return {
            "project_type": result["project_type"],
            "users": result["users"],
            "requirements": [
                {"id": r.id, "category": r.category, "description": r.description}
                for r in result["requirements"]
            ],
            "features": [
                {
                    "id": f.id,
                    "canonical_name": f.canonical_name,
                    "description": f.description,
                    "priority": f.priority,
                    "complexity": f.complexity,
                    "confidence": f.confidence,
                }
                for f in result["features"]
            ],
        }
    except AIAnalysisError as e:
        raise HTTPException(status_code=502, detail=str(e))
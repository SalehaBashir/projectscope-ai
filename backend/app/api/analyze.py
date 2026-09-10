from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.requirement_analysis import AnalyzeRequest
from app.services.ai_analysis_service import analyze_and_save, AIAnalysisError
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["AI Analysis"])


@router.post("/{project_id}/analyze")
def analyze_project(
    request: Request,
    project_id: uuid.UUID,
    body: AnalyzeRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)

    try:
        result = analyze_and_save(
            db,
            project_id=project_id,
            organization_id=current_user.organization_id,
            description=body.description,
            budget=body.budget,
            platform=body.platform,       
        )
        llm_metadata = result.get("llm_metadata", {})

        request.state.organization_id = current_user.organization_id
        request.state.project_id = project_id
        request.state.model_version = llm_metadata.get("model")
        request.state.prompt_tokens = llm_metadata.get("prompt_tokens")
        request.state.completion_tokens = llm_metadata.get("completion_tokens")
        request.state.estimated_ai_cost = llm_metadata.get("estimated_ai_cost")  

        return {
            "project_type": result["project_type"],
            "users": result["users"],
            "assumptions": result["assumptions"],
            "missing_information": result["missing_information"],
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

from fastapi import APIRouter, HTTPException
from app.schemas.requirement_analysis import AnalyzeRequest, RequirementAnalysisResult
from app.services.ai_analysis_service import analyze_project_description, AIAnalysisError

router = APIRouter(prefix="/analyze", tags=["AI Analysis"])


@router.post("/", response_model=RequirementAnalysisResult)
def analyze_project(request: AnalyzeRequest):
    try:
        result = analyze_project_description(
            description=request.description,
            budget=request.budget,
            platform=request.platform,
        )
        return result
    except AIAnalysisError as e:
        raise HTTPException(status_code=502, detail=str(e))
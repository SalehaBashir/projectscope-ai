from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import question_service
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/projects", tags=["Follow-Up Questions"])


class AnswerRequest(BaseModel):
    question_id: str
    answer: str


@router.get("/{project_id}/questions")
def get_questions(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    return question_service.get_relevant_questions(db, project_id)


@router.post("/{project_id}/questions/answer")
def answer_question(
    project_id: uuid.UUID,
    request: AnswerRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        saved = question_service.save_answer(
            db, project_id, request.question_id, request.answer
        )
        return {
            "id": saved.id,
            "category": saved.category,
            "description": saved.description,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

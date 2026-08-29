from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.services import question_service
from pydantic import BaseModel
import uuid

router = APIRouter(prefix="/projects", tags=["Follow-Up Questions"])


class AnswerRequest(BaseModel):
    question_id: str
    answer: str


@router.get("/{project_id}/questions")
def get_questions(project_id: uuid.UUID, db: Session = Depends(get_db)):
    return question_service.get_relevant_questions(db, project_id)


@router.post("/{project_id}/questions/answer")
def answer_question(project_id: uuid.UUID, request: AnswerRequest, db: Session = Depends(get_db)):
    try:
        saved = question_service.save_answer(db, project_id, request.question_id, request.answer)
        return {"id": saved.id, "category": saved.category, "description": saved.description}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
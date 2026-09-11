from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.schemas.feedback import FeedbackCreate, FeedbackResponse, FeedbackSummary
from app.services.feedback_service import (
    submit_feedback,
    get_project_feedback,
    get_task_feedback,
    get_feedback_detail,
    get_project_feedback_summary,
    delete_feedback_item,
    FeedbackError,
)
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
from app.models.task import Task
from app.models.feature import Feature
from app.models.project import Project
import uuid

router = APIRouter(prefix="/projects", tags=["Feedback"])


def _require_task_access(db, current_user: User, task_id: uuid.UUID):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    feature = db.query(Feature).filter(Feature.id == task.feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail="Task feature not found")
    project = db.query(Project).filter(Project.id == feature.project_id).first()
    if not project or project.organization_id != current_user.organization_id:
        raise HTTPException(
            status_code=403, detail="You do not have access to this task"
        )
    return task


@router.post("/{project_id}/feedback", response_model=FeedbackResponse)
def create_feedback(
    project_id: uuid.UUID,
    request: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        feedback = submit_feedback(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
            organization_id=current_user.organization_id,
            actual_hours=request.actual_hours,
            task_id=request.task_id,
            estimated_hours=request.estimated_hours,
            notes=request.notes,
        )
        return feedback
    except FeedbackError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{project_id}/feedback", response_model=list[FeedbackResponse])
def list_project_feedback(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        return get_project_feedback(db, project_id)
    except FeedbackError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/feedback/summary", response_model=FeedbackSummary)
def get_feedback_summary(
    project_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        return get_project_feedback_summary(db, project_id)
    except FeedbackError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{project_id}/feedback/{feedback_id}", response_model=FeedbackResponse)
def get_single_feedback(
    project_id: uuid.UUID,
    feedback_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        feedback = get_feedback_detail(db, feedback_id)
        if feedback.project_id != project_id:
            raise HTTPException(
                status_code=404,
                detail="Feedback not found for this project",
            )
        return feedback
    except FeedbackError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/tasks/{task_id}/feedback", response_model=list[FeedbackResponse])
def list_task_feedback(
    task_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    _require_task_access(db, current_user, task_id)
    try:
        return get_task_feedback(db, task_id)
    except FeedbackError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/{project_id}/feedback/{feedback_id}")
def remove_feedback(
    project_id: uuid.UUID,
    feedback_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    require_project_access(project_id, db, current_user)
    try:
        feedback = get_feedback_detail(db, feedback_id)
        if feedback.project_id != project_id:
            raise HTTPException(
                status_code=404,
                detail="Feedback not found for this project",
            )
        delete_feedback_item(db, feedback_id)
        return {"detail": "Feedback deleted successfully"}
    except FeedbackError as e:
        raise HTTPException(status_code=404, detail=str(e))

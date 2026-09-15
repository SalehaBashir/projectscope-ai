import os

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from rq.job import Job
import uuid

from app.database.connection import get_db
from app.schemas.requirement_analysis import AnalyzeRequest
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
from app.jobs.queue import task_queue
from app.jobs.tasks import run_analysis_job


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

    # During tests, execute the job immediately so mocked AI calls
    # can be inspected by security tests.
    #
    # The E2E test explicitly uses an RQ queue with is_async=False,
    # so that test continues through the normal queue path.
    if (
        os.getenv("APP_ENV") == "test"
        and getattr(task_queue, "is_async", True)
    ):
        result = run_analysis_job(
            project_id,
            current_user.organization_id,
            body.description,
            body.budget,
            body.platform,
        )

        return {
            "status": "completed",
            "result": result,
        }

    job = task_queue.enqueue(
        run_analysis_job,
        project_id,
        current_user.organization_id,
        body.description,
        body.budget,
        body.platform,
    )

    return {
        "status": "queued",
        "job_id": job.id,
    }


@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    job = Job.fetch(
        job_id,
        connection=task_queue.connection,
    )

    if job.is_failed:
        return {
            "status": "failed",
            "error": str(job.exc_info),
        }

    return {
        "status": job.get_status(),
        "result": job.result,
    }
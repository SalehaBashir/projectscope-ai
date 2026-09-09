from enum import Enum

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.services.report_service import (
    gather_report_data,
    generate_pdf,
    generate_docx,
    ReportGenerationError,
)
from app.security.security import get_current_user
from app.security.ownership import require_project_access
from app.models.user import User
import uuid

router = APIRouter(prefix="/projects", tags=["Reports"])


class ReportFormat(str, Enum):
    pdf = "pdf"
    docx = "docx"


MEDIA_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.get("/{project_id}/report")
def generate_project_report(
    project_id: uuid.UUID,
    format: ReportFormat = ReportFormat.pdf,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    project = require_project_access(project_id, db, current_user)

    try:
        data = gather_report_data(db, project_id)
    except ReportGenerationError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        if format == ReportFormat.docx:
            content = generate_docx(data)
        else:
            content = generate_pdf(data)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Report could not be generated: {e}",
        )

    filename = f"projectscope-{project.title}".replace(" ", "-").lower()
    return Response(
        content=content,
        media_type=MEDIA_TYPES[format.value],
        headers={
            "Content-Disposition": f'attachment; filename="{filename}.{format.value}"'
        },
    )

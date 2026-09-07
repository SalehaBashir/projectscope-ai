import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.llm_request import LLMRequest


def create_llm_request(
    db: Session,
    project_id: Optional[uuid.UUID],
    provider: str,
    model: str,
    prompt_tokens: Optional[float] = None,
    completion_tokens: Optional[float] = None,
    latency_ms: Optional[float] = None,
    status: str = "success",
    error_message: Optional[str] = None,
    metadata_json: Optional[dict] = None,
):
    request = LLMRequest(
        project_id=project_id,
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        latency_ms=latency_ms,
        status=status,
        error_message=error_message,
        metadata_json=metadata_json,
    )

    db.add(request)
    db.commit()
    db.refresh(request)

    return request
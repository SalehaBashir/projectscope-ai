from pydantic import BaseModel
from typing import List, Optional


class StackChoice(BaseModel):
    category: str          # e.g. "frontend", "backend", "database", "hosting", "auth"
    recommendation: str    # e.g. "Next.js", "FastAPI", "PostgreSQL"
    reason: str            # short justification tied to the project's requirements/features


class TechStackResult(BaseModel):
    stack: List[StackChoice]
    summary: str            # 1-2 line overall rationale


class TechStackRequest(BaseModel):
    preferred_language: Optional[str] = None   # optional user hint, e.g. "prefer Python backend"
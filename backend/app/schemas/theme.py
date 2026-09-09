from pydantic import BaseModel
from typing import Optional


class ThemeSelectRequest(BaseModel):
    theme_id: Optional[str] = None  # omit to accept the AI-suggested theme
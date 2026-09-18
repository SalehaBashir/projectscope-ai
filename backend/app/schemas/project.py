from pydantic import BaseModel, field_validator
from typing import Optional
from datetime import datetime
from uuid import UUID


MINIMUM_BUDGET = 10000


class ProjectCreate(BaseModel):
    title: str
    description: str
    budget: Optional[str] = None
    platform: Optional[str] = None

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, value):
        if value is None or value.strip() == "":
            return value

        try:
            amount = float(value)
        except ValueError:
            raise ValueError("Budget must be a valid number.")

        if amount < MINIMUM_BUDGET:
            raise ValueError(
                f"Minimum project budget must be {MINIMUM_BUDGET}."
            )

        return value


class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[str] = None
    platform: Optional[str] = None

    @field_validator("budget")
    @classmethod
    def validate_budget(cls, value):
        if value is None or value.strip() == "":
            return value

        try:
            amount = float(value)
        except ValueError:
            raise ValueError("Budget must be a valid number.")

        if amount < MINIMUM_BUDGET:
            raise ValueError(
                f"Minimum project budget must be {MINIMUM_BUDGET}."
            )

        return value


class ProjectResponse(BaseModel):
    id: UUID
    title: str
    description: str
    budget: Optional[str] = None
    platform: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
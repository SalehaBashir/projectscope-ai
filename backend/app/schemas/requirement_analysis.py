
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, field_validator


class RequirementCategory(str, Enum):
    functional = "functional"
    non_functional = "non_functional"
    integration = "integration"
    constraint = "constraint"


class PriorityLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"


class ExtractedRequirement(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    category: RequirementCategory
    text: str = Field(min_length=1, max_length=2000)
    confidence: float = Field(ge=0.0, le=1.0)


class ExtractedFeature(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    canonical_name: str = Field(min_length=1, max_length=200)
    description: str = Field(min_length=1, max_length=2000)
    priority: PriorityLevel
    complexity: PriorityLevel
    confidence: float = Field(ge=0.0, le=1.0)


class RequirementAnalysisResult(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    _llm_metadata: dict = PrivateAttr(default_factory=dict)
    project_type: str = Field(min_length=1, max_length=200)
    users: List[str] = Field(max_length=100)
    requirements: List[ExtractedRequirement] = Field(max_length=200)
    features: List[ExtractedFeature] = Field(max_length=200)
    assumptions: List[str] = Field(default_factory=list, max_length=100)
    missing_information: List[str] = Field(default_factory=list, max_length=100)

    @field_validator("project_type")
    @classmethod
    def validate_project_type(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Project type cannot be blank")
        return value

    @field_validator("users")
    @classmethod
    def validate_users(cls, values: List[str]) -> List[str]:
        cleaned = []

        for value in values:
            value = value.strip()

            if not value:
                raise ValueError("User entries cannot be blank")

            if len(value) > 200:
                raise ValueError("User entry is too long")

            cleaned.append(value)

        return cleaned


class AnalyzeRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    description: str = Field(
        min_length=10,
        max_length=10000,
    )
    budget: Optional[str] = Field(
        default=None,
        max_length=200,
    )
    platform: Optional[str] = Field(
        default=None,
        max_length=100,
    )

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Project description cannot be blank")

        if any(ord(char) < 32 and char not in "\n\t\r" for char in value):
            raise ValueError("Project description contains invalid control characters")

        return value

    @field_validator("budget", "platform")
    @classmethod
    def validate_optional_fields(cls, value: Optional[str]) -> Optional[str]:
        if value is not None and not value.strip():
            raise ValueError("Field cannot be blank")

        return value
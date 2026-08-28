from pydantic import BaseModel
from typing import List, Optional
from enum import Enum


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
    category: RequirementCategory
    text: str
    confidence: float


class ExtractedFeature(BaseModel):
    canonical_name: str
    description: str
    priority: PriorityLevel
    complexity: PriorityLevel
    confidence: float


class RequirementAnalysisResult(BaseModel):
    requirements: List[ExtractedRequirement]
    features: List[ExtractedFeature]


class AnalyzeRequest(BaseModel):
    description: str
    budget: Optional[str] = None
    platform: Optional[str] = None
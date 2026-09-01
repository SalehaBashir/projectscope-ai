from pydantic import BaseModel
from typing import List


class TechStackRecommendation(BaseModel):
    frontend: str
    backend: str
    database: str
    hosting: str
    reasoning: str


class TechStackResult(BaseModel):
    tech_stack: TechStackRecommendation
    folder_structure: List[str]
    guidelines: List[str]
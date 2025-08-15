from typing import Dict, List
from pydantic import BaseModel


class HiringSignals(BaseModel):
    """Structured signals extracted from a job description."""
    keywords: List[str]
    tools: List[str]
    cloud: List[str]
    nice_to_have: List[str]
    weights: Dict[str, float]


class RewrittenProject(BaseModel):
    """Single rewritten project for the resume."""
    title: str
    description: str
    accomplishments: List[str]
    duration: str

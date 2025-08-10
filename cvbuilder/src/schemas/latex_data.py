from typing import List
from pydantic import BaseModel, RootModel


class SkillCategory(BaseModel):
    """Grouping for skills section."""
    category: str
    items: List[str]


class SkillsSchema(RootModel[List[SkillCategory]]):
    """Full skills payload."""
    pass


class ProjectItem(BaseModel):
    """Single project entry."""
    title: str
    description: str
    details: str
    duration: str


class ProjectCategory(BaseModel):
    """Grouping for projects section."""
    category: str
    items: List[ProjectItem]


class ProjectsSchema(RootModel[List[ProjectCategory]]):
    """Full projects payload."""
    pass

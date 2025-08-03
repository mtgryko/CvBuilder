# src/schemas/notion.py
from pydantic import BaseModel, HttpUrl
from typing import List, Optional

# ---------- Personal Info ----------
class PersonalInfo(BaseModel):
    key: str
    value: Optional[str] = None

# ---------- Skills ----------
class Skills(BaseModel):
    tools: List[str]
    tags: List[str]

# ---------- Project ----------
class Project(BaseModel):
    name: str
    status: Optional[str] = None
    category: Optional[str] = None
    tech_stack: List[str]
    description: Optional[str] = None
    notes: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    role: Optional[str] = None
    tags: List[str]

# ---------- Certificate ----------
class Certificate(BaseModel):
    name: str
    issuer: Optional[str] = None
    skills: List[str] = []
    issue_date: Optional[str] = None
    expiration_date: Optional[str] = None
    credential_id: Optional[str] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None

# ---------- Education ----------
class Education(BaseModel):
    level: Optional[str] = None
    university: Optional[str] = None
    field: Optional[str] = None
    specialization: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    duration_years: Optional[float] = None
    url: Optional[HttpUrl] = None
    summary: Optional[str] = None

# ---------- Experience ----------
class Experience(BaseModel):
    role: Optional[str] = None
    company: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    employment_type: Optional[str] = None
    duration: Optional[str] = None
    url: Optional[HttpUrl] = None

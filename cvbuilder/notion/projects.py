"""Project synchronization using the shared Notion client."""

from __future__ import annotations

import json
import os
from datetime import datetime
from typing import List, Optional

from .client import NotionClient
from src.schemas.notion import Project
from src.utils.logger import get_logger

logger = get_logger("notion-projects")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "projects.json")


def compute_duration(start: Optional[str], end: Optional[str]) -> str:
    """Return human readable duration between two ISO dates."""
    if not start:
        return ""
    try:
        start_dt = datetime.fromisoformat(start)
        end_dt = datetime.fromisoformat(end) if end else datetime.now()
    except (TypeError, ValueError):
        return ""

    months = (end_dt.year - start_dt.year) * 12 + (end_dt.month - start_dt.month)
    if months <= 0:
        months = 1
    years, months = divmod(months, 12)
    parts: List[str] = []
    if years:
        parts.append(f"{years} yr")
    if months:
        parts.append(f"{months} mo")
    return " ".join(parts)


class Projects(NotionClient):
    """Client to fetch and persist project information from Notion."""

    def __init__(self, database_id: str | None = None) -> None:
        super().__init__()
        self.database_id = database_id or os.getenv("NOTION_PROJECT_ID")

    def fetch(self):
        if not self.database_id:
            logger.error("NOTION_PROJECT_ID not set. Skipping project fetch.")
            return None
        return self.query_database(self.database_id)

    def extract(self, notion_data) -> List[Project]:
        projects: List[Project] = []
        for item in notion_data.get("results", []):
            properties = item.get("properties", {})
            project_name = properties.get("Project name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled Project")
            status = properties.get("Status", {}).get("select", {}).get("name", "No Status")
            category = properties.get("Category", {}).get("select", {}).get("name", "No Category")
            tech_stack = [t["name"] for t in properties.get("Tech Stack", {}).get("multi_select", [])]
            description = properties.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Description")
            notes = properties.get("Detailed Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Notes")
            start_date = properties.get("Start Date", {}).get("date", {}).get("start")
            end_date_prop = properties.get("End Date")
            end_date = end_date_prop["date"]["start"] if end_date_prop and end_date_prop.get("date") else None
            duration = compute_duration(start_date, end_date)
            role = properties.get("Role", {}).get("select", {}).get("name", "No Role")
            tags = [t["name"] for t in properties.get("Tags", {}).get("multi_select", [])]
            project_entry = Project(
                name=project_name,
                status=status,
                category=category,
                tech_stack=tech_stack,
                description=description,
                notes=notes,
                duration=duration,
                role=role,
                tags=tags,
            )
            projects.append(project_entry)
        return projects

    def save(self, projects: List[Project]) -> None:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in projects], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d projects to %s", len(projects), DATA_PATH)

    def sync(self) -> None:
        notion_data = self.fetch()
        if not notion_data:
            logger.error("No project data fetched.")
            return
        projects = self.extract(notion_data)
        self.save(projects)

# src/notion/projects.py

from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
from src.schemas.notion import Project  # <-- use Pydantic model
from datetime import datetime
from typing import Optional
import requests
import json
import os

logger = get_logger("notion-projects")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'projects.json')


def _compute_duration(start: Optional[str], end: Optional[str]) -> str:
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
    parts = []
    if years:
        parts.append(f"{years} yr")
    if months:
        parts.append(f"{months} mo")
    return " ".join(parts)

def fetch_projects(project_id):
    """Fetch project data from Notion"""
    url = f"https://api.notion.com/v1/databases/{project_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)

    if response.status_code != 200:
        # The logging call previously passed the response JSON as a separate argument
        # without a formatting placeholder which caused a TypeError during
        # string formatting. We explicitly format the error message so the
        # response body is logged correctly.
        try:
            error_detail = response.json()
        except ValueError:
            error_detail = response.text
        logger.error("Error fetching data: %s", error_detail)
        return None

    return response.json()

def extract_project_data(notion_data):
    """Extract relevant project details and return a list of Project models"""
    projects = []

    for item in notion_data.get("results", []):
        properties = item.get("properties", {})

        project_name = properties.get("Project name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled Project")
        status = properties.get("Status", {}).get("select", {}).get("name", "No Status")
        category = properties.get("Category", {}).get("select", {}).get("name", "No Category")
        tech_stack = [t["name"] for t in properties.get("Tech Stack", {}).get("multi_select", [])]
        description = properties.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Description")
        notes = properties.get("Detailed Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Notes")
        start_date = properties.get("Start Date", {}).get("date", {}).get("start")
        end_prop = properties.get("End Date")
        end_date = end_prop["date"]["start"] if end_prop and end_prop.get("date") else None

        duration = _compute_duration(start_date, end_date)

        role = properties.get("Role", {}).get("select", {}).get("name", "No Role")
        tags = [t["name"] for t in properties.get("Tags", {}).get("multi_select", [])]

        # Create Pydantic model instance
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

def save_projects_to_file(projects):
    """Dump project data to data/projects.json"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([p.model_dump(mode="json") for p in projects], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(projects)} projects to {DATA_PATH}")

def run():
    project_id = os.getenv("NOTION_PROJECT_ID")
    if not project_id:
        logger.error("NOTION_PROJECT_ID not set. Skipping project fetch.")
        return
    notion_data = fetch_projects(project_id)
    if not notion_data:
        logger.error("No NOTION_PROJECT data not fetched.")
        return

    projects = extract_project_data(notion_data)
    save_projects_to_file(projects)

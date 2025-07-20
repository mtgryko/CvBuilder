# src/notion/projects.py

from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
import requests
import json
import os

logger = get_logger("notion-projects")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'projects.json')

def fetch_projects(project_id):
    """Fetch project data from Notion"""
    url = f"https://api.notion.com/v1/databases/{project_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)

    if response.status_code != 200:
        logger.error("Error fetching data:", response.json())
        return None

    return response.json()

def extract_project_data(notion_data):
    """Extract relevant project details from Notion API response"""
    projects = []

    for item in notion_data.get("results", []):
        properties = item.get("properties", {})

        project_name = properties.get("Project name", {}).get("title", [{}])[0].get("text", {}).get("content", "Untitled Project")
        status = properties.get("Status", {}).get("select", {}).get("name", "No Status")
        category = properties.get("Category", {}).get("select", {}).get("name", "No Category")
        tech_stack = [t["name"] for t in properties.get("Tech Stack", {}).get("multi_select", [])]
        description = properties.get("Description", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Description")
        notes = properties.get("Detailed Notes", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "No Notes")
        start_date = properties.get("Start Date", {}).get("date", {}).get("start", "No Start Date")

        end_date = properties.get("End Date")
        end_date = end_date["date"]["start"] if end_date and end_date.get("date") else "No End Date"

        role = properties.get("Role", {}).get("select", {}).get("name", "No Role")
        tags = [t["name"] for t in properties.get("Tags", {}).get("multi_select", [])]

        projects.append({
            "name": project_name,
            "status": status,
            "category": category,
            "tech_stack": ", ".join(tech_stack),
            "description": description,
            "notes": notes,
            "start_date": start_date,
            "end_date": end_date,
            "role": role,
            "tags": ", ".join(tags),
        })

    return projects

def save_projects_to_file(projects):
    """Dump project data to data/projects.json"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump(projects, f, indent=2, ensure_ascii=False)
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

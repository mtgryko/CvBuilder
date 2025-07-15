from utils.api import NOTION_BASE_HEADERS

import requests

def fetch_projects(project_id):
    """Fetch project data from Notion"""
    url = f"https://api.notion.com/v1/databases/{project_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)
    
    if response.status_code != 200:
        print("Error fetching data:", response.json())
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


def display_projects(projects):
    """Print retrieved projects"""
    for idx, project in enumerate(projects, 1):
        print(f"{idx}. {project['name']} ({project['status']})")
        print(f"   Category: {project['category']}")
        print(f"   Tech Stack: {project['tech_stack']}")
        print(f"   Description: {project['description']}")
        print(f"   Notes: {project['notes']}")
        print(f"   Start Date: {project['start_date']} - End Date: {project['end_date']}")
        print(f"   Role: {project['role']}")
        print(f"   Tags: {project['tags']}\n")

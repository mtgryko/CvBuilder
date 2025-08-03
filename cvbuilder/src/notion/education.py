# src/notion/education.py
from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
from src.utils.commons import safe_get_text, safe_get_title, safe_get_date
from src.schemas.notion import Education

import requests
import json
import os

logger = get_logger("notion-education")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'education.json')

def fetch_education(db_id):
    """Fetch education data from Notion"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)
    if response.status_code != 200:
        logger.error(f"Error fetching education: {response.json()}")
        return None
    return response.json()

def extract_education(notion_data):
    """Extract education info and return a list of Education models"""
    logger.info(notion_data)
    
    education = []
    for item in notion_data.get("results", []):
        props = item.get("properties", {})

        level = safe_get_title(props.get("Level", {}))
        university = safe_get_text(props.get("University", {}))
        field = safe_get_text(props.get("Field of study", {}))
        specialization = safe_get_text(props.get("Specialization", {}))
        start_date = safe_get_date(props.get("Start Date Aprox", {}))
        end_date = safe_get_date(props.get("End Date Aprox", {}))
        duration_years = props.get("Duration (years)", {}).get("formula", {}).get("number", None)

        # Build CV-friendly summary
        summary = f"{level} in {field}" if field else level
        if specialization:
            summary += f", specialization in {specialization}"
        summary += f" – {university}"
        if start_date or end_date:
            summary += f" ({start_date} – {end_date or 'Present'})"
        if duration_years:
            summary += f" [{duration_years} years]"

        # Create Pydantic model instance
        edu_entry = Education(
            level=level,
            university=university,
            field=field,
            specialization=specialization,
            start_date=start_date,
            end_date=end_date,
            duration_years=duration_years,
            url=item.get("url", ""),
            summary=summary
        )
        education.append(edu_entry)
    return education

def save_education_to_file(data):
    """Save list of Education models to JSON"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([e.model_dump(mode="json") for e in data], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} education records to {DATA_PATH}")

def run():
    db_id = os.getenv("NOTION_EDUCATION_ID")
    if not db_id:
        logger.error("NOTION_EDUCATION_ID not set. Skipping education fetch.")
        return
    notion_data = fetch_education(db_id)
    if not notion_data:
        logger.error("No education data fetched.")
        return
    data = extract_education(notion_data)
    save_education_to_file(data)

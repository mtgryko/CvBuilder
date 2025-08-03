# src/notion/experience.py
from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
from src.utils.commons import safe_get_text, safe_get_title, safe_get_date
from src.schemas.notion import Experience

import requests
import json
import os

logger = get_logger("notion-experience")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'experience.json')

def fetch_experience(db_id):
    """Fetch work experience data from Notion"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)
    if response.status_code != 200:
        logger.error(f"Error fetching experience: {response.json()}")
        return None
    return response.json()

def extract_experience(notion_data):
    """Extract relevant fields and return a list of Experience models"""
    logger.info(notion_data)
    
    experiences = []
    for item in notion_data.get("results", []):
        props = item.get("properties", {})

        role = safe_get_title(props.get("Headline", {}))
        company = safe_get_text(props.get("Company", {}))
        start_date = safe_get_date(props.get("Start Date Aprox", {}))
        end_date = safe_get_date(props.get("End Date Aprox", {}))
        employment_type = safe_get_text(props.get("Employment time", {}))
        duration = props.get("Duration", {}).get("formula", {}).get("string", "")

        # Create Pydantic model instance
        exp_entry = Experience(
            role=role,
            company=company,
            start_date=start_date,
            end_date=end_date,
            employment_type=employment_type,
            duration=duration,
            url=item.get("url", "")
        )
        experiences.append(exp_entry)
    return experiences

def save_experience_to_file(data):
    """Save list of Experience models to JSON"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([e.model_dump(mode="json") for e in data], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} experiences to {DATA_PATH}")

def run():
    db_id = os.getenv("NOTION_EXPERIENCE_ID")
    if not db_id:
        logger.error("NOTION_EXPERIENCE_ID not set. Skipping experience fetch.")
        return
    notion_data = fetch_experience(db_id)
    if not notion_data:
        logger.error("No experience data fetched.")
        return
    data = extract_experience(notion_data)
    save_experience_to_file(data)

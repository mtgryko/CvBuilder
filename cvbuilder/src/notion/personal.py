# src/notion/personal.py
from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
from src.schemas.notion import PersonalInfo

import requests
import json
import os

logger = get_logger("notion-personal-info")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'personal_info.json')

def fetch_personal_info(info_id):
    """Fetch personal info data from Notion"""
    url = f"https://api.notion.com/v1/databases/{info_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)

    if response.status_code != 200:
        logger.error(f"Error fetching personal info: {response.json()}")
        return None

    return response.json()

def extract_personal_info(notion_data):
    """Extract key-value style personal info as a list of PersonalInfo models"""
    personal_info = []

    for item in notion_data.get("results", []):
        properties = item.get("properties", {})
        key = (
            properties.get("Name", {})
            .get("title", [{}])[0]
            .get("text", {})
            .get("content", None)
        )
        value = (
            properties.get("Value", {})
            .get("rich_text", [{}])[0]
            .get("text", {})
            .get("content", None)
        )

        if key:  # skip entries without keys
            personal_info.append(PersonalInfo(key=key, value=value or ""))

    return personal_info

def save_personal_info_to_file(info):
    """Dump personal info list to data/personal_info.json"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        json.dump([p.model_dump(mode="json") for p in info], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(info)} personal info entries to {DATA_PATH}")

def run():
    info_id = os.getenv("NOTION_PERSONAL_INFO_ID")
    if not info_id:
        logger.error("NOTION_PERSONAL_INFO_ID not set. Skipping personal info fetch.")
        return
    notion_data = fetch_personal_info(info_id)
    if not notion_data:
        logger.error("No personal info data fetched.")
        return

    info = extract_personal_info(notion_data)
    save_personal_info_to_file(info)

# src/notion/certificates.py
from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger
from src.utils.commons import safe_get_text, safe_get_title, safe_get_date, safe_get_multi_select
from src.schemas.notion import Certificate 

import requests
import json
import os

logger = get_logger("notion-certificates")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'certificates.json')

def fetch_certificates(db_id):
    """Fetch certificates data from Notion"""
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    response = requests.post(url, headers=NOTION_BASE_HEADERS)
    if response.status_code != 200:
        logger.error(f"Error fetching certificates: {response.json()}")
        return None
    return response.json()

def extract_certificates(notion_data):
    """Extract certificates and return a list of Certificate models"""
    logger.info(notion_data)
    
    certificates = []
    for item in notion_data.get("results", []):
        props = item.get("properties", {})

        name = safe_get_title(props.get("Name", {}))
        skills = safe_get_multi_select(props.get("Skills", {}))
        credential_id = safe_get_text(props.get("Credential ID", {}))
        issue_date = safe_get_date(props.get("Issue date", {}))
        expiration_date = safe_get_date(props.get("Expiration date", {}))
        url = props.get("Url", {}).get("url", "")
        issuer = ""  # (If you later add an Issuer field, extract it here)

        # Build a CV-friendly text summary
        summary = f"{name}"
        if issuer:
            summary += f" – {issuer}"
        if issue_date:
            summary += f" ({issue_date[:4]})"
        if skills:
            summary += f" [{', '.join(skills)}]"

        # Create Pydantic model instance
        certificate = Certificate(
            name=name,
            issuer=issuer,
            skills=skills,
            issue_date=issue_date,
            expiration_date=expiration_date,
            credential_id=credential_id,
            url=url if url else None,
            summary=summary
        )
        certificates.append(certificate)
    return certificates

def save_certificates_to_file(data):
    """Save list of Certificate models to JSON"""
    os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
    with open(DATA_PATH, 'w', encoding='utf-8') as f:
        # Serialize using .model_dump(mode="json") for Pydantic models
        json.dump([c.model_dump(mode="json") for c in data], f, indent=2, ensure_ascii=False)
    logger.info(f"Saved {len(data)} certificates to {DATA_PATH}")

def run():
    db_id = os.getenv("NOTION_CERTIFICATES_ID")
    if not db_id:
        logger.error("NOTION_CERTIFICATES_ID not set. Skipping certificate fetch.")
        return
    notion_data = fetch_certificates(db_id)
    if not notion_data:
        logger.error("No certificate data fetched.")
        return
    data = extract_certificates(notion_data)
    save_certificates_to_file(data)

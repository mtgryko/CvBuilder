"""Education synchronization using the shared Notion client."""

from __future__ import annotations

import json
import os
from typing import List

from .client import NotionClient
from src.schemas.notion import Education as EducationModel
from src.utils.commons import safe_get_date, safe_get_text, safe_get_title
from src.utils.logger import get_logger

logger = get_logger("notion-education")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "education.json")


class EducationClient(NotionClient):
    """Client to fetch and persist education information from Notion."""

    def __init__(self, database_id: str | None = None) -> None:
        super().__init__()
        self.database_id = database_id or os.getenv("NOTION_EDUCATION_ID")

    def fetch(self):
        if not self.database_id:
            logger.error("NOTION_EDUCATION_ID not set. Skipping education fetch.")
            return None
        return self.query_database(self.database_id)

    def extract(self, notion_data) -> List[EducationModel]:
        logger.info(notion_data)
        education: List[EducationModel] = []
        for item in notion_data.get("results", []):
            props = item.get("properties", {})
            level = safe_get_title(props.get("Level", {}))
            university = safe_get_text(props.get("University", {}))
            field = safe_get_text(props.get("Field of study", {}))
            specialization = safe_get_text(props.get("Specialization", {}))
            start_date = safe_get_date(props.get("Start Date Aprox", {}))
            end_date = safe_get_date(props.get("End Date Aprox", {}))
            duration_years = props.get("Duration (years)", {}).get("formula", {}).get("number", None)
            summary = f"{level} in {field}" if field else level
            if specialization:
                summary += f", specialization in {specialization}"
            summary += f" – {university}"
            if start_date or end_date:
                summary += f" ({start_date} – {end_date or 'Present'})"
            if duration_years:
                summary += f" [{duration_years} years]"
            edu_entry = EducationModel(
                level=level,
                university=university,
                field=field,
                specialization=specialization,
                start_date=start_date,
                end_date=end_date,
                duration_years=duration_years,
                url=item.get("url", ""),
                summary=summary,
            )
            education.append(edu_entry)
        return education

    def save(self, data: List[EducationModel]) -> None:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(mode="json") for e in data], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d education records to %s", len(data), DATA_PATH)

    def sync(self) -> None:
        notion_data = self.fetch()
        if not notion_data:
            logger.error("No education data fetched.")
            return
        data = self.extract(notion_data)
        self.save(data)

# Backwards compatibility alias
Education = EducationClient

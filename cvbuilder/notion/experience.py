"""Work experience synchronization using the shared Notion client."""

from __future__ import annotations

import json
import os
from typing import List

from .client import NotionClient
from src.schemas.notion import Experience as ExperienceModel
from src.utils.commons import safe_get_date, safe_get_text, safe_get_title
from src.utils.logger import get_logger

logger = get_logger("notion-experience")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "experience.json")


class ExperienceClient(NotionClient):
    """Client to fetch and persist experience information from Notion."""

    def __init__(self, database_id: str | None = None) -> None:
        super().__init__()
        self.database_id = database_id or os.getenv("NOTION_EXPERIENCE_ID")

    def fetch(self):
        if not self.database_id:
            logger.error("NOTION_EXPERIENCE_ID not set. Skipping experience fetch.")
            return None
        return self.query_database(self.database_id)

    def extract(self, notion_data) -> List[ExperienceModel]:
        logger.info(notion_data)
        experiences: List[ExperienceModel] = []
        for item in notion_data.get("results", []):
            props = item.get("properties", {})
            role = safe_get_title(props.get("Headline", {}))
            company = safe_get_text(props.get("Company", {}))
            start_date = safe_get_date(props.get("Start Date Aprox", {}))
            end_date = safe_get_date(props.get("End Date Aprox", {}))
            employment_type = safe_get_text(props.get("Employment time", {}))
            duration = props.get("Duration", {}).get("formula", {}).get("string", "")
            exp_entry = ExperienceModel(
                role=role,
                company=company,
                start_date=start_date,
                end_date=end_date,
                employment_type=employment_type,
                duration=duration,
                url=item.get("url", ""),
            )
            experiences.append(exp_entry)
        return experiences

    def save(self, data: List[ExperienceModel]) -> None:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([e.model_dump(mode="json") for e in data], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d experiences to %s", len(data), DATA_PATH)

    def sync(self) -> None:
        notion_data = self.fetch()
        if not notion_data:
            logger.error("No experience data fetched.")
            return
        data = self.extract(notion_data)
        self.save(data)

# Backwards compatibility alias
Experience = ExperienceClient

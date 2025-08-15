"""Personal information synchronization using the shared Notion client."""

from __future__ import annotations

import json
import os
from typing import List

from .client import NotionClient
from src.schemas.notion import PersonalInfo as PersonalInfoModel
from src.utils.logger import get_logger

logger = get_logger("notion-personal-info")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "personal_info.json")


class PersonalInfoClient(NotionClient):
    """Client to fetch and persist personal information from Notion."""

    def __init__(self, database_id: str | None = None) -> None:
        super().__init__()
        self.database_id = database_id or os.getenv("NOTION_PERSONAL_INFO_ID")

    def fetch(self):
        if not self.database_id:
            logger.error("NOTION_PERSONAL_INFO_ID not set. Skipping personal info fetch.")
            return None
        return self.query_database(self.database_id)

    def extract(self, notion_data) -> List[PersonalInfoModel]:
        personal_info: List[PersonalInfoModel] = []
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
            if key:
                personal_info.append(PersonalInfoModel(key=key, value=value or ""))
        return personal_info

    def save(self, info: List[PersonalInfoModel]) -> None:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([p.model_dump(mode="json") for p in info], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d personal info entries to %s", len(info), DATA_PATH)

    def sync(self) -> None:
        notion_data = self.fetch()
        if not notion_data:
            logger.error("No personal info data fetched.")
            return
        info = self.extract(notion_data)
        self.save(info)

# Backwards compatibility alias
PersonalInfo = PersonalInfoClient

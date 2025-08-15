"""Shared Notion API client."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from src.utils.api import NOTION_BASE_HEADERS
from src.utils.logger import get_logger

logger = get_logger("notion-client")


class NotionClient:
    """Basic HTTP client for the Notion API."""

    base_url = "https://api.notion.com/v1/"

    def __init__(self, headers: Optional[Dict[str, str]] = None) -> None:
        self.headers = headers or NOTION_BASE_HEADERS

    def query_database(self, database_id: str, payload: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Query a Notion database and return the JSON response."""
        url = f"{self.base_url}databases/{database_id}/query"
        response = requests.post(url, headers=self.headers, json=payload or {})
        if response.status_code != 200:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            logger.error("Error fetching data: %s", detail)
            return None
        return response.json()

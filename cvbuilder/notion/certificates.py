"""Certificate synchronization using the shared Notion client."""

from __future__ import annotations

import json
import os
from typing import List

from .client import NotionClient
from src.schemas.notion import Certificate as CertificateModel
from src.utils.commons import safe_get_date, safe_get_multi_select, safe_get_text, safe_get_title
from src.utils.logger import get_logger

logger = get_logger("notion-certificates")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA_PATH = os.path.join(BASE_DIR, "data", "certificates.json")


class CertificatesClient(NotionClient):
    """Client to fetch and persist certificate information from Notion."""

    def __init__(self, database_id: str | None = None) -> None:
        super().__init__()
        self.database_id = database_id or os.getenv("NOTION_CERTIFICATES_ID")

    def fetch(self):
        if not self.database_id:
            logger.error("NOTION_CERTIFICATES_ID not set. Skipping certificate fetch.")
            return None
        return self.query_database(self.database_id)

    def extract(self, notion_data) -> List[CertificateModel]:
        logger.info(notion_data)
        certificates: List[CertificateModel] = []
        for item in notion_data.get("results", []):
            props = item.get("properties", {})
            name = safe_get_title(props.get("Name", {}))
            skills = safe_get_multi_select(props.get("Skills", {}))
            credential_id = safe_get_text(props.get("Credential ID", {}))
            issue_date = safe_get_date(props.get("Issue date", {}))
            expiration_date = safe_get_date(props.get("Expiration date", {}))
            url = props.get("Url", {}).get("url", "")
            issuer = ""
            summary = f"{name}"
            if issuer:
                summary += f" – {issuer}"
            if issue_date:
                summary += f" ({issue_date[:4]})"
            if skills:
                summary += f" [{', '.join(skills)}]"
            certificate = CertificateModel(
                name=name,
                issuer=issuer,
                skills=skills,
                issue_date=issue_date,
                expiration_date=expiration_date,
                credential_id=credential_id,
                url=url if url else None,
                summary=summary,
            )
            certificates.append(certificate)
        return certificates

    def save(self, data: List[CertificateModel]) -> None:
        os.makedirs(os.path.dirname(DATA_PATH), exist_ok=True)
        with open(DATA_PATH, "w", encoding="utf-8") as f:
            json.dump([c.model_dump(mode="json") for c in data], f, indent=2, ensure_ascii=False)
        logger.info("Saved %d certificates to %s", len(data), DATA_PATH)

    def sync(self) -> None:
        notion_data = self.fetch()
        if not notion_data:
            logger.error("No certificate data fetched.")
            return
        data = self.extract(notion_data)
        self.save(data)

# Backwards compatibility alias
Certificates = CertificatesClient

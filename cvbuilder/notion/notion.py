"""High level synchronisation orchestrator for Notion data."""

from __future__ import annotations

from src.utils.logger import get_logger

from .certificates import Certificates
from .education import Education
from .experience import Experience
from .personal import PersonalInfo
from .projects import Projects
from .skills import generate_skills_from_projects

logger = get_logger("notion-main")


class Notion:
    """Facade for synchronising all Notion data sources."""

    def __init__(self) -> None:
        self.projects = Projects()
        self.personal = PersonalInfo()
        self.experience = Experience()
        self.certificates = Certificates()
        self.education = Education()

    def sync_all(self) -> None:
        logger.info("[SYNC] Projects")
        self.projects.sync()

        logger.info("[SYNC] Personal Info")
        self.personal.sync()

        logger.info("[SYNC] Experience")
        self.experience.sync()

        logger.info("[SYNC] Certificates")
        self.certificates.sync()

        logger.info("[SYNC] Education")
        self.education.sync()

        generate_skills_from_projects()
        logger.info("[DONE] All data synced")

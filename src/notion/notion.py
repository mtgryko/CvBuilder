
from src.notion import projects
from src.utils.logger import get_logger

import os

logger = get_logger("notion-main")

class Notion:
    def __init__(self):
        self.project_id = os.getenv("NOTION_PROJECT_ID")

    def fetch_projects(self):
        if not self.project_id:
            logger.error("NOTION_PROJECT_ID not set")
            return []
        data = projects.fetch_projects(self.project_id)
        if not data:
            return []
        return projects.extract_project_data(data)

    def save_projects(self, project_data):
        projects.save_projects_to_file(project_data)

    def sync_projects(self):
        logger.info("[SYNC] Projects")
        data = self.fetch_projects()
        if data:
            self.save_projects(data)
            logger.info("[DONE] Projects synced\n")

    def sync_all(self):
        self.sync_projects()

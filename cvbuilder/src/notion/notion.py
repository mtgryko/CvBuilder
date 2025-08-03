# src/notion/notion.py

from src.notion import projects, skills, personal, experience, certificates, education
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
            
    def sync_personal_info(self):
        logger.info("[SYNC] Personal Info")
        data = personal.fetch_personal_info(os.getenv("NOTION_PERSONAL_INFO_ID"))
        if data:
            extracted = personal.extract_personal_info(data)
            personal.save_personal_info_to_file(extracted)
            logger.info("[DONE] Personal Info synced\n")

    def sync_experience(self):
        logger.info("[SYNC] Experience")
        data = experience.fetch_experience(os.getenv("NOTION_EXPERIENCE_ID"))
        if data:
            extracted = experience.extract_experience(data)
            experience.save_experience_to_file(extracted)
            logger.info("[DONE] Experience synced\n")

    def sync_certificates(self):
        logger.info("[SYNC] Certificates")
        data = certificates.fetch_certificates(os.getenv("NOTION_CERTIFICATES_ID"))
        if data:
            extracted = certificates.extract_certificates(data)
            certificates.save_certificates_to_file(extracted)
            logger.info("[DONE] Certificates synced\n")

    def sync_education(self):
        logger.info("[SYNC] Education")
        data = education.fetch_education(os.getenv("NOTION_EDUCATION_ID"))
        if data:
            extracted = education.extract_education(data)
            education.save_education_to_file(extracted)
            logger.info("[DONE] Education synced\n")

    def sync_all(self):
        self.sync_projects()
        self.sync_personal_info()
        self.sync_experience()
        self.sync_certificates()
        self.sync_education()
        skills.generate_skills_from_projects()
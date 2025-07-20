# src/notion/skills.py

import json
import os
from src.utils.logger import get_logger

logger = get_logger("notion-skills")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
PROJECTS_PATH = os.path.join(BASE_DIR, 'data', 'projects.json')
SKILLS_PATH = os.path.join(BASE_DIR, 'data', 'skills.json')

def generate_skills_from_projects():
    if not os.path.exists(PROJECTS_PATH):
        logger.error(f"Missing {PROJECTS_PATH}")
        return

    with open(PROJECTS_PATH, 'r', encoding='utf-8') as f:
        projects = json.load(f)

    techs = set()
    tags = set()

    for p in projects:
        tech_stack = p.get("tech_stack", "")
        project_tags = p.get("tags", "")

        for tech in tech_stack.split(","):
            tech = tech.strip()
            if tech:
                techs.add(tech)

        for tag in project_tags.split(","):
            tag = tag.strip()
            if tag:
                tags.add(tag)

    skills = {
        "tools": sorted(techs),
        "tags": sorted(tags)
    }

    os.makedirs(os.path.dirname(SKILLS_PATH), exist_ok=True)
    with open(SKILLS_PATH, 'w', encoding='utf-8') as f:
        json.dump(skills, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved flat skills to {SKILLS_PATH}")

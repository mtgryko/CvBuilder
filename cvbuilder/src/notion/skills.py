# src/notion/skills.py

import json
import os
from src.utils.logger import get_logger
from src.schemas.notion import Skills  # <-- use Pydantic model

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
        # Handle both string and list cases for compatibility
        tech_stack = p.get("tech_stack", [])
        if isinstance(tech_stack, str):
            tech_stack = [t.strip() for t in tech_stack.split(",") if t.strip()]
        tags_list = p.get("tags", [])
        if isinstance(tags_list, str):
            tags_list = [t.strip() for t in tags_list.split(",") if t.strip()]

        techs.update(tech_stack)
        tags.update(tags_list)

    skills_model = Skills(
        tools=sorted(techs),
        tags=sorted(tags)
    )

    os.makedirs(os.path.dirname(SKILLS_PATH), exist_ok=True)
    with open(SKILLS_PATH, 'w', encoding='utf-8') as f:
        json.dump(skills_model.model_dump(mode="json"), f, indent=2, ensure_ascii=False)

    logger.info(f"Saved flat skills to {SKILLS_PATH}")

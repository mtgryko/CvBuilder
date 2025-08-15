"""Pipeline utilities for building the skills section."""

import os
from src.notion import skills as notion_skills
from src.cv_agent.selector import CVSelector
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Generate raw skills from projects data."""
    notion_skills.generate_skills_from_projects()


def select_relevant():
    """Run AI selector to curate skills for LaTeX output."""
    selector = CVSelector(
        mode=os.getenv("MODE", "local"),
        model=os.getenv("MODEL", "deepseek-coder:6.7b"),
    )
    selector.select_skills()


def render_section():
    """Load curated skills JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "skills.json")
    return load_json(path)


def run():
    """Execute the full skills pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

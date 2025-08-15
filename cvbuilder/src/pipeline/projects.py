"""Pipeline utilities for building the projects section."""

import os
from src.notion import projects as notion_projects
from src.cv_agent.selector import CVSelector
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Fetch project data from Notion and store raw JSON."""
    notion_projects.run()


def select_relevant():
    """Run AI selector to curate projects for LaTeX output."""
    selector = CVSelector(
        mode=os.getenv("MODE", "local"),
        model=os.getenv("MODEL", "deepseek-coder:6.7b"),
    )
    selector.select_projects()


def render_section():
    """Load curated projects JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "projects.json")
    return load_json(path)


def run():
    """Execute the full projects pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

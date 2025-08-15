"""Pipeline utilities for building the education section."""

import os
import json
from src.notion import education as notion_education
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Fetch education data from Notion and store raw JSON."""
    notion_education.run()


def select_relevant():
    """Copy raw education data to LaTeX directory."""
    src_path = os.path.join(DATA_DIR, "education.json")
    dst_path = os.path.join(LATEX_DIR, "education.json")
    os.makedirs(LATEX_DIR, exist_ok=True)
    data = load_json(src_path)
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def render_section():
    """Load curated education JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "education.json")
    return load_json(path)


def run():
    """Execute the full education pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

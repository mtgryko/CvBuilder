"""Pipeline utilities for building the experience section."""

import os
import json
from notion import Experience
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Fetch experience data from Notion and store raw JSON."""
    client = Experience()
    client.sync()


def select_relevant():
    """Copy raw experience data to LaTeX directory."""
    src_path = os.path.join(DATA_DIR, "experience.json")
    dst_path = os.path.join(LATEX_DIR, "experience.json")
    os.makedirs(LATEX_DIR, exist_ok=True)
    data = load_json(src_path)
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def render_section():
    """Load curated experience JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "experience.json")
    return load_json(path)


def run():
    """Execute the full experience pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

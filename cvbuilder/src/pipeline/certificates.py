"""Pipeline utilities for building the certificates section."""

import os
import json
from src.notion import certificates as notion_certificates
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Fetch certificates data from Notion and store raw JSON."""
    notion_certificates.run()


def select_relevant():
    """Copy raw certificates data to LaTeX directory."""
    src_path = os.path.join(DATA_DIR, "certificates.json")
    dst_path = os.path.join(LATEX_DIR, "certificates.json")
    os.makedirs(LATEX_DIR, exist_ok=True)
    data = load_json(src_path)
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def render_section():
    """Load curated certificates JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "certificates.json")
    return load_json(path)


def run():
    """Execute the full certificates pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

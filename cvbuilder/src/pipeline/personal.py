"""Pipeline utilities for building the contact section."""

import os
import json
from notion import PersonalInfo
from src.utils.commons import load_json

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")


def fetch_raw():
    """Fetch personal information from Notion and store raw JSON."""
    client = PersonalInfo()
    client.sync()


def select_relevant():
    """Convert raw personal info into LaTeX-ready contact data."""
    src_path = os.path.join(DATA_DIR, "personal_info.json")
    dst_path = os.path.join(LATEX_DIR, "contact.json")
    os.makedirs(LATEX_DIR, exist_ok=True)
    data = load_json(src_path)

    contact = {}
    for item in data:
        key = item.get("key", "").strip().lower().replace(" ", "_")
        value = item.get("value", "")
        if not key:
            continue
        if key in contact:
            if isinstance(contact[key], list):
                contact[key].append(value)
            else:
                contact[key] = [contact[key], value]
        else:
            contact[key] = value
    if isinstance(contact.get("github"), list):
        contact["githubs"] = contact.pop("github")

    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(contact, f, indent=2, ensure_ascii=False)


def render_section():
    """Load curated contact JSON ready for LaTeX rendering."""
    path = os.path.join(LATEX_DIR, "contact.json")
    return load_json(path)


def run():
    """Execute the full contact pipeline and return LaTeX data."""
    fetch_raw()
    select_relevant()
    return render_section()

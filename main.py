import os
import json
from dotenv import load_dotenv

from src.utils.projects import run as fetch_and_save_projects
from src.utils.latex import compile_latex, render_resume, save_tex

# Load env vars
load_dotenv(".env")

# Constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LATEX_DIR = os.path.join(BASE_DIR, 'latex_data')

def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {path}\n{e}")
        exit(1)

if __name__ == "__main__":
    # Step 1: Fetch & store Notion projects
    NOTION_PROJECT_ID = os.getenv("NOTION_PROJECT_ID")
    if NOTION_PROJECT_ID:
        fetch_and_save_projects(NOTION_PROJECT_ID)
    else:
        print("NOTION_PROJECT_ID not set. Skipping project fetch.")

    # Step 2: Load JSON data
    contact = load_json(os.path.join(LATEX_DIR, 'contact.json'))
    skills = load_json(os.path.join(LATEX_DIR, 'skills.json'))
    projects = load_json(os.path.join(LATEX_DIR, 'projects.json'))
    experience = load_json(os.path.join(LATEX_DIR, 'experience.json'))
    education = load_json(os.path.join(LATEX_DIR, 'education.json'))

    # Step 3: Render + Save LaTeX + Compile
    tex = render_resume(contact, skills, projects, experience, education)
    save_tex(tex)
    compile_latex()

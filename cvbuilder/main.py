from src.notion.notion import Notion
from latex import compile_latex, render_resume, save_tex
from src.utils.commons import load_json

import os
from dotenv import load_dotenv

# Load env vars
load_dotenv(".env")

# Constants
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
LATEX_DIR = os.path.join(BASE_DIR, 'latex_data')

if __name__ == "__main__":
    # Step 1: Sync data from Notion
    notion = Notion()
    notion.sync_all()

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

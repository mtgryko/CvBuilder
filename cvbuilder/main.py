from src.pipeline import (
    personal as personal_pipeline,
    projects as project_pipeline,
    skills as skills_pipeline,
    experience as experience_pipeline,
    education as education_pipeline,
    certificates as certificates_pipeline,
)
from src.latex import compile_latex, render_resume, save_tex
from src.utils.logger import get_logger

import subprocess
import sys

from dotenv import load_dotenv

# Load env vars
load_dotenv(".env")

logger = get_logger("main")

if __name__ == "__main__":
    # Build each resume section via its dedicated pipeline
    contact = personal_pipeline.run()
    projects = project_pipeline.run()
    skills = skills_pipeline.run()
    experience = experience_pipeline.run()
    education = education_pipeline.run()
    certificates_pipeline.run()

    # Render + Save LaTeX + Compile
    tex = render_resume(contact, skills, projects, experience, education)
    save_tex(tex)
    try:
        compile_latex()
    except subprocess.CalledProcessError as e:
        logger.error("LaTeX compilation failed. See logs above for details.")
        sys.exit(e.returncode or 1)
    except FileNotFoundError:
        logger.error("pdflatex not found. Please ensure LaTeX is installed and in your PATH.")
        sys.exit(1)

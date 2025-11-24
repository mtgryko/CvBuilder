from src.utils.logger import get_logger

import os
import re
import subprocess
from jinja2 import Environment, FileSystemLoader

logger = get_logger("latex")

# Setup paths
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../"))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
MAIN_TEX_PATH = os.path.join(TEMPLATE_DIR, 'main.tex')

# Jinja2 setup
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

def compile_latex(latex_file="main.tex", working_dir=TEMPLATE_DIR, output_dir=OUTPUT_DIR):
    """Compile a LaTeX file using pdflatex"""
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, latex_file],
            cwd=working_dir,
            check=True
        )
        logger.info(f"Compilation successful! PDF is in {output_dir}")
    except subprocess.CalledProcessError as e:
        logger.exception("Error in compilation")
        raise
    except FileNotFoundError:
        logger.exception("Error: pdflatex not found. Please ensure LaTeX is installed and in your PATH.")
        raise

def escape_latex(s):
    if not isinstance(s, str):
        return s
    replace = {
        '&': r'\&', '%': r'\%', '$': r'\$', '#': r'\#',
        '_': r'\_', '{': r'\{', '}': r'\}',
        '~': r'\textasciitilde{}', '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    pattern = re.compile('|'.join(re.escape(k) for k in replace))
    return pattern.sub(lambda m: replace[m.group()], s)

# register the filter with Jinja2 environment
env.filters["escape_latex"] = escape_latex

def render_template(template_name, context):
    try:
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception:
        logger.exception(f"Error rendering template: {template_name}")
        exit(1)

def render_resume(contact, skills, projects, experience, education):
    """Render full LaTeX string for resume"""
    try:
        with open(os.path.join(TEMPLATE_DIR, 'header.tex'), encoding='utf-8') as f:
            tex = f.read()

        # Contact info block
        tex += f"\\namesection{{{escape_latex(contact.get('name', ''))}}}{{%\n"

        contact_lines = []

        if contact.get("phone"):
            contact_lines.append(escape_latex(contact["phone"]))

        if contact.get("email"):
            contact_lines.append(
                f"\\href{{mailto:{escape_latex(contact['email'])}}}{{{escape_latex(contact['email'])}}}"
            )

        if contact.get("linkedin"):
            contact_lines.append(
                f"LinkedIn: \\href{{{escape_latex(contact['linkedin'])}}}{{{escape_latex(contact['linkedin'].replace('https://',''))}}}"
            )

        if "githubs" in contact:
            for gh in contact["githubs"]:
                contact_lines.append(
                    f"{escape_latex(gh['label'])} GitHub: \\href{{{escape_latex(gh['url'])}}}{{{escape_latex(gh['url'].replace('https://', ''))}}}"
                )
        elif contact.get("github"):
            contact_lines.append(
                f"GitHub: \\href{{{escape_latex(contact['github'])}}}{{{escape_latex(contact['github'].replace('https://', ''))}}}"
            )

        if contact_lines:
            tex += " \\\n".join(contact_lines) + " \\\n"

        tex += "}\n"

        # Add your sections
        tex += render_template('skills.tex.j2', {'skills': skills})
        tex += render_template('projects.tex.j2', {'projects': projects})
        tex += render_template('experience.tex.j2', {'experience': experience})
        tex += render_template('education.tex.j2', {'education': education})

        with open(os.path.join(TEMPLATE_DIR, 'footer.tex'), encoding='utf-8') as f:
            tex += f.read()

        return tex
    except Exception as e:
        logger.exception("Error assembling LaTeX document")
        exit(1)

def save_tex(tex_str, path=MAIN_TEX_PATH):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(tex_str)
    logger.info(f"main.tex written to {path}")

import os
import subprocess
import json
from jinja2 import Environment, FileSystemLoader
from dotenv import load_dotenv

# Load env vars if any
load_dotenv()

# Paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
OUTPUT_DIR = os.path.join(BASE_DIR, 'output')
MAIN_TEX_PATH = os.path.join(TEMPLATE_DIR, 'main.tex')

# Jinja2 setup (reuse!)
env = Environment(loader=FileSystemLoader(TEMPLATE_DIR), trim_blocks=True, lstrip_blocks=True)

def compile_latex(latex_file, working_dir, output_dir):
    """Compile a LaTeX file using pdflatex."""
    try:
        subprocess.run(
            ["pdflatex", "-interaction=nonstopmode", "-output-directory", output_dir, latex_file],
            cwd=working_dir,
            check=True
        )
        print(f"Compilation successful! PDF is in {output_dir}")
    except subprocess.CalledProcessError as e:
        print("Error in compilation:", e)
    except FileNotFoundError:
        print("Error: pdflatex not found. Please ensure LaTeX is installed and in your PATH.")

def escape_latex(s):
    if not isinstance(s, str):
        return s
    replace = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    for old, new in replace.items():
        s = s.replace(old, new)
    return s

def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading JSON file: {path}\n{e}")
        exit(1)

def render_template(template_name, context):
    try:
        template = env.get_template(template_name)
        return template.render(**context)
    except Exception as e:
        print(f"Error rendering template: {template_name}\n{e}")
        exit(1)

def render_resume(contact, skills, projects, experience, education):
    """Render the entire LaTeX resume as a string."""
    try:
        with open(os.path.join(TEMPLATE_DIR, 'header.tex'), encoding='utf-8') as f:
            tex = f.read()
        # Use only safe adjustbox options (no scale only axis=true)
        tex += '\n\\begin{document}\n\\begin{adjustbox}{minipage=\\textwidth,center,max height=\\textheight}\n'

        # Contact info block
        tex += f"""\\namesection{{{escape_latex(contact['name'])}}}{{%
        {escape_latex(contact['phone'])} \\\\
        \\href{{mailto:{escape_latex(contact['email'])}}}{{{escape_latex(contact['email'])}}} \\\\
        LinkedIn: \\href{{{escape_latex(contact['linkedin'])}}}{{{escape_latex(contact['linkedin'].replace('https://',''))}}} \\\\
        """
        if "githubs" in contact:
            for gh in contact["githubs"]:
                tex += f'{escape_latex(gh["label"])} GitHub: \\href{{{escape_latex(gh["url"])}}}{{{escape_latex(gh["url"].replace("https://", ""))}}} \\\\\n'
        elif "github" in contact:
            tex += f'GitHub: \\href{{{escape_latex(contact["github"])}}}{{{escape_latex(contact["github"].replace("https://", ""))}}}\n'
        tex += "}\n"

        tex += render_template('skills.tex.j2', {'skills': skills})
        tex += render_template('projects.tex.j2', {'projects': projects})
        tex += render_template('experience.tex.j2', {'experience': experience})
        tex += render_template('education.tex.j2', {'education': education})

        with open(os.path.join(TEMPLATE_DIR, 'footer.tex'), encoding='utf-8') as f:
            tex += f.read()
        return tex
    except Exception as e:
        print(f"Error assembling LaTeX document:\n{e}")
        exit(1)

if __name__ == "__main__":
    # Load your JSON data
    contact = load_json(os.path.join(DATA_DIR, 'contact.json'))
    skills = load_json(os.path.join(DATA_DIR, 'skills.json'))
    projects = load_json(os.path.join(DATA_DIR, 'projects.json'))
    experience = load_json(os.path.join(DATA_DIR, 'experience.json'))
    education = load_json(os.path.join(DATA_DIR, 'education.json'))

    # Render the resume
    tex = render_resume(contact, skills, projects, experience, education)

    # Save to main.tex
    with open(MAIN_TEX_PATH, 'w', encoding='utf-8') as f:
        f.write(tex)
    print(f"main.tex written to {MAIN_TEX_PATH}")

    # Make sure output dir exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    # Compile LaTeX
    compile_latex("main.tex", TEMPLATE_DIR, OUTPUT_DIR)

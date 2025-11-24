# CVBuilder

A command-line pipeline that assembles a tailored resume by syncing content from Notion, curating the most relevant entries with an LLM, and rendering the final document with LaTeX.

## Key Features
- Pulls personal, project, skill, education, experience, and certificate data from dedicated Notion databases.
- Uses the CV agent to score projects and skills against a target job description using OpenAI or a local Ollama model.
- Renders modular Jinja2 templates into LaTeX and compiles to PDF (`output/main.pdf`).
- Ships with pytest-based checks for critical data transformations and duration calculations.
- Optional Docker Compose stack to run the builder alongside an Ollama model server.

## Project Structure
```
cvbuilder/
|-- main.py             # CLI entry point that runs the full pipeline
|-- data/               # Raw JSON dumps fetched from Notion
|-- job_descriptions/   # Target job description text read by the selector
|-- latex_data/         # Curated JSON consumed by LaTeX templates
|-- notion/             # Notion API clients and sync helpers
|-- output/             # Generated LaTeX artefacts including main.pdf
|-- src/
|   |-- pipeline/       # Section-specific ETL steps
|   |-- cv_agent/       # LLM selector, prompts, and validation helpers
|   |-- schemas/        # Pydantic schemas for selector and LaTeX payloads
|   |-- latex.py        # Rendering + pdflatex wrapper
|   |-- utils/          # Shared utilities (API helpers, logging, etc.)
|-- templates/          # Header/footer plus section templates (Jinja2)
|-- tests/              # Pytest suite
|-- .env                # Runtime secrets (never commit real keys)
```

## Prerequisites
- Python 3.10+ (virtual environment recommended).
- `pdflatex` available on your PATH (TeX Live or MiKTeX).
- Access to the relevant Notion databases and API key.
- Either an OpenAI API key or a locally served Ollama model that matches the configured `MODEL`.

## Configuration
Create `cvbuilder/.env` (do **not** check real secrets into source control) with values similar to:
```
NOTION_PROJECT_ID=<uuid of Notion project database>
NOTION_PERSONAL_INFO_ID=<uuid of Notion personal info database>
NOTION_EDUCATION_ID=<uuid of Notion education database>
NOTION_EXPERIENCE_ID=<uuid of Notion experience database>
NOTION_CERTIFICATES_ID=<uuid of Notion certificates database>
NOTION_API_KEY=<notion integration secret>
OPENAI_API_KEY=<openai key when MODE=openai>
MODE=local            # "local" for Ollama, "openai" to call OpenAI directly
MODEL=deepseek-v2:16b # Ollama model or OpenAI model name
OLLAMA_HOST=http://localhost:11434 # required when MODE=local
```
You can point `job_descriptions/job.txt` to any target role text and update `src/cv_agent/config.json` if you need a different path or character budgets.

## Local Setup
1. `cd cvbuilder`
2. (Optional) `python -m venv .venv && .\\.venv\\Scripts\\activate`
3. `pip install -r requirements.txt`
4. Ensure `pdflatex` is installed and reachable (`pdflatex --version`).

## Running the Builder
```
python main.py
```
The command performs the following steps:
1. Synchronises every Notion database into `data/`.
2. Runs the CV selector to rewrite and filter projects/skills against the job description, saving curated payloads into `latex_data/`.
3. Renders the LaTeX templates and compiles `templates/main.tex` into `output/main.pdf`.

Logs from the LLM prompts are appended to `logs/model_responses.log`, which helps debug malformed responses.

## Docker Compose Workflow
The repository includes a two-service stack:
```
docker compose up --build
```
- `cv_builder` runs the Python pipeline inside a container that mounts the local repo.
- `ollama` launches the Ollama server, ensures the configured `MODEL` is available, and exposes it on port 11434 (GPU runtime expected by default).

Update `.env` before starting the stack so containers have the correct credentials. Adjust `docker-compose.yaml` if you do not have GPU support or prefer CPU inference.

## Testing
Install dev dependencies and execute:
```
pytest
```
The suite covers data extraction utilities, LaTeX escaping, and schema validation. Add new tests whenever you modify transformation logic or introduce additional templates.

## Troubleshooting
- **LaTeX compilation fails**: inspect `output/main.log` for missing packages or syntax issues; ensure non-ASCII characters are escaped or encoded.
- **Empty sections**: confirm the Notion databases contain entries and that the API key has access to them.
- **LLM errors**: check `logs/model_responses.log` and verify MODE/MODEL/OLLAMA_HOST or OpenAI credentials.
- **Job mismatch**: refresh `job_descriptions/job.txt` with the target role and re-run the pipeline to regenerate the tailored resume.

## Contributing
- Keep secrets out of git history.
- Add or update pytest cases alongside behavioural changes.
- Run the full pipeline locally before opening a pull request to confirm the PDF still builds.

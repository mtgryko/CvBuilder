# CV Agent Subsystem

This document explains how the resume-selection agents work, how they are configured, and how to extend or troubleshoot them.

## Overview
The CV agent subsystem curates project and skill entries so that the generated resume matches a specific job description. It orchestrates the following steps:
1. Extract hiring signals from the target job description.
2. Score and select the most relevant projects from the raw Notion export.
3. Rewrite the selected projects into concise resume-ready snippets while enforcing character budgets and preventing hallucinated tech stacks.
4. Choose and group the most relevant skills for the same job description.
5. Persist all curated content into `latex_data/` for consumption by the LaTeX renderer.

All agent calls are validated against Pydantic schemas to guarantee that downstream templates receive well-formed JSON.

## Key Modules
- `src/cv_agent/agent.py` - Thin wrapper around either OpenAI or Ollama chat APIs. Handles mode switching, temperature configuration, and JSON extraction.
- `src/cv_agent/selector.py` - Coordinates the multi-stage selection pipeline (signal extraction, scoring, rewriting, grouping) and writes validated JSON outputs.
- `src/cv_agent/validator.py` - Provides `ask_and_validate_json`, a retry helper that enforces schema compliance and optionally logs malformed responses for debugging.
- `src/cv_agent/prompts/` - Prompt templates used at each stage (`extract_signals.txt`, `rewrite_project.txt`, `select_skills.txt`). Placeholders are formatted at runtime with job descriptions, project data, or configuration values.
- `src/schemas/selector.py` and `src/schemas/latex_data.py` - Strict schemas for model outputs and LaTeX-ready payloads.
- `src/cv_agent/config.json` - Central configuration for character budgets and the job description file path.

## Data Flow
```
job_descriptions/job.txt ---> CVSelector._extract_signals() ------+
                                                               | signals
                                                               v
data/projects.json -----+--> CVSelector._score_projects() -> top projects
                        |                                        |
                        |                                        v
                        +--> CVSelector.select_projects() -> latex_data/projects.json

raw skills (generated via Notion pipeline) --> CVSelector.select_skills() -> latex_data/skills.json
```

1. `CVSelector.select_projects` loads the job description and raw project JSON, extracts hiring signals, scores projects lexically, and rewrites the best matches. The rewritten projects are validated against `ProjectsSchema` before being saved.
2. `CVSelector.select_skills` uses the same job description to cluster and trim skills, outputting data that matches `SkillsSchema`.
3. Both methods write to `latex_data/` so the LaTeX renderer can render the updated sections without direct model calls.

## Configuration and Environment
| Setting | Description |
|---------|-------------|
| `MODE` | `openai` to call the OpenAI API or `local` to target an Ollama server. Defaults to `local` in the pipelines. |
| `MODEL` | Model identifier for the selected backend (for example `gpt-4` or `deepseek-v2:16b`). |
| `OPENAI_API_KEY` | Required when `MODE=openai`. Loaded via `dotenv` before agent instantiation. |
| `OLLAMA_HOST` | Base URL of the Ollama instance, default `http://localhost:11434`. Used when `MODE=local`. |
| `NOTION_*` | Provide database IDs and API key so pipelines can populate `data/` before selection. |

`src/cv_agent/config.json` provides two configurable knobs:
- `job_description_path` - Relative path to the text file containing the target job description.
- `max_characters.projects` / `max_characters.skills` - Global budgets applied by the selector to avoid overlong LaTeX sections.

Adjust these values when tailoring the resume for different roles or length constraints.

## Running the Selector Manually
After the Notion pipelines have produced fresh `data/projects.json` and `data/skills.json`, you can run the selector in isolation (from inside `cvbuilder/` so `src` is on the import path, or set `PYTHONPATH=.` when running from the repo root):

```bash
python -c "from src.cv_agent.selector import CVSelector; CVSelector(mode='local', model='deepseek-v2:16b').run_all()"
```

This regenerates `latex_data/projects.json` and `latex_data/skills.json` without invoking the rest of the resume builder. Override `mode`/`model` to switch providers.

## Logging and Validation
- Each prompt/response pair is appended to `logs/model_responses.log`. Review this file when debugging hallucinated or malformed outputs.
- If schema validation fails, the validator retries once with a corrective prompt seeded with the expected JSON schema and the invalid payload. Persistent failures raise an exception and surface in the console logs.
- API or transport errors from OpenAI/Ollama propagate upward, so wrap standalone calls with additional error handling if needed.

## Extending the Agent Pipeline
1. **New scoring dimensions** - Modify `_score_projects` in `selector.py` to factor in other fields (for example role seniority). Keep the computation deterministic; the selector relies on stable ordering.
2. **Additional sections** - Add new methods to `CVSelector` that read raw data, prompt the model, and write to `latex_data/`. Define matching Pydantic schemas in `src/schemas/` and update `render_resume` to include the section.
3. **Custom prompts** - Introduce new prompt templates in `src/cv_agent/prompts/`. Keep them JSON-only and highlight any character budgets.
4. **Alternative models** - Extend `CVAgent` if you need to call another provider. Implement an `_ask_<provider>` helper and update the mode switch in `__init__` / `ask`.

## Troubleshooting
- **Schema validation errors** - Inspect `logs/model_responses.log`. If the model persistently violates the schema, tighten prompt instructions or increase `retries` when calling `ask_and_validate_json`.
- **Budget overflows** - `CVSelector._enforce_total_budget` trims accomplishments to satisfy `max_characters`. Increase the limit or post-process the data if sections are too sparse.
- **Missing job signals** - Ensure `job_descriptions/job.txt` exists and contains the intended role description. The selector reads it literally.
- **Ollama access errors** - Confirm the Docker Compose stack (or local server) is running and exposes the requested model name.
- **OpenAI rate limits** - Lower `retries`, adjust usage cadence, or cache `latex_data/` files to avoid repeated calls during development.

## Related Tests
Pytest coverage includes `cvbuilder/tests/test_validator.py` for `ask_and_validate_json`, plus downstream duration/transform tests. When modifying selector logic, add targeted cases under `tests/` - for example verifying that `_strip_disallowed` removes unauthorized terms or that `ProjectsSchema` rejects malformed payloads.

## Security Notes
- `.env` contains API keys and database IDs. Never commit real values.
- Prompt logs in `logs/model_responses.log` may include sensitive project descriptions. Treat the log directory as confidential data.

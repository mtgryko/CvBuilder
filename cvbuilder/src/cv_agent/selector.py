# src/cv_agent/selector.py

import os
import json
from src.cv_agent.agent import CVAgent
from src.utils.logger import get_logger

logger = get_logger("cv-selector")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
LATEX_DIR = os.path.join(BASE_DIR, "latex_data")
CONFIG_PATH = os.path.join(BASE_DIR, "src/cv_agent/config.json")
LOG_FILE = os.path.join(BASE_DIR, "logs/model_responses.log")


class CVSelector:
    def __init__(self, mode="openai", model="gpt-4"):
        self.agent = CVAgent(mode=mode, model=model)
        self.config = self._load_config()

    def _load_config(self):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)

    def _load_job_description(self):
        path = os.path.join(BASE_DIR, self.config["job_description_path"])
        with open(path, "r") as f:
            return f.read()

    def _load_prompt(self, filename, **vars):
        prompt_path = os.path.join(BASE_DIR, "src/cv_agent/prompts", filename)
        with open(prompt_path, "r") as f:
            prompt = f.read()
        return prompt.format(**vars)

    def _load_data(self, filename):
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r") as f:
            return json.load(f)

    def _save_latex(self, filename, data):
        os.makedirs(LATEX_DIR, exist_ok=True)
        path = os.path.join(LATEX_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _save_debug_log(self, context, prompt, response):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"\n--- {context} ---\nPROMPT:\n{prompt}\n\nRESPONSE:\n{response}\n\n")

    def _ask_and_parse_json(self, prompt, context, retries=1):
        """Send prompt, log response, and parse JSON with optional retries."""
        for attempt in range(retries + 1):
            result = self.agent.ask(prompt)
            self._save_debug_log(context, prompt, result)

            try:
                return json.loads(result)
            except json.JSONDecodeError:
                logger.error(f"{context}: Failed to parse JSON on attempt {attempt+1}")
                if attempt < retries:
                    prompt = f"Reformat this to valid JSON only:\n\n{result}"
                    continue
                else:
                    logger.error(f"Final raw output was:\n{result}")
                    raise

    def select_projects(self):
        job_desc = self._load_job_description()
        projects = self._load_data("projects.json")
        max_chars = self.config["max_characters"]["projects"]

        prompt = self._load_prompt(
            "select_projects.txt",
            job_desc=job_desc,
            projects=json.dumps(projects, indent=2),
            max_chars=max_chars
        )

        parsed = self._ask_and_parse_json(prompt, "Project Selection", retries=1)
        self._save_latex("projects.json", parsed)
        logger.info("Selected projects saved to LaTeX folder.")

    def select_skills(self):
        job_desc = self._load_job_description()
        skills = self._load_data("skills.json")
        max_chars = self.config["max_characters"]["skills"]

        prompt = self._load_prompt(
            "select_skills.txt",
            job_desc=job_desc,
            skills=json.dumps(skills, indent=2),
            max_chars=max_chars
        )

        parsed = self._ask_and_parse_json(prompt, "Skills Selection", retries=1)
        self._save_latex("skills.json", parsed)
        logger.info("Selected skills saved to LaTeX folder.")

    def run_all(self):
        self.select_projects()
        self.select_skills()

# src/cv_agent/selector.py

import os
import json
import re
from collections import defaultdict
from typing import Dict, List

from src.cv_agent.agent import CVAgent
from src.utils.logger import get_logger
from src.schemas.latex_data import ProjectsSchema, SkillsSchema
from src.schemas.selector import HiringSignals, RewrittenProject
from src.cv_agent.validator import ask_and_validate_json

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
    # ------------------------ Project Selection ---------------------
    def _extract_signals(self, job_desc: str) -> Dict:
        """Stage 1: Extract hiring signals from job description."""
        prompt = self._load_prompt("extract_signals.txt", job_desc=job_desc)
        return ask_and_validate_json(
            self.agent,
            prompt,
            "Signal Extraction",
            schema=HiringSignals,
            retries=1,
            log_callback=self._save_debug_log,
        )

    def _score_projects(
        self, signals: Dict, projects: List[Dict], top_n: int = 6
    ) -> List[Dict]:
        """Stage 2: Score projects lexically against hiring signals."""
        weights = signals.get("weights", {})

        def score(p: Dict) -> float:
            text = " ".join(
                [
                    p.get("name", ""),
                    p.get("description", ""),
                    p.get("notes", ""),
                    " ".join(p.get("tech_stack", [])),
                    " ".join(p.get("tags", [])),
                ]
            ).lower()
            total = 0.0
            for term in signals.get("keywords", []):
                if term.lower() in text:
                    total += weights.get("keywords", 1)
            for term in signals.get("tools", []):
                if term.lower() in text:
                    total += weights.get("tools", 1)
            for term in signals.get("cloud", []):
                if term.lower() in text:
                    total += weights.get("cloud", 1)
            for term in signals.get("nice_to_have", []):
                if term.lower() in text:
                    total += weights.get("nice_to_have", 1)
            return total

        scored = sorted(projects, key=score, reverse=True)
        return scored[:top_n]

    def _extract_allowed_terms(self, project: Dict) -> List[str]:
        """Derive allowed technology terms from project data."""
        allowed = set()
        for field in ("tech_stack", "tags"):
            for t in project.get(field, []):
                allowed.add(t.lower())
        text = f"{project.get('description', '')} {project.get('notes', '')}"
        tokens = re.findall(r"\b[A-Za-z][A-Za-z0-9\+\#\.]*\b", text)
        for tok in tokens:
            if any(c.isupper() or c.isdigit() for c in tok):
                allowed.add(tok.lower())
        return sorted(allowed)

    def _strip_disallowed(self, text: str, allowed: set) -> str:
        """Remove technology terms not present in allowed set."""

        def repl(match: re.Match) -> str:
            word = match.group(0)
            if any(c.isupper() or c.isdigit() for c in word) and word.lower() not in allowed:
                return ""
            return word

        return re.sub(r"\b[A-Za-z][A-Za-z0-9\+\#\.]*\b", repl, text)

    def _enforce_total_budget(self, items: List[Dict], max_chars: int) -> None:
        """Trim accomplishments to satisfy global character budget."""

        def current_len() -> int:
            return sum(len(i["description"]) + len(i["details"]) for i in items)

        while current_len() > max_chars:
            longest = max(items, key=lambda x: len(x["details"].split("\n")))
            details = longest["details"].split("\n")
            if not details:
                break
            details.pop()
            longest["details"] = "\n".join(details).strip()

    def select_projects(self):
        job_desc = self._load_job_description()
        projects = self._load_data("projects.json")
        max_total_chars = self.config["max_characters"]["projects"]

        signals = self._extract_signals(job_desc)
        max_projects = self.config.get("max_projects", 6)
        top_projects = self._score_projects(signals, projects, top_n=max_projects)
        max_per_project = max_total_chars // max(len(top_projects), 1)

        rewritten_items: List[Dict] = []
        for proj in top_projects:
            allowed_terms = self._extract_allowed_terms(proj)
            prompt = self._load_prompt(
                "rewrite_project.txt",
                signals=json.dumps(signals, indent=2),
                project=json.dumps(proj, indent=2),
                allowed_terms=json.dumps(allowed_terms),
                max_chars=max_per_project,
            )
            rewritten = ask_and_validate_json(
                self.agent,
                prompt,
                f"Rewrite Project: {proj.get('name')}",
                schema=RewrittenProject,
                retries=1,
                log_callback=self._save_debug_log,
            )
            allowed_set = set(allowed_terms)
            rewritten["description"] = self._strip_disallowed(
                rewritten["description"], allowed_set
            ).strip()
            rewritten["accomplishments"] = [
                self._strip_disallowed(a, allowed_set).strip()
                for a in rewritten["accomplishments"]
            ]
            item = {
                "title": rewritten["title"],
                "description": rewritten["description"],
                "details": "\n".join(filter(None, rewritten["accomplishments"])),
                "duration": rewritten["duration"],
                "category": proj.get("category", "General"),
            }
            rewritten_items.append(item)

        self._enforce_total_budget(rewritten_items, max_total_chars)

        grouped: Dict[str, List[Dict]] = defaultdict(list)
        for item in rewritten_items:
            category = item.pop("category")
            grouped[category].append(item)
        final_data = [{"category": cat, "items": items} for cat, items in grouped.items()]

        validated = ProjectsSchema.model_validate(final_data).model_dump(mode="python")
        self._save_latex("projects.json", validated)
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

        parsed = ask_and_validate_json(
            self.agent,
            prompt,
            "Skills Selection",
            schema=SkillsSchema,
            retries=1,
            log_callback=self._save_debug_log,
        )
        self._save_latex("skills.json", parsed)
        logger.info("Selected skills saved to LaTeX folder.")

    def run_all(self):
        self.select_projects()
        self.select_skills()

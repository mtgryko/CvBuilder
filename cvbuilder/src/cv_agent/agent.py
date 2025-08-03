# src/cv_agent/agent.py

from openai import OpenAI
from dotenv import load_dotenv
from typing import Literal

load_dotenv()

class CVAgent:
    def __init__(self, mode: Literal["openai", "local"] = "openai", model: str = "gpt-4"):
        self.mode = mode
        self.model = model

        if mode == "openai":
            self.client = OpenAI()
        elif mode == "local":
            import subprocess
            self.local_cmd = "ollama run " + model
        else:
            raise ValueError("Mode must be 'openai' or 'local'")

    def ask(self, prompt: str) -> str:
        if self.mode == "openai":
            return self._ask_openai(prompt)
        elif self.mode == "local":
            return self._ask_local(prompt)

    def _ask_openai(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return completion.choices[0].message.content.strip()

    def _ask_local(self, prompt: str) -> str:
        import subprocess

        process = subprocess.Popen(
            self.local_cmd.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate(input=prompt)
        if stderr:
            raise RuntimeError(f"Local model error: {stderr}")
        return stdout.strip()

# src/cv_agent/agent.py

import os
import re
import requests
import logging
from openai import OpenAI
from dotenv import load_dotenv
from typing import Literal

# Load environment variables
load_dotenv()

# Setup logger
logger = logging.getLogger("cv-agent")
logger.setLevel(logging.DEBUG)


class CVAgent:
    def __init__(self, mode: Literal["openai", "local"] = "openai", model: str = "gpt-4"):
        self.mode = mode
        self.model = model
        if mode == "openai":
            self.client = OpenAI()
        elif mode == "local":
            self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        else:
            raise ValueError("Mode must be 'openai' or 'local'")

    def ask(self, prompt: str, extract_json=True) -> str:
        """
        Ask the model for a response.
        :param extract_json: Extract JSON part from the response if extra text exists.
        """
        logger.debug(f"Using model: {self.model} (mode: {self.mode})")
        logger.debug(f"Prompt sent:\n{prompt}")

        # Call the right backend
        if self.mode == "openai":
            result = self._ask_openai(prompt)
        else:
            result = self._ask_ollama(prompt)

        if not result:
            logger.error("Empty response from model.")
            raise RuntimeError("Model returned an empty response.")

        # Extract JSON if needed
        if extract_json:
            cleaned = self._extract_json(result)
            if cleaned:
                result = cleaned

        logger.debug(f"Cleaned model response:\n{result}")
        return result.strip()

    def _ask_openai(self, prompt: str) -> str:
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
            )
            return completion.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _ask_ollama(self, prompt: str) -> str:
        url = f"{self.ollama_host}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False, "format": "json"}
        try:
            response = requests.post(url, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Ollama error: {response.text}")
            return response.json().get("response", "").strip()
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise

    def _extract_json(self, text: str) -> str:
        """Extract the first JSON object or array from the text."""
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        return match.group(1) if match else text

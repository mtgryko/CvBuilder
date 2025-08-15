import json
import os
import sys
from pydantic import BaseModel

import os
import sys
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.cv_agent.validator import ask_and_validate_json


class DummySchema(BaseModel):
    foo: int


class DummyAgent:
    def __init__(self):
        self.prompts = []
        self.responses = [
            '{"foo": "bar"}',
            '{"foo": 1}',
        ]

    def ask(self, prompt: str, schema=None):
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_retry_prompt_includes_schema():
    agent = DummyAgent()
    result = ask_and_validate_json(
        agent,
        "Initial prompt that should not be repeated",
        "Test",
        schema=DummySchema,
        retries=1,
    )

    assert result == {"foo": 1}
    assert len(agent.prompts) == 2
    schema_json = json.dumps(DummySchema.model_json_schema(), indent=2)
    expected_retry = (
        f"Expected JSON schema:\n{schema_json}\n\n"
        "Invalid JSON:\n{\"foo\": \"bar\"}\n\n"
        "Respond only with corrected JSON."
    )
    assert agent.prompts[1] == expected_retry
    assert "Initial prompt" not in agent.prompts[1]


class ValidAgent:
    def __init__(self):
        self.prompts = []
        self.responses = ['{"foo": 1}']

    def ask(self, prompt: str, schema=None):
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_success_no_retry():
    agent = ValidAgent()
    result = ask_and_validate_json(
        agent,
        "Prompt",
        "Test",
        schema=DummySchema,
    )

    assert result == {"foo": 1}
    assert len(agent.prompts) == 1

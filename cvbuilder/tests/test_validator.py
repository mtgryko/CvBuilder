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

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_retry_prompt_minimal():
    agent = DummyAgent()
    format_hint = '{"foo": 0}'
    result = ask_and_validate_json(
        agent,
        "Initial prompt that should not be repeated",
        "Test",
        schema=DummySchema,
        format_hint=format_hint,
        retries=1,
    )

    assert result == {"foo": 1}
    assert len(agent.prompts) == 2
    expected_retry = (
        f"Expected JSON format:\n{format_hint}\n\n"
        "Invalid JSON:\n{\"foo\": \"bar\"}\n\n"
        "Respond only with corrected JSON."
    )
    assert agent.prompts[1] == expected_retry
    assert "Initial prompt" not in agent.prompts[1]


class SingleQuoteAgent:
    def __init__(self):
        self.prompts = []
        self.responses = ["{'foo': 1}"]

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_auto_fix_with_all_fields():
    agent = SingleQuoteAgent()
    result = ask_and_validate_json(
        agent,
        "Prompt",
        "Test",
        schema=DummySchema,
    )

    assert result == {"foo": 1}
    assert len(agent.prompts) == 1


class MissingFieldAgent:
    def __init__(self):
        self.prompts = []
        self.responses = ["{'bar': 1}", '{"foo": 2}']

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


def test_missing_fields_triggers_retry():
    agent = MissingFieldAgent()
    result = ask_and_validate_json(
        agent,
        "Prompt",
        "Test",
        schema=DummySchema,
        retries=1,
    )

    assert result == {"foo": 2}
    assert len(agent.prompts) == 2
    assert agent.prompts[1] == "Reformat this to valid JSON only:\n\n{'bar': 1}"


class BrokenJsonAgent:
    def __init__(self):
        self.prompts = []
        # Missing closing brace should trigger regex-based extraction
        self.responses = ['{"foo":1, "bar":2']

    def ask(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return self.responses.pop(0)


class DoubleSchema(BaseModel):
    foo: int
    bar: int


def test_regex_fallback_extracts_fields():
    agent = BrokenJsonAgent()
    result = ask_and_validate_json(
        agent,
        "Prompt",
        "Test",
        schema=DoubleSchema,
    )

    assert result == {"foo": 1, "bar": 2}
    assert len(agent.prompts) == 1


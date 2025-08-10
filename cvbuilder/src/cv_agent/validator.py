import ast
import json
import re
from typing import Callable, Optional, Type
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger("cv-validator")


def _extract_fields(text: str, fields) -> Optional[dict]:
    """Best-effort extraction of required fields from broken JSON.

    Uses regular expressions to pull out simple key/value pairs so that a
    partially formatted response (missing braces, mismatched quotes, etc.) can
    still be validated by Pydantic. Only returns a dict if all requested fields
    are present.
    """
    extracted = {}
    for field in fields:
        # match "field": "value" or 'field': 'value'
        pattern = rf"['\"]{field}['\"]\s*:\s*(['\"])(.*?)\1"
        m = re.search(pattern, text)
        if m:
            extracted[field] = m.group(2)
            continue
        # match numeric values without quotes
        m = re.search(rf"['\"]{field}['\"]\s*:\s*([0-9]+)", text)
        if m:
            extracted[field] = m.group(1)
    return extracted if len(extracted) == len(list(fields)) else None

def ask_and_validate_json(
    agent,
    prompt: str,
    context: str,
    *,
    schema: Type[BaseModel],
    format_hint: Optional[str] = None,
    retries: int = 1,
    log_callback: Optional[Callable[[str, str, str], None]] = None,
):
    """Send prompt via agent and validate JSON response against schema.

    If parsing or validation fails, optionally retry with a reformatted prompt
    providing feedback about the expected structure. When re-asking after
    validation errors, only the expected format and the invalid JSON are sent to
    the agent, avoiding resending the entire original prompt. If the response
    contains all required fields but has minor JSON formatting issues, an
    attempt is made to repair it locally before requesting help from the agent.
    """
    for attempt in range(retries + 1):
        result = agent.ask(prompt)
        if log_callback:
            log_callback(context, prompt, result)

        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
            fields = schema.model_fields.keys()
            parsed = None
            if all(field in result for field in fields):
                try:
                    candidate = ast.literal_eval(result)
                    if isinstance(candidate, dict) and all(f in candidate for f in fields):
                        parsed = candidate
                except Exception:
                    parsed = None
                if parsed is None:
                    parsed = _extract_fields(result, fields)
            if parsed is None:
                logger.error(f"{context}: Failed to parse JSON on attempt {attempt+1}")
                if attempt < retries:
                    prompt = f"Reformat this to valid JSON only:\n\n{result}"
                    continue
                logger.error(f"Final raw output was:\n{result}")
                raise

        try:
            return schema.model_validate(parsed).model_dump(mode="python")
        except Exception:
            logger.error(f"{context}: JSON schema validation failed on attempt {attempt+1}")
            if attempt < retries and format_hint:
                prompt = (
                    f"Expected JSON format:\n{format_hint}\n\n"
                    f"Invalid JSON:\n{result}\n\n"
                    f"Respond only with corrected JSON."
                )
                continue
            logger.error(f"Final invalid JSON was:\n{result}")
            raise

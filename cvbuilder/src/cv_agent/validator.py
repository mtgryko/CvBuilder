import json
from typing import Callable, Optional, Set, Type
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger("cv-validator")


def _collect_fields(obj) -> Set[str]:
    """Recursively gather field names from a JSON-like structure."""
    fields: Set[str] = set()
    if isinstance(obj, dict):
        fields.update(obj.keys())
        for v in obj.values():
            fields.update(_collect_fields(v))
    elif isinstance(obj, list):
        for item in obj:
            fields.update(_collect_fields(item))
    return fields


def _expected_fields(format_hint: Optional[str]) -> Set[str]:
    if not format_hint:
        return set()
    try:
        loaded = json.loads(format_hint)
    except json.JSONDecodeError:
        return set()
    return _collect_fields(loaded)


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
    providing feedback about the expected structure.
    """
    base_prompt = prompt
    required_fields = _expected_fields(format_hint)
    for attempt in range(retries + 1):
        result = agent.ask(prompt)
        if log_callback:
            log_callback(context, prompt, result)

        try:
            parsed = json.loads(result)
        except json.JSONDecodeError:
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
                missing = [f for f in required_fields if f not in result]
                missing_msg = f"Missing fields: {', '.join(missing)}\n\n" if missing else ""
                prompt = (
                    f"{base_prompt}\n\n"
                    f"Expected JSON format:\n{format_hint}\n\n"
                    f"Invalid JSON:\n{result}\n\n"
                    f"{missing_msg}"
                    f"Respond only with corrected JSON."
                )
                continue
            logger.error(f"Final invalid JSON was:\n{result}")
            raise

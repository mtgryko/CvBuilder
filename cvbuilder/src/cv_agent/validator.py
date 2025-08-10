import json
from typing import Callable, Optional, Type
from pydantic import BaseModel
from src.utils.logger import get_logger

logger = get_logger("cv-validator")


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
                prompt = (
                    f"{base_prompt}\n\n"
                    f"Expected JSON format:\n{format_hint}\n\n"
                    f"Invalid JSON:\n{result}\n\n"
                    f"Respond only with corrected JSON."
                )
                continue
            logger.error(f"Final invalid JSON was:\n{result}")
            raise

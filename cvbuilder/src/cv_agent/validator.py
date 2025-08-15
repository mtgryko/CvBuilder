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
    retries: int = 1,
    log_callback: Optional[Callable[[str, str, str], None]] = None,
):
    """Send prompt via agent and validate JSON response against schema.

    If validation fails, the function optionally retries with a minimal prompt
    referencing the expected schema and the invalid JSON produced previously.
    """
    for attempt in range(retries + 1):
        result = agent.ask(prompt, schema=schema)
        if log_callback:
            log_callback(context, prompt, result)
        try:
            return schema.model_validate_json(result).model_dump(mode="python")
        except Exception:
            logger.error(
                f"{context}: JSON schema validation failed on attempt {attempt+1}"
            )
            if attempt < retries:
                schema_json = json.dumps(schema.model_json_schema(), indent=2)
                prompt = (
                    f"Expected JSON schema:\n{schema_json}\n\n"
                    f"Invalid JSON:\n{result}\n\n"
                    "Respond only with corrected JSON."
                )
                continue
            logger.error(f"Final invalid JSON was:\n{result}")
            raise

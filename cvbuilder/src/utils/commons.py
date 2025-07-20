import json

from src.utils.logger import get_logger


logger = get_logger("commons")


def load_json(path):
    try:
        with open(path, encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.exception(f"Error loading JSON file: {path}")
        exit(1)
        
        

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
        
def safe_get_text(field):
    """Safely extract content from a rich_text field"""
    texts = field.get("rich_text", [])
    return texts[0].get("text", {}).get("content", "") if texts else ""

def safe_get_title(field):
    """Safely extract content from a title field"""
    texts = field.get("title", [])
    return texts[0].get("text", {}).get("content", "") if texts else ""

def safe_get_date(field):
    """Safely extract start date from a date field"""
    date_obj = field.get("date")
    return date_obj.get("start") if date_obj else ""

def safe_get_multi_select(field):
    """Safely extract names from a multi_select field"""
    return [item.get("name", "") for item in field.get("multi_select", [])]

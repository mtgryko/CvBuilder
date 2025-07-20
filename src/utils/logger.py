import logging

def get_logger(name="cvbuilder"):
    formatter = logging.Formatter(f"[{name.upper()}] [%(asctime)s] [%(levelname)s] %(message)s")
    
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        logger.addHandler(handler)

    return logger
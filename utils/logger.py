"""Logging configuration."""
import logging
import sys
from pythonjsonlogger import jsonlogger
from config.settings import settings


def setup_logging():
    """Setup application logging."""
    log_handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s"
    )
    log_handler.setFormatter(formatter)
    
    root_logger = logging.getLogger()
    root_logger.addHandler(log_handler)
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    return root_logger


logger = setup_logging()


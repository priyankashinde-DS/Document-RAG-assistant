import os
import logging
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logger(name: str = "rag_app") -> logging.Logger:
    """
    Creates a logger that writes:
    - JSON logs to logs/app.log (rotating)
    - human-readable logs to console
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # prevent duplicate handlers
    logger.setLevel(logging.INFO)

    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", "app.log")

    # File handler (JSON)
    file_handler = RotatingFileHandler(log_path, maxBytes=5_000_000, backupCount=3)
    file_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(logging.INFO)

    # Console handler (simple)
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s | %(name)s | %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    logger.propagate = False

    return logger
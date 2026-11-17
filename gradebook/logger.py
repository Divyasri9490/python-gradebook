"""Logging setup for the gradebook.

All modules share one logger that writes INFO and ERROR lines
to logs/app.log in the project folder.
"""

import logging
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LOG_FILE = PROJECT_ROOT / "logs" / "app.log"
LOGGER_NAME = "gradebook"


def get_logger():
    """Return the shared gradebook logger, setting it up the first time.

    The logs folder is created automatically if it does not exist.
    """
    logger = logging.getLogger(LOGGER_NAME)
    if not logger.handlers:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
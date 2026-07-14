"""
==========================================
LOGGER
AI Invoice Extractor
==========================================
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config import LOG_FILE, LOG_LEVEL

# -------------------------------------------------
# Create Log Folder
# -------------------------------------------------

Path(LOG_FILE).parent.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# Logger
# -------------------------------------------------

logger = logging.getLogger("AIInvoiceExtractor")

logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

# Prevent duplicate logs
logger.propagate = False

# Remove existing handlers if app reloads
if logger.hasHandlers():
    logger.handlers.clear()

# -------------------------------------------------
# Formatter
# -------------------------------------------------

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# -------------------------------------------------
# Console Handler
# -------------------------------------------------

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# -------------------------------------------------
# File Handler
# -------------------------------------------------

file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=5 * 1024 * 1024,   # 5 MB
    backupCount=5,
    encoding="utf-8"
)

file_handler.setFormatter(formatter)

# -------------------------------------------------
# Add Handlers
# -------------------------------------------------

logger.addHandler(console_handler)
logger.addHandler(file_handler)

# -------------------------------------------------
# Startup Log
# -------------------------------------------------

logger.info("=" * 60)
logger.info("AI Invoice Extractor Logger Started")
logger.info("=" * 60)
"""
==========================================
CONFIGURATION
AI Invoice Extractor
==========================================
"""
import torch
import os
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------------------------
# Load Environment Variables
# -------------------------------------------------

load_dotenv()

# -------------------------------------------------
# Project Paths
# -------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent

UPLOAD_FOLDER = BASE_DIR / "uploads"
EXPORT_FOLDER = BASE_DIR / "exports"
STATIC_FOLDER = BASE_DIR / "static"
TEMPLATE_FOLDER = BASE_DIR / "templates"
LOG_FOLDER = BASE_DIR / "logs"
DATABASE_FOLDER = BASE_DIR / "database"

# Create folders automatically
for folder in [
    UPLOAD_FOLDER,
    EXPORT_FOLDER,
    STATIC_FOLDER,
    TEMPLATE_FOLDER,
    LOG_FOLDER,
    DATABASE_FOLDER
]:
    folder.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------
# Application
# -------------------------------------------------

APP_NAME = "AI Invoice Extractor"
APP_VERSION = "2.0.0"

# -------------------------------------------------
# Database
# -------------------------------------------------

DATABASE_NAME = "invoice.db"
DATABASE_PATH = DATABASE_FOLDER / DATABASE_NAME

# -------------------------------------------------
# OCR
# -------------------------------------------------

TESSERACT_CMD = os.getenv("TESSERACT_CMD", "")

# -------------------------------------------------
# AI Settings
# -------------------------------------------------


# Local non-quantized Qwen model
MODEL_PATH = str(Path.home() / "Qwen2.5-3B-Instruct")

# Automatically select device
if torch.backends.mps.is_available():
    DEVICE = "mps"          # Apple Silicon GPU
elif torch.cuda.is_available():
    DEVICE = "cuda"         # NVIDIA GPU
else:
    DEVICE = "cpu"

MAX_NEW_TOKENS = 512
TEMPERATURE = 0.0
# File Upload
# -------------------------------------------------

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg"
}

MAX_UPLOAD_SIZE = 25 * 1024 * 1024  # 25 MB

# -------------------------------------------------
# Excel
# -------------------------------------------------

EXCEL_FILENAME = "invoice.xlsx"

# -------------------------------------------------
# Logging
# -------------------------------------------------

LOG_FILE = LOG_FOLDER / "application.log"
LOG_LEVEL = "INFO"

# -------------------------------------------------
# Server
# -------------------------------------------------

HOST = "0.0.0.0"
PORT = 8000
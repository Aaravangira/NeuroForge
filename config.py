"""
==========================================================
AI Invoice Extractor
Production Configuration
==========================================================
Version : 4.0.0
==========================================================
"""

# ==========================================================
# STANDARD LIBRARIES
# ==========================================================

import os
from pathlib import Path
from typing import Any
from urllib.parse import quote_plus

# ==========================================================
# THIRD PARTY LIBRARIES
# ==========================================================

import torch
from dotenv import load_dotenv

# ==========================================================
# LOAD ENVIRONMENT VARIABLES
# ==========================================================

load_dotenv()

# ==========================================================
# PROJECT INFORMATION
# ==========================================================

APP_NAME = "AI Invoice Extractor"
APP_VERSION = "4.0.0"
APP_AUTHOR = "Aarav Sharma"

APP_DESCRIPTION = (
    "Enterprise AI Invoice Extraction Platform"
)

# ==========================================================
# PROJECT ROOT
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent

# ==========================================================
# PROJECT DIRECTORIES
# ==========================================================

UPLOAD_FOLDER = BASE_DIR / "uploads"
EXPORT_FOLDER = BASE_DIR / "exports"
STATIC_FOLDER = BASE_DIR / "static"
TEMPLATE_FOLDER = BASE_DIR / "templates"
LOG_FOLDER = BASE_DIR / "logs"
DATABASE_FOLDER = BASE_DIR / "database"
TEMP_FOLDER = BASE_DIR / "temp"
MODEL_FOLDER = BASE_DIR / "models"
PROMPT_FOLDER = BASE_DIR / "prompts"
REPORT_FOLDER = BASE_DIR / "reports"
CACHE_FOLDER = BASE_DIR / "cache"
VECTOR_FOLDER = BASE_DIR / "vectors"
BACKUP_FOLDER = DATABASE_FOLDER / "backup"

OCR_CACHE_FOLDER = CACHE_FOLDER / "ocr"
AI_CACHE_FOLDER = CACHE_FOLDER / "ai"
REPORT_TEMPLATE_FOLDER = REPORT_FOLDER / "templates"

DIRECTORIES = [
    UPLOAD_FOLDER,
    EXPORT_FOLDER,
    STATIC_FOLDER,
    TEMPLATE_FOLDER,
    LOG_FOLDER,
    DATABASE_FOLDER,
    TEMP_FOLDER,
    MODEL_FOLDER,
    PROMPT_FOLDER,
    REPORT_FOLDER,
    CACHE_FOLDER,
    VECTOR_FOLDER,
    BACKUP_FOLDER,
    OCR_CACHE_FOLDER,
    AI_CACHE_FOLDER,
    REPORT_TEMPLATE_FOLDER,
]

for directory in DIRECTORIES:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )

# ==========================================================
# ENVIRONMENT HELPER
# ==========================================================

def get_env(
    key: str,
    default: Any = None,
    required: bool = False,
):
    """
    Safely read environment variable.
    """

    value = os.getenv(key, default)

    if required:

        if value is None:
            raise RuntimeError(
                f"Environment variable '{key}' is missing."
            )

        if str(value).strip() == "":
            raise RuntimeError(
                f"Environment variable '{key}' is empty."
            )

    return value

# ==========================================================
# APPLICATION CONFIGURATION
# ==========================================================

APP_ENV = get_env(
    "APP_ENV",
    "development"
).lower()

DEBUG = (
    get_env(
        "DEBUG",
        "False"
    ).lower() == "true"
)

HOST = get_env(
    "HOST",
    "0.0.0.0"
)

PORT = int(
    get_env(
        "PORT",
        "8000"
    )
)

API_PREFIX = "/api/v1"

API_TITLE = APP_NAME
API_VERSION = APP_VERSION
API_DESCRIPTION = APP_DESCRIPTION

# ==========================================================
# ENVIRONMENT FLAGS
# ==========================================================

IS_DEVELOPMENT = APP_ENV == "development"
IS_TESTING = APP_ENV == "testing"
IS_PRODUCTION = APP_ENV == "production"

# ==========================================================
# SERVER SETTINGS
# ==========================================================

SERVER_NAME = get_env(
    "SERVER_NAME",
    APP_NAME
)

SERVER_TIMEOUT = int(
    get_env(
        "SERVER_TIMEOUT",
        "300"
    )
)

KEEP_ALIVE_TIMEOUT = int(
    get_env(
        "KEEP_ALIVE_TIMEOUT",
        "5"
    )
)

WORKERS = int(
    get_env(
        "WORKERS",
        "1"
    )
)

# ==========================================================
# REQUEST LIMITS
# ==========================================================

MAX_REQUEST_SIZE = 25 * 1024 * 1024

REQUEST_TIMEOUT = int(
    get_env(
        "REQUEST_TIMEOUT",
        "300"
    )
)

# ==========================================================
# CORS
# ==========================================================

ENABLE_CORS = (
    get_env(
        "ENABLE_CORS",
        "True"
    ).lower() == "true"
)

CORS_ALLOW_ORIGINS = [
    origin.strip()
    for origin in get_env(
        "CORS_ALLOW_ORIGINS",
        "*"
    ).split(",")
]

CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

CORS_ALLOW_HEADERS = ["*"]

CORS_ALLOW_CREDENTIALS = True

# ==========================================================
# SWAGGER
# ==========================================================

ENABLE_SWAGGER = (
    get_env(
        "ENABLE_SWAGGER",
        "True"
    ).lower() == "true"
)

ENABLE_REDOC = (
    get_env(
        "ENABLE_REDOC",
        "True"
    ).lower() == "true"
)

ENABLE_OPENAPI = (
    get_env(
        "ENABLE_OPENAPI",
        "True"
    ).lower() == "true"
)

# ==========================================================
# APPLICATION BANNER
# ==========================================================

APP_BANNER = f"""
=========================================================
{APP_NAME}
Version      : {APP_VERSION}
Environment  : {APP_ENV}
Host         : {HOST}
Port         : {PORT}
=========================================================
"""

# ==========================================================
# OCR CONFIGURATION
# ==========================================================

OCR_ENGINE = get_env(
    "OCR_ENGINE",
    "paddleocr"
).lower()

SUPPORTED_OCR_ENGINES = [
    "paddleocr",
    "tesseract",
]

if OCR_ENGINE not in SUPPORTED_OCR_ENGINES:
    raise RuntimeError(
        f"Unsupported OCR Engine : {OCR_ENGINE}"
    )

# ==========================================================
# OCR LANGUAGE
# ==========================================================

OCR_LANG = get_env(
    "OCR_LANG",
    "en"
)

OCR_SECONDARY_LANG = get_env(
    "OCR_SECONDARY_LANG",
    ""
)

# ==========================================================
# OCR CONFIDENCE
# ==========================================================

OCR_CONFIDENCE = float(
    get_env(
        "OCR_CONFIDENCE",
        "0.60"
    )
)

OCR_MIN_TEXT_LENGTH = int(
    get_env(
        "OCR_MIN_TEXT_LENGTH",
        "2"
    )
)

OCR_PARAGRAPH_THRESHOLD = float(
    get_env(
        "OCR_PARAGRAPH_THRESHOLD",
        "0.5"
    )
)

# ==========================================================
# OCR ENGINE COMPATIBILITY
# ==========================================================

OCR_LANGUAGE = OCR_LANG

OCR_USE_GPU = (
    get_env(
        "OCR_USE_GPU",
        "false"
    )
    .strip()
    .lower()
    in {
        "1",
        "true",
        "yes",
        "on",
    }
)

OCR_CONFIDENCE_THRESHOLD = OCR_CONFIDENCE

# ==========================================================
# IMAGE QUALITY
# ==========================================================

OCR_DPI = int(
    get_env(
        "OCR_DPI",
        "300"
    )
)

OCR_MIN_DPI = int(
    get_env(
        "OCR_MIN_DPI",
        "200"
    )
)

OCR_MAX_DPI = int(
    get_env(
        "OCR_MAX_DPI",
        "600"
    )
)

# ==========================================================
# OCR PERFORMANCE
# ==========================================================

OCR_BATCH_SIZE = int(
    get_env(
        "OCR_BATCH_SIZE",
        "8"
    )
)

OCR_NUM_THREADS = int(
    get_env(
        "OCR_NUM_THREADS",
        "4"
    )
)

OCR_TIMEOUT = int(
    get_env(
        "OCR_TIMEOUT",
        "300"
    )
)

# ==========================================================
# IMAGE PREPROCESSING
# ==========================================================

ENABLE_PREPROCESSING = (
    get_env(
        "ENABLE_PREPROCESSING",
        "True"
    ).lower() == "true"
)

ENABLE_DESKEW = (
    get_env(
        "ENABLE_DESKEW",
        "True"
    ).lower() == "true"
)

ENABLE_DENOISE = (
    get_env(
        "ENABLE_DENOISE",
        "True"
    ).lower() == "true"
)

ENABLE_SHARPEN = (
    get_env(
        "ENABLE_SHARPEN",
        "True"
    ).lower() == "true"
)

ENABLE_CONTRAST = (
    get_env(
        "ENABLE_CONTRAST",
        "True"
    ).lower() == "true"
)

ENABLE_BINARIZATION = (
    get_env(
        "ENABLE_BINARIZATION",
        "True"
    ).lower() == "true"
)

ENABLE_AUTO_ROTATE = (
    get_env(
        "ENABLE_AUTO_ROTATE",
        "True"
    ).lower() == "true"
)

ENABLE_BORDER_REMOVAL = (
    get_env(
        "ENABLE_BORDER_REMOVAL",
        "True"
    ).lower() == "true"
)

ENABLE_SHADOW_REMOVAL = (
    get_env(
        "ENABLE_SHADOW_REMOVAL",
        "True"
    ).lower() == "true"
)

# ==========================================================
# IMAGE SIZE LIMITS
# ==========================================================

IMAGE_MAX_WIDTH = int(
    get_env(
        "IMAGE_MAX_WIDTH",
        "3500"
    )
)

IMAGE_MAX_HEIGHT = int(
    get_env(
        "IMAGE_MAX_HEIGHT",
        "3500"
    )
)

IMAGE_MIN_WIDTH = int(
    get_env(
        "IMAGE_MIN_WIDTH",
        "500"
    )
)

IMAGE_MIN_HEIGHT = int(
    get_env(
        "IMAGE_MIN_HEIGHT",
        "500"
    )
)

# Compatibility name used by ocr_engine.py
MAX_IMAGE_SIZE = int(
    get_env(
        "MAX_IMAGE_SIZE",
        "4096"
    )
)

# ==========================================================
# TESSERACT
# ==========================================================

TESSERACT_CMD = get_env(
    "TESSERACT_CMD",
    ""
)

TESSERACT_PATH = TESSERACT_CMD

ENABLE_TESSERACT_FALLBACK = (
    get_env(
        "ENABLE_TESSERACT_FALLBACK",
        "True"
    ).lower() == "true"
)

# ==========================================================
# PADDLEOCR
# ==========================================================

PADDLE_USE_GPU = (
    get_env(
        "PADDLE_USE_GPU",
        "False"
    ).lower() == "true"
)

PADDLE_USE_ANGLE_CLS = (
    get_env(
        "PADDLE_USE_ANGLE_CLS",
        "True"
    ).lower() == "true"
)

PADDLE_DETECT_ORIENTATION = (
    get_env(
        "PADDLE_DETECT_ORIENTATION",
        "True"
    ).lower() == "true"
)
# ==========================================================
# PADDLEOCR PROCESSING OPTIONS
# ==========================================================

OCR_USE_DOC_ORIENTATION_CLASSIFY = (
    get_env(
        "OCR_USE_DOC_ORIENTATION_CLASSIFY",
        "False",
    ).strip().lower() == "true"
)

OCR_USE_DOC_UNWARPING = (
    get_env(
        "OCR_USE_DOC_UNWARPING",
        "False",
    ).strip().lower() == "true"
)

OCR_USE_TEXTLINE_ORIENTATION = (
    get_env(
        "OCR_USE_TEXTLINE_ORIENTATION",
        "False",
    ).strip().lower() == "true"
)

# ==========================================================
# OCR CACHE
# ==========================================================

ENABLE_OCR_CACHE = (
    get_env(
        "ENABLE_OCR_CACHE",
        "True"
    ).lower() == "true"
)

OCR_CACHE_EXPIRE = int(
    get_env(
        "OCR_CACHE_EXPIRE",
        "3600"
    )
)

# ==========================================================
# OCR INFORMATION
# ==========================================================

OCR_INFO = {
    "engine": OCR_ENGINE,
    "language": OCR_LANG,
    "dpi": OCR_DPI,
    "confidence": OCR_CONFIDENCE,
    "batch_size": OCR_BATCH_SIZE,
    "gpu": PADDLE_USE_GPU,
    "preprocessing": ENABLE_PREPROCESSING,
    "tesseract_fallback": ENABLE_TESSERACT_FALLBACK,
}

# ==========================================================
# DATABASE CONFIGURATION
# ==========================================================

DATABASE_TYPE = get_env(
    "DATABASE_TYPE",
    "mysql"
).lower()

SUPPORTED_DATABASES = [
    "mysql",
    "sqlite",
]

if DATABASE_TYPE not in SUPPORTED_DATABASES:
    raise RuntimeError(
        f"Unsupported database type: {DATABASE_TYPE}"
    )

# ==========================================================
# MYSQL SETTINGS
# ==========================================================

DB_HOST = get_env(
    "DB_HOST",
    "localhost"
)

DB_PORT = int(
    get_env(
        "DB_PORT",
        "3306"
    )
)

DB_NAME = get_env(
    "DB_NAME",
    "ai_document_extractor"
)

DB_USER = get_env(
    "DB_USER",
    "root"
)

DB_PASSWORD = get_env(
    "DB_PASSWORD",
    ""
)

DB_CHARSET = get_env(
    "DB_CHARSET",
    "utf8mb4"
)

# ==========================================================
# SQLITE SETTINGS
# ==========================================================

SQLITE_DATABASE = DATABASE_FOLDER / get_env(
    "SQLITE_DATABASE",
    "invoice.db"
)

# ==========================================================
# SQLALCHEMY DATABASE URL
# ==========================================================

if DATABASE_TYPE == "mysql":

    encoded_user = quote_plus(
        str(DB_USER)
    )

    encoded_password = quote_plus(
        str(DB_PASSWORD)
    )

    encoded_host = quote_plus(
        str(DB_HOST)
    )

    encoded_database = quote_plus(
        str(DB_NAME)
    )

    DATABASE_URL = (
        f"mysql+pymysql://"
        f"{encoded_user}:"
        f"{encoded_password}"
        f"@{encoded_host}:{DB_PORT}"
        f"/{encoded_database}"
        f"?charset={DB_CHARSET}"
    )

else:

    DATABASE_URL = (
        f"sqlite:///{SQLITE_DATABASE}"
    )

# ==========================================================
# CONNECTION POOL
# ==========================================================

DB_POOL_SIZE = int(
    get_env(
        "DB_POOL_SIZE",
        "10"
    )
)

DB_MAX_OVERFLOW = int(
    get_env(
        "DB_MAX_OVERFLOW",
        "20"
    )
)

DB_POOL_TIMEOUT = int(
    get_env(
        "DB_POOL_TIMEOUT",
        "30"
    )
)

DB_POOL_RECYCLE = int(
    get_env(
        "DB_POOL_RECYCLE",
        "1800"
    )
)

DB_POOL_PRE_PING = (
    get_env(
        "DB_POOL_PRE_PING",
        "True"
    ).lower() == "true"
)

DATABASE_ECHO = (
    get_env(
        "DATABASE_ECHO",
        "False"
    ).lower() == "true"
)

DATABASE_AUTOCOMMIT = False
DATABASE_AUTOFLUSH = False
DATABASE_EXPIRE_ON_COMMIT = False

DATABASE_CONNECT_TIMEOUT = int(
    get_env(
        "DATABASE_CONNECT_TIMEOUT",
        "30"
    )
)

# ==========================================================
# DATABASE RETRY
# ==========================================================

DATABASE_MAX_RETRIES = int(
    get_env(
        "DATABASE_MAX_RETRIES",
        "3"
    )
)

DATABASE_RETRY_DELAY = int(
    get_env(
        "DATABASE_RETRY_DELAY",
        "2"
    )
)

# ==========================================================
# DATABASE BACKUP
# ==========================================================

ENABLE_DATABASE_BACKUP = (
    get_env(
        "ENABLE_DATABASE_BACKUP",
        "False"
    ).lower() == "true"
)

BACKUP_RETENTION_DAYS = int(
    get_env(
        "BACKUP_RETENTION_DAYS",
        "7"
    )
)

# ==========================================================
# DATABASE HEALTH
# ==========================================================

DATABASE_HEALTH_CHECK_INTERVAL = int(
    get_env(
        "DATABASE_HEALTH_CHECK_INTERVAL",
        "60"
    )
)

DATABASE_HEALTH_TIMEOUT = int(
    get_env(
        "DATABASE_HEALTH_TIMEOUT",
        "10"
    )
)

# ==========================================================
# DATABASE INFORMATION
# ==========================================================

DATABASE_INFO = {
    "database_type": DATABASE_TYPE,
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_NAME,
    "charset": DB_CHARSET,
    "pool_size": DB_POOL_SIZE,
    "max_overflow": DB_MAX_OVERFLOW,
    "pool_timeout": DB_POOL_TIMEOUT,
    "pool_recycle": DB_POOL_RECYCLE,
    "pool_pre_ping": DB_POOL_PRE_PING,
}

# ==========================================================
# FILE UPLOAD CONFIGURATION
# ==========================================================

MAX_UPLOAD_SIZE = int(
    get_env(
        "MAX_UPLOAD_SIZE",
        str(25 * 1024 * 1024)
    )
)

MAX_FILES_PER_REQUEST = int(
    get_env(
        "MAX_FILES_PER_REQUEST",
        "10"
    )
)

UPLOAD_TEMP_FOLDER = TEMP_FOLDER / "uploads"

UPLOAD_TEMP_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# ==========================================================
# ALLOWED FILES
# ==========================================================

ALLOWED_EXTENSIONS = {
    ".pdf",
    ".png",
    ".jpg",
    ".jpeg",
    ".tif",
    ".tiff",
    ".bmp",
    ".webp",
}

SUPPORTED_MIME_TYPES = {
    "application/pdf",
    "image/png",
    "image/jpeg",
    "image/tiff",
    "image/webp",
    "image/bmp",
}

# ==========================================================
# PDF SETTINGS
# ==========================================================

PDF_RENDER_DPI = int(
    get_env(
        "PDF_RENDER_DPI",
        "300"
    )
)

PDF_MAX_PAGES = int(
    get_env(
        "PDF_MAX_PAGES",
        "50"
    )
)

PDF_PASSWORD_SUPPORTED = (
    get_env(
        "PDF_PASSWORD_SUPPORTED",
        "False"
    ).lower() == "true"
)

# ==========================================================
# IMAGE SETTINGS
# ==========================================================

IMAGE_FORMAT = get_env(
    "IMAGE_FORMAT",
    "PNG"
)

IMAGE_QUALITY = int(
    get_env(
        "IMAGE_QUALITY",
        "95"
    )
)

IMAGE_COLOR_MODE = get_env(
    "IMAGE_COLOR_MODE",
    "RGB"
)

# ==========================================================
# DUPLICATE DETECTION
# ==========================================================

ENABLE_DUPLICATE_CHECK = (
    get_env(
        "ENABLE_DUPLICATE_CHECK",
        "True"
    ).lower() == "true"
)

HASH_ALGORITHM = get_env(
    "HASH_ALGORITHM",
    "sha256"
)

# ==========================================================
# EXPORT SETTINGS
# ==========================================================

DEFAULT_EXPORT_FORMAT = get_env(
    "DEFAULT_EXPORT_FORMAT",
    "json"
)

SUPPORTED_EXPORT_FORMATS = [
    "json",
    "csv",
    "xlsx",
    "xml",
    "pdf",
]

EXPORT_COMPRESS = (
    get_env(
        "EXPORT_COMPRESS",
        "False"
    ).lower() == "true"
)
# ==========================================================
# EXCEL EXPORT
# ==========================================================
EXCEL_FILENAME=get_env(
    "EXCEL_FILENAME",
    "invoices.xlsx",
).strip()

if not EXCEL_FILENAME:
    EXCEL_FILENAME = "invoices.xlsx"
# ==========================================================
# AUTO CLEANUP
# ==========================================================

AUTO_DELETE_TEMP_FILES = (
    get_env(
        "AUTO_DELETE_TEMP_FILES",
        "True"
    ).lower() == "true"
)

TEMP_FILE_RETENTION_HOURS = int(
    get_env(
        "TEMP_FILE_RETENTION_HOURS",
        "24"
    )
)

# ==========================================================
# STORAGE
# ==========================================================

SAVE_ORIGINAL_DOCUMENT = (
    get_env(
        "SAVE_ORIGINAL_DOCUMENT",
        "True"
    ).lower() == "true"
)

SAVE_RENDERED_IMAGES = (
    get_env(
        "SAVE_RENDERED_IMAGES",
        "False"
    ).lower() == "true"
)

SAVE_OCR_TEXT = (
    get_env(
        "SAVE_OCR_TEXT",
        "True"
    ).lower() == "true"
)

SAVE_AI_RESPONSE = (
    get_env(
        "SAVE_AI_RESPONSE",
        "True"
    ).lower() == "true"
)

# ==========================================================
# EXPORT INFO
# ==========================================================

EXPORT_INFO = {
    "default_format": DEFAULT_EXPORT_FORMAT,
    "formats": SUPPORTED_EXPORT_FORMATS,
    "compression": EXPORT_COMPRESS,
    "max_upload_size": MAX_UPLOAD_SIZE,
}

# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================

LOG_LEVEL = get_env(
    "LOG_LEVEL",
    "INFO"
).upper()

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

LOG_FILE = LOG_FOLDER / "application.log"
LOG_ERROR_FILE = LOG_FOLDER / "error.log"

LOG_MAX_SIZE = int(
    get_env(
        "LOG_MAX_SIZE",
        str(20 * 1024 * 1024)
    )
)

LOG_DATE_FORMAT = get_env(
    "LOG_DATE_FORMAT",
    "%Y-%m-%d %H:%M:%S"
).strip()

LOG_ROTATION_SIZE = LOG_MAX_SIZE

LOG_BACKUP_COUNT = int(
    get_env(
        "LOG_BACKUP_COUNT",
        "10"
    )
)

ENABLE_CONSOLE_LOG = (
    get_env(
        "ENABLE_CONSOLE_LOG",
        "True"
    ).strip().lower() == "true"
)

ENABLE_FILE_LOG = (
    get_env(
        "ENABLE_FILE_LOG",
        "True"
    ).strip().lower() == "true"
)

# ==========================================================
# SECURITY
# ==========================================================

SECRET_KEY = get_env(
    "SECRET_KEY",
    required=True
)

JWT_ALGORITHM = get_env(
    "JWT_ALGORITHM",
    "HS256"
)

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    get_env(
        "ACCESS_TOKEN_EXPIRE_MINUTES",
        "60"
    )
)

REFRESH_TOKEN_EXPIRE_DAYS = int(
    get_env(
        "REFRESH_TOKEN_EXPIRE_DAYS",
        "7"
    )
)

PASSWORD_HASH_SCHEME = "bcrypt"

ENABLE_AUTH = (
    get_env(
        "ENABLE_AUTH",
        "True"
    ).lower() == "true"
)
# ==========================================================
# GOOGLE AUTHENTICATION
# ==========================================================

GOOGLE_CLIENT_ID = get_env(
    "GOOGLE_CLIENT_ID",
    "",
)

GOOGLE_CLIENT_SECRET = get_env(
    "GOOGLE_CLIENT_SECRET",
    "",
)

GOOGLE_REDIRECT_URI = get_env(
    "GOOGLE_REDIRECT_URI",
    "http://localhost:8000/api/auth/google/callback",
)
# ==========================================================
# API KEYS
# ==========================================================

OPENAI_API_KEY = get_env(
    "OPENAI_API_KEY",
    ""
)

GEMINI_API_KEY = get_env(
    "GEMINI_API_KEY",
    ""
)

DEEPSEEK_API_KEY = get_env(
    "DEEPSEEK_API_KEY",
    ""
)

# ==========================================================
# AI MODEL CONFIGURATION
# ==========================================================

AI_PROVIDER = get_env(
    "AI_PROVIDER",
    "deepseek"
).strip().lower()

MODEL_NAME = get_env(
    "MODEL_NAME",
    "deepseek-chat"
).strip()

MODEL_PATH = MODEL_FOLDER / get_env(
    "MODEL_PATH",
    MODEL_NAME,
)

MAX_NEW_TOKENS = int(
    get_env(
        "MAX_NEW_TOKENS",
        "1024"
    )
)

TEMPERATURE = float(
    get_env(
        "TEMPERATURE",
        "0.1"
    )
)

# ==========================================================
# AI ENGINE RUNTIME CONFIGURATION
# ==========================================================

AI_SERVICE_NAME = get_env(
    "AI_SERVICE_NAME",
    "AI Engine",
)

AI_SERVICE_VERSION = get_env(
    "AI_SERVICE_VERSION",
    "5.0.0",
)

AI_LOG_SEPARATOR_WIDTH = int(
    get_env(
        "AI_LOG_SEPARATOR_WIDTH",
        "70",
    )
)

DEEPSEEK_BASE_URL = get_env(
    "DEEPSEEK_BASE_URL",
    "https://api.deepseek.com",
)

OPENAI_BASE_URL = get_env(
    "OPENAI_BASE_URL",
    "https://api.openai.com/v1",
)

AI_MAX_INPUT_CHARS = int(
    get_env(
        "AI_MAX_INPUT_CHARS",
        "20000",
    )
)

AI_MAX_JSON_SIZE = int(
    get_env(
        "AI_MAX_JSON_SIZE",
        "50000",
    )
)

AI_MAX_RETRIES = int(
    get_env(
        "AI_MAX_RETRIES",
        "3",
    )
)

AI_MIN_RESPONSE_LENGTH = int(
    get_env(
        "AI_MIN_RESPONSE_LENGTH",
        "10",
    )
)

AI_MAX_FIELD_LENGTH = int(
    get_env(
        "AI_MAX_FIELD_LENGTH",
        "500",
    )
)

AI_CONFIDENCE_THRESHOLD = float(
    get_env(
        "AI_CONFIDENCE_THRESHOLD",
        "0.80",
    )
)

HUMAN_REVIEW_THRESHOLD = float(
    get_env(
        "HUMAN_REVIEW_THRESHOLD",
        "0.60",
    )
)

AI_REQUIRED_FIELD_WEIGHT = float(
    get_env(
        "AI_REQUIRED_FIELD_WEIGHT",
        "0.70",
    )
)

AI_OPTIONAL_FIELD_WEIGHT = float(
    get_env(
        "AI_OPTIONAL_FIELD_WEIGHT",
        "0.30",
    )
)

AI_RETRY_SLEEP_CAP = float(
    get_env(
        "AI_RETRY_SLEEP_CAP",
        "2",
    )
)

AI_FIELD_CONFIDENCE_RULES = {
    "empty": 0.0,
    "vendor_name": {
        "min_length": int(get_env("AI_VENDOR_MIN_LENGTH", "2")),
        "valid": float(get_env("AI_VENDOR_VALID_SCORE", "1.0")),
        "invalid": float(get_env("AI_VENDOR_INVALID_SCORE", "0.30")),
    },
    "invoice_number": {
        "min_length": int(get_env("AI_INVOICE_NUMBER_MIN_LENGTH", "2")),
        "valid": float(get_env("AI_INVOICE_NUMBER_VALID_SCORE", "1.0")),
        "invalid": float(get_env("AI_INVOICE_NUMBER_INVALID_SCORE", "0.40")),
    },
    "gst_number": {
        "partial_min_length": int(get_env("AI_GST_PARTIAL_MIN_LENGTH", "10")),
        "valid": float(get_env("AI_GST_VALID_SCORE", "1.0")),
        "partial": float(get_env("AI_GST_PARTIAL_SCORE", "0.65")),
        "invalid": float(get_env("AI_GST_INVALID_SCORE", "0.30")),
    },
    "invoice_date": {
        "partial_min_length": int(get_env("AI_DATE_PARTIAL_MIN_LENGTH", "6")),
        "valid": float(get_env("AI_DATE_VALID_SCORE", "1.0")),
        "partial": float(get_env("AI_DATE_PARTIAL_SCORE", "0.65")),
        "invalid": float(get_env("AI_DATE_INVALID_SCORE", "0.30")),
    },
    "monetary": {
        "valid": float(get_env("AI_MONETARY_VALID_SCORE", "1.0")),
        "invalid": float(get_env("AI_MONETARY_INVALID_SCORE", "0.30")),
    },
    "monetary_fields": (
        "subtotal",
        "tax",
        "grand_total",
    ),
    "currency": {
        "max_length": int(get_env("AI_CURRENCY_MAX_LENGTH", "10")),
        "valid": float(get_env("AI_CURRENCY_VALID_SCORE", "1.0")),
        "invalid": float(get_env("AI_CURRENCY_INVALID_SCORE", "0.50")),
    },
    "payment_method": {
        "min_length": int(get_env("AI_PAYMENT_METHOD_MIN_LENGTH", "2")),
        "valid": float(get_env("AI_PAYMENT_METHOD_VALID_SCORE", "1.0")),
        "invalid": float(get_env("AI_PAYMENT_METHOD_INVALID_SCORE", "0.40")),
    },
    "default": float(get_env("AI_DEFAULT_FIELD_SCORE", "0.75")),
}

SUPPORTED_AI_PROVIDERS = {
    "deepseek",
    "openai",
    "gemini",
    "ollama",
}

if AI_PROVIDER not in SUPPORTED_AI_PROVIDERS:
    raise RuntimeError(
        f"Unsupported AI provider: {AI_PROVIDER}. "
        f"Supported providers: "
        f"{', '.join(sorted(SUPPORTED_AI_PROVIDERS))}"
    )

# ==========================================================
# CACHE
# ==========================================================

ENABLE_CACHE = (
    get_env(
        "ENABLE_CACHE",
        "True"
    ).lower() == "true"
)

CACHE_TTL = int(
    get_env(
        "CACHE_TTL",
        "3600"
    )
)

CACHE_MAX_ITEMS = int(
    get_env(
        "CACHE_MAX_ITEMS",
        "1000"
    )
)

# ==========================================================
# RATE LIMITING
# ==========================================================

ENABLE_RATE_LIMIT = (
    get_env(
        "ENABLE_RATE_LIMIT",
        "True"
    ).lower() == "true"
)

RATE_LIMIT_REQUESTS = int(
    get_env(
        "RATE_LIMIT_REQUESTS",
        "100"
    )
)

RATE_LIMIT_WINDOW = int(
    get_env(
        "RATE_LIMIT_WINDOW",
        "60"
    )
)

# ==========================================================
# PERFORMANCE
# ==========================================================

MAX_WORKERS = int(
    get_env(
        "MAX_WORKERS",
        "4"
    )
)

ENABLE_MULTIPROCESSING = (
    get_env(
        "ENABLE_MULTIPROCESSING",
        "True"
    ).lower() == "true"
)

ENABLE_MULTITHREADING = (
    get_env(
        "ENABLE_MULTITHREADING",
        "True"
    ).lower() == "true"
)

# ==========================================================
# MONITORING
# ==========================================================

ENABLE_HEALTH_CHECK = (
    get_env(
        "ENABLE_HEALTH_CHECK",
        "True"
    ).lower() == "true"
)

HEALTH_CHECK_INTERVAL = int(
    get_env(
        "HEALTH_CHECK_INTERVAL",
        "60"
    )
)

ENABLE_METRICS = (
    get_env(
        "ENABLE_METRICS",
        "True"
    ).lower() == "true"
)

ENABLE_PROFILING = (
    get_env(
        "ENABLE_PROFILING",
        "False"
    ).lower() == "true"
)

# ==========================================================
# GPU / DEVICE CONFIGURATION
# ==========================================================

CUDA_AVAILABLE = False

try:
    CUDA_AVAILABLE = bool(
        torch.cuda.is_available()
    )
except Exception:
    CUDA_AVAILABLE = False

MPS_AVAILABLE = False

try:
    MPS_AVAILABLE = bool(
        hasattr(
            torch.backends,
            "mps"
        )
        and torch.backends.mps.is_available()
        and torch.backends.mps.is_built()
    )
except Exception:
    MPS_AVAILABLE = False

# ==========================================================
# DEVICE SELECTION
# ==========================================================

if CUDA_AVAILABLE:
    DEVICE = "cuda"
elif MPS_AVAILABLE:
    DEVICE = "mps"
else:
    DEVICE = "cpu"

ENABLE_GPU = DEVICE != "cpu"
GPU_DEVICE = DEVICE

DEVICE_INFO = {
    "device": DEVICE,
    "cuda_available": CUDA_AVAILABLE,
    "mps_available": MPS_AVAILABLE,
    "gpu_enabled": ENABLE_GPU,
}

# ==========================================================
# APPLICATION INFORMATION
# ==========================================================

SYSTEM_INFO = {
    "application": APP_NAME,
    "version": APP_VERSION,
    "environment": APP_ENV,
    "device": DEVICE,
    "gpu_enabled": ENABLE_GPU,
    "workers": MAX_WORKERS,
    "debug": DEBUG,
}

# ==========================================================
# STARTUP VALIDATION
# ==========================================================

REQUIRED_DIRECTORIES = [
    UPLOAD_FOLDER,
    EXPORT_FOLDER,
    LOG_FOLDER,
    TEMP_FOLDER,
    MODEL_FOLDER,
]

for directory in REQUIRED_DIRECTORIES:
    directory.mkdir(
        parents=True,
        exist_ok=True
    )

print(APP_BANNER)

# ==========================================================
# DOCUMENT TYPES
# ==========================================================

SUPPORTED_DOCUMENT_TYPES = [
    "invoice",
    "tax_invoice",
    "gst_invoice",
    "purchase_invoice",
    "credit_note",
    "debit_note",
]

# ==========================================================
# CURRENCIES
# ==========================================================

SUPPORTED_CURRENCIES = [
    "INR",
    "USD",
    "EUR",
    "GBP",
    "AED",
]

DEFAULT_CURRENCY = get_env(
    "DEFAULT_CURRENCY",
    "INR"
)

# ==========================================================
# DATE FORMAT
# ==========================================================

SUPPORTED_DATE_FORMATS = [
    "%d/%m/%Y",
    "%d-%m-%Y",
    "%Y-%m-%d",
    "%d.%m.%Y",
    "%d %b %Y",
    "%d %B %Y",
]

# ==========================================================
# GST
# ==========================================================

GST_NUMBER_LENGTH = 15
GST_STATE_CODE_LENGTH = 2
GST_PAN_LENGTH = 10

GST_REGEX = (
    r"^[0-9]{2}"
    r"[A-Z]{5}"
    r"[0-9]{4}"
    r"[A-Z]{1}"
    r"[1-9A-Z]{1}"
    r"Z"
    r"[0-9A-Z]{1}$"
)

# ==========================================================
# CONFIDENCE
# ==========================================================

FIELD_CONFIDENCE_THRESHOLD = float(
    get_env(
        "FIELD_CONFIDENCE_THRESHOLD",
        "0.80"
    )
)

DOCUMENT_CONFIDENCE_THRESHOLD = float(
    get_env(
        "DOCUMENT_CONFIDENCE_THRESHOLD",
        "0.85"
    )
)

AUTO_APPROVE_THRESHOLD = float(
    get_env(
        "AUTO_APPROVE_THRESHOLD",
        "0.95"
    )
)

# ==========================================================
# VALIDATION
# ==========================================================

ENABLE_RULE_VALIDATION = (
    get_env(
        "ENABLE_RULE_VALIDATION",
        "True"
    ).lower() == "true"
)

ENABLE_AI_VALIDATION = (
    get_env(
        "ENABLE_AI_VALIDATION",
        "True"
    ).lower() == "true"
)

ENABLE_TOTAL_VALIDATION = (
    get_env(
        "ENABLE_TOTAL_VALIDATION",
        "True"
    ).lower() == "true"
)

ENABLE_GST_VALIDATION = (
    get_env(
        "ENABLE_GST_VALIDATION",
        "True"
    ).lower() == "true"
)

ENABLE_DATE_VALIDATION = (
    get_env(
        "ENABLE_DATE_VALIDATION",
        "True"
    ).lower() == "true"
)

ENABLE_VENDOR_VALIDATION = (
    get_env(
        "ENABLE_VENDOR_VALIDATION",
        "True"
    ).lower() == "true"
)

# ==========================================================
# REQUIRED FIELDS
# ==========================================================

REQUIRED_FIELDS = [
    "vendor_name",
    "invoice_number",
    "invoice_date",
    "grand_total",
]


OPTIONAL_FIELDS = [
    "gst_number",
    "subtotal",
    "tax",
    "payment_method",
    "currency",
]
# ==========================================================
# CONFIDENCE ENGINE CONFIGURATION
# ==========================================================

CONFIDENCE_WEIGHTS = {
    "ocr": float(
        get_env("CONFIDENCE_WEIGHT_OCR", "0.30")
    ),
    "rule": float(
        get_env("CONFIDENCE_WEIGHT_RULE", "0.30")
    ),
    "validation": float(
        get_env("CONFIDENCE_WEIGHT_VALIDATION", "0.25")
    ),
    "ai": float(
        get_env("CONFIDENCE_WEIGHT_AI", "0.15")
    ),
}

INVOICE_FIELD_WEIGHTS = {
    "invoice_number": float(
        get_env("FIELD_WEIGHT_INVOICE_NUMBER", "0.15")
    ),
    "vendor_name": float(
        get_env("FIELD_WEIGHT_VENDOR_NAME", "0.10")
    ),
    "invoice_date": float(
        get_env("FIELD_WEIGHT_INVOICE_DATE", "0.10")
    ),
    "gst_number": float(
        get_env("FIELD_WEIGHT_GST_NUMBER", "0.15")
    ),
    "pan_number": float(
        get_env("FIELD_WEIGHT_PAN_NUMBER", "0.05")
    ),
    "currency": float(
        get_env("FIELD_WEIGHT_CURRENCY", "0.05")
    ),
    "subtotal": float(
        get_env("FIELD_WEIGHT_SUBTOTAL", "0.10")
    ),
    "cgst": float(
        get_env("FIELD_WEIGHT_CGST", "0.05")
    ),
    "sgst": float(
        get_env("FIELD_WEIGHT_SGST", "0.05")
    ),
    "igst": float(
        get_env("FIELD_WEIGHT_IGST", "0.05")
    ),
    "grand_total": float(
        get_env("FIELD_WEIGHT_GRAND_TOTAL", "0.15")
    ),
}

DEFAULT_FIELD_WEIGHT = float(
    get_env("DEFAULT_FIELD_WEIGHT", "0.05")
)

CONFIDENCE_EXCELLENT_THRESHOLD = float(
    get_env("CONFIDENCE_EXCELLENT_THRESHOLD", "0.95")
)

CONFIDENCE_HIGH_THRESHOLD = float(
    get_env("CONFIDENCE_HIGH_THRESHOLD", "0.90")
)

CONFIDENCE_MEDIUM_THRESHOLD = float(
    get_env("CONFIDENCE_MEDIUM_THRESHOLD", "0.75")
)

OVERALL_EXCELLENT_THRESHOLD = float(
    get_env("OVERALL_EXCELLENT_THRESHOLD", "0.97")
)

OVERALL_HIGH_THRESHOLD = float(
    get_env("OVERALL_HIGH_THRESHOLD", "0.92")
)

REVIEW_THRESHOLD = float(
    get_env("REVIEW_THRESHOLD", "0.80")
)

REVIEW_FIELD_THRESHOLD = float(
    get_env("REVIEW_FIELD_THRESHOLD", "0.90")
)

HIGH_PRIORITY_THRESHOLD = float(
    get_env("HIGH_PRIORITY_THRESHOLD", "0.75")
)

CRITICAL_FIELDS = {
    field.strip()
    for field in get_env(
        "CRITICAL_FIELDS",
        "invoice_number,vendor_name,invoice_date,grand_total",
    ).split(",")
    if field.strip()
}# ==========================================================
# AI ENGINE CONFIGURATION VALIDATION
# ==========================================================

if AI_MAX_INPUT_CHARS <= 0:
    raise RuntimeError("AI_MAX_INPUT_CHARS must be greater than zero.")

if AI_MAX_JSON_SIZE <= 0:
    raise RuntimeError("AI_MAX_JSON_SIZE must be greater than zero.")

if AI_MAX_RETRIES < 1:
    raise RuntimeError("AI_MAX_RETRIES must be at least 1.")

if AI_MIN_RESPONSE_LENGTH < 0:
    raise RuntimeError("AI_MIN_RESPONSE_LENGTH cannot be negative.")

if AI_MAX_FIELD_LENGTH <= 0:
    raise RuntimeError("AI_MAX_FIELD_LENGTH must be greater than zero.")

if not 0.0 <= AI_CONFIDENCE_THRESHOLD <= 1.0:
    raise RuntimeError("AI_CONFIDENCE_THRESHOLD must be between 0 and 1.")

if not 0.0 <= HUMAN_REVIEW_THRESHOLD <= 1.0:
    raise RuntimeError("HUMAN_REVIEW_THRESHOLD must be between 0 and 1.")

if abs((AI_REQUIRED_FIELD_WEIGHT + AI_OPTIONAL_FIELD_WEIGHT) - 1.0) > 0.0001:
    raise RuntimeError("AI_REQUIRED_FIELD_WEIGHT + AI_OPTIONAL_FIELD_WEIGHT must equal 1.0.")

# ==========================================================
# APPLICATION SUMMARY
# ==========================================================

CONFIG_SUMMARY = {
    "application": APP_NAME,
    "version": APP_VERSION,
    "environment": APP_ENV,
    "database": DATABASE_TYPE,
    "ocr": OCR_ENGINE,
    "ai_provider": AI_PROVIDER,
    "model": MODEL_NAME,
    "device": DEVICE,
    "gpu": ENABLE_GPU,
}

# ==========================================================
# CONFIG VALIDATION
# ==========================================================

if MAX_UPLOAD_SIZE <= 0:
    raise RuntimeError(
        "MAX_UPLOAD_SIZE must be greater than zero."
    )

if OCR_CONFIDENCE < 0 or OCR_CONFIDENCE > 1:
    raise RuntimeError(
        "OCR_CONFIDENCE must be between 0 and 1."
    )

if FIELD_CONFIDENCE_THRESHOLD < 0 or FIELD_CONFIDENCE_THRESHOLD > 1:
    raise RuntimeError(
        "FIELD_CONFIDENCE_THRESHOLD must be between 0 and 1."
    )

if DOCUMENT_CONFIDENCE_THRESHOLD < 0 or DOCUMENT_CONFIDENCE_THRESHOLD > 1:
    raise RuntimeError(
        "DOCUMENT_CONFIDENCE_THRESHOLD must be between 0 and 1."
    )

# ==========================================================
# READY
# ==========================================================

CONFIG_READY = True

print("=" * 60)
print(f"{APP_NAME} Configuration Loaded Successfully")
print(f"Environment : {APP_ENV}")
print(f"Database    : {DATABASE_TYPE}")
print(f"OCR Engine  : {OCR_ENGINE}")
print(f"AI Provider : {AI_PROVIDER}")
print(f"Model       : {MODEL_NAME}")
print(f"Device      : {DEVICE}")
print("=" * 60)
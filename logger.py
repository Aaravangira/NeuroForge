"""
=========================================================
AI Invoice Extractor
Production Logger
=========================================================
"""

# ==========================================================
# STANDARD LIBRARIES
# ==========================================================

import logging
import logging.handlers
from pathlib import Path

# ==========================================================
# PROJECT IMPORTS
# ==========================================================

from config import (
    APP_NAME,
    LOG_FOLDER,
    LOG_LEVEL,
    LOG_FORMAT,
    LOG_DATE_FORMAT,
    LOG_ROTATION_SIZE,
    LOG_BACKUP_COUNT,
    ENABLE_CONSOLE_LOG,
    ENABLE_FILE_LOG,
)

# ==========================================================
# LOG FILES
# ==========================================================

LOG_FILE = LOG_FOLDER / "application.log"

ERROR_LOG_FILE = LOG_FOLDER / "error.log"

ACCESS_LOG_FILE = LOG_FOLDER / "access.log"

AI_LOG_FILE = LOG_FOLDER / "ai.log"

OCR_LOG_FILE = LOG_FOLDER / "ocr.log"

DATABASE_LOG_FILE = LOG_FOLDER / "database.log"

# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(APP_NAME)

logger.setLevel(LOG_LEVEL)

logger.propagate = False

# ==========================================================
# REMOVE OLD HANDLERS
# ==========================================================

if logger.hasHandlers():

    logger.handlers.clear()
    # ==========================================================
# FORMATTER
# ==========================================================

formatter = logging.Formatter(

    fmt=LOG_FORMAT,

    datefmt=LOG_DATE_FORMAT,

)

# ==========================================================
# HANDLER FACTORY
# ==========================================================

def create_file_handler(
    log_file,
    level=logging.INFO,
):
    """
    Create rotating file handler.
    """

    handler = logging.handlers.RotatingFileHandler(

        filename=log_file,

        maxBytes=LOG_ROTATION_SIZE,

        backupCount=LOG_BACKUP_COUNT,

        encoding="utf-8",

    )

    handler.setLevel(level)

    handler.setFormatter(formatter)

    return handler


# ==========================================================
# CONSOLE HANDLER
# ==========================================================

console_handler = logging.StreamHandler()

console_handler.setLevel(LOG_LEVEL)

console_handler.setFormatter(formatter)


# ==========================================================
# FILE HANDLERS
# ==========================================================

application_handler = create_file_handler(

    LOG_FILE,

    logging.INFO,

)

error_handler = create_file_handler(

    ERROR_LOG_FILE,

    logging.ERROR,

)

access_handler = create_file_handler(

    ACCESS_LOG_FILE,

    logging.INFO,

)

ai_handler = create_file_handler(

    AI_LOG_FILE,

    logging.INFO,

)

ocr_handler = create_file_handler(

    OCR_LOG_FILE,

    logging.INFO,

)

database_handler = create_file_handler(

    DATABASE_LOG_FILE,

    logging.INFO,

)

# ==========================================================
# ATTACH HANDLERS
# ==========================================================

if ENABLE_CONSOLE_LOG:

    logger.addHandler(
        console_handler
    )

if ENABLE_FILE_LOG:

    logger.addHandler(
        application_handler
    )

    logger.addHandler(
        error_handler
    )

    logger.addHandler(
        access_handler
    )

    logger.addHandler(
        ai_handler
    )

    logger.addHandler(
        ocr_handler
    )

    logger.addHandler(
        database_handler
    )
    # ==========================================================
# STANDARD LIBRARIES
# ==========================================================

import os
import threading
from datetime import datetime

# ==========================================================
# REQUEST CONTEXT
# ==========================================================

class RequestContextFilter(logging.Filter):
    """
    Add extra information to every log record.
    """

    def filter(self, record):

        record.app_name = APP_NAME

        record.process_id = os.getpid()

        record.thread_name = threading.current_thread().name

        record.timestamp = datetime.utcnow().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return True


# ==========================================================
# CUSTOM FORMATTER
# ==========================================================

class ProductionFormatter(logging.Formatter):
    """
    Production log formatter.
    """

    def format(self, record):

        record.level = record.levelname

        record.module_name = record.module

        record.function_name = record.funcName

        record.line_number = record.lineno

        return super().format(record)


# ==========================================================
# PRODUCTION FORMAT
# ==========================================================

PRODUCTION_LOG_FORMAT = (
    "[%(asctime)s] "
    "[%(levelname)s] "
    "[PID:%(process_id)s] "
    "[%(thread_name)s] "
    "[%(module_name)s:%(function_name)s:%(line_number)s] "
    "%(message)s"
)

production_formatter = ProductionFormatter(

    fmt=PRODUCTION_LOG_FORMAT,

    datefmt="%Y-%m-%d %H:%M:%S",

)

# ==========================================================
# APPLY FILTER
# ==========================================================

context_filter = RequestContextFilter()

logger.addFilter(
    context_filter
)

# ==========================================================
# UPDATE ALL HANDLERS
# ==========================================================

for handler in logger.handlers:

    handler.setFormatter(
        production_formatter
    )

    handler.addFilter(
        context_filter
    )
    # ==========================================================
# HELPER LOGGING FUNCTIONS
# ==========================================================

def log_info(message: str):
    """
    Log info message.
    """

    logger.info(message)


def log_warning(message: str):
    """
    Log warning message.
    """

    logger.warning(message)


def log_error(message: str):
    """
    Log error message.
    """

    logger.error(message)


def log_debug(message: str):
    """
    Log debug message.
    """

    logger.debug(message)


def log_critical(message: str):
    """
    Log critical message.
    """

    logger.critical(message)


# ==========================================================
# OCR LOGGING
# ==========================================================

def log_ocr(
    message: str,
    file_name: str = "",
):
    """
    OCR log.
    """

    logger.info(
        f"[OCR] [{file_name}] {message}"
    )


# ==========================================================
# AI LOGGING
# ==========================================================

def log_ai(
    message: str,
    model: str = "",
):
    """
    AI log.
    """

    logger.info(
        f"[AI] [{model}] {message}"
    )


# ==========================================================
# DATABASE LOGGING
# ==========================================================

def log_database(
    message: str,
):
    """
    Database log.
    """

    logger.info(
        f"[DATABASE] {message}"
    )


# ==========================================================
# API LOGGING
# ==========================================================

def log_api(
    method: str,
    endpoint: str,
    status_code: int,
):
    """
    API request log.
    """

    logger.info(
        f"[API] {method} "
        f"{endpoint} "
        f"Status={status_code}"
    )


# ==========================================================
# FILE LOGGING
# ==========================================================

def log_file(
    filename: str,
    action: str,
):
    """
    File operation log.
    """

    logger.info(
        f"[FILE] "
        f"{filename} "
        f"{action}"
    )


# ==========================================================
# SECURITY LOGGING
# ==========================================================

def log_security(
    message: str,
):
    """
    Security log.
    """

    logger.warning(
        f"[SECURITY] {message}"
    )


# ==========================================================
# STARTUP LOGGING
# ==========================================================

def log_startup():
    """
    Application startup.
    """

    logger.info(
        "=" * 60
    )

    logger.info(
        APP_NAME
    )

    logger.info(
        "Application Started Successfully"
    )

    logger.info(
        "=" * 60
    )


# ==========================================================
# SHUTDOWN LOGGING
# ==========================================================

def log_shutdown():
    """
    Application shutdown.
    """

    logger.info(
        "=" * 60
    )

    logger.info(
        "Application Shutdown"
    )

    logger.info(
        "=" * 60
    )
    # ==========================================================
# STANDARD LIBRARIES
# ==========================================================

import functools
import time

# ==========================================================
# PERFORMANCE TIMER DECORATOR
# ==========================================================

def log_execution_time(operation: str = ""):
    """
    Measure execution time of a function.

    Example:
        @log_execution_time("OCR")
        def process():
            ...
    """

    def decorator(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            start_time = time.perf_counter()

            try:

                result = func(*args, **kwargs)

                elapsed = (
                    time.perf_counter() - start_time
                ) * 1000

                logger.info(
                    "[PERFORMANCE] "
                    f"[{operation}] "
                    f"{func.__name__} "
                    f"completed in "
                    f"{elapsed:.2f} ms"
                )

                return result

            except Exception:

                elapsed = (
                    time.perf_counter() - start_time
                ) * 1000

                logger.exception(
                    "[PERFORMANCE] "
                    f"[{operation}] "
                    f"{func.__name__} "
                    f"failed after "
                    f"{elapsed:.2f} ms"
                )

                raise

        return wrapper

    return decorator


# ==========================================================
# SIMPLE TIMER
# ==========================================================

class PerformanceTimer:
    """
    Context manager for measuring execution time.

    Example:

        with PerformanceTimer("OCR"):
            process_invoice()
    """

    def __init__(self, operation):

        self.operation = operation

        self.start = None

    def __enter__(self):

        self.start = time.perf_counter()

        return self

    def __exit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):

        elapsed = (
            time.perf_counter() - self.start
        ) * 1000

        logger.info(
            "[PERFORMANCE] "
            f"[{self.operation}] "
            f"{elapsed:.2f} ms"
        )


# ==========================================================
# PERFORMANCE LOGGER
# ==========================================================

def log_performance(
    operation: str,
    elapsed_ms: float,
):
    """
    Log execution time manually.
    """

    logger.info(
        "[PERFORMANCE] "
        f"[{operation}] "
        f"{elapsed_ms:.2f} ms"
    )


# ==========================================================
# MEMORY LOGGER
# ==========================================================

def log_memory_usage():
    """
    Log current memory usage if psutil is installed.
    """

    try:

        import psutil

        process = psutil.Process()

        memory = (
            process.memory_info().rss
            / (1024 * 1024)
        )

        logger.info(
            "[MEMORY] "
            f"{memory:.2f} MB"
        )

    except ImportError:

        logger.debug(
            "psutil not installed."
        )

    except Exception:

        logger.exception(
            "Unable to determine memory usage."
        )
        # ==========================================================
# STANDARD LIBRARIES
# ==========================================================

import traceback

# ==========================================================
# EXCEPTION LOGGER
# ==========================================================

def log_exception(
    exception: Exception,
    message: str = "",
):
    """
    Log complete exception with traceback.
    """

    logger.exception(
        "[EXCEPTION] "
        f"{message}\n"
        f"{str(exception)}"
    )


# ==========================================================
# OCR ERROR LOGGER
# ==========================================================

def log_ocr_error(
    exception: Exception,
    filename: str = "",
):
    """
    Log OCR related errors.
    """

    logger.exception(
        "[OCR ERROR] "
        f"[{filename}] "
        f"{str(exception)}"
    )


# ==========================================================
# AI ERROR LOGGER
# ==========================================================

def log_ai_error(
    exception: Exception,
    model: str = "",
):
    """
    Log AI inference errors.
    """

    logger.exception(
        "[AI ERROR] "
        f"[{model}] "
        f"{str(exception)}"
    )


# ==========================================================
# DATABASE ERROR LOGGER
# ==========================================================

def log_database_error(
    exception: Exception,
):
    """
    Log database errors.
    """

    logger.exception(
        "[DATABASE ERROR] "
        f"{str(exception)}"
    )


# ==========================================================
# API ERROR LOGGER
# ==========================================================

def log_api_error(
    endpoint: str,
    exception: Exception,
):
    """
    Log API errors.
    """

    logger.exception(
        "[API ERROR] "
        f"[{endpoint}] "
        f"{str(exception)}"
    )


# ==========================================================
# FILE ERROR LOGGER
# ==========================================================

def log_file_error(
    filename: str,
    exception: Exception,
):
    """
    Log file related errors.
    """

    logger.exception(
        "[FILE ERROR] "
        f"[{filename}] "
        f"{str(exception)}"
    )


# ==========================================================
# VALIDATION LOGGER
# ==========================================================

def log_validation_error(
    field: str,
    message: str,
):
    """
    Log validation failures.
    """

    logger.warning(
        "[VALIDATION] "
        f"{field} -> "
        f"{message}"
    )


# ==========================================================
# SECURITY LOGGER
# ==========================================================

def log_security_event(
    event: str,
    ip_address: str = "",
):
    """
    Log security related events.
    """

    logger.warning(
        "[SECURITY] "
        f"IP={ip_address} "
        f"{event}"
    )


# ==========================================================
# OCR CONFIDENCE LOGGER
# ==========================================================

def log_ocr_confidence(
    confidence: float,
):
    """
    Log OCR confidence score.
    """

    logger.info(
        "[OCR CONFIDENCE] "
        f"{confidence:.2%}"
    )


# ==========================================================
# AI CONFIDENCE LOGGER
# ==========================================================

def log_ai_confidence(
    confidence: float,
):
    """
    Log AI confidence score.
    """

    logger.info(
        "[AI CONFIDENCE] "
        f"{confidence:.2%}"
    )


# ==========================================================
# JSON LOGGER
# ==========================================================

def log_json_error(
    exception: Exception,
):
    """
    JSON parsing errors.
    """

    logger.exception(
        "[JSON ERROR] "
        f"{str(exception)}"
    )


# ==========================================================
# MODEL LOGGER
# ==========================================================

def log_model_loaded(
    model_name: str,
):
    """
    Log AI model loading.
    """

    logger.info(
        "[MODEL] "
        f"{model_name} loaded successfully."
    )


# ==========================================================
# OCR LOGGER
# ==========================================================

def log_ocr_loaded(
    engine: str,
):
    """
    Log OCR engine loading.
    """

    logger.info(
        "[OCR ENGINE] "
        f"{engine} initialized successfully."
    )


# ==========================================================
# STARTUP LOGGER
# ==========================================================

def log_application_start():

    logger.info("=" * 70)

    logger.info("Application Started")

    logger.info("=" * 70)


# ==========================================================
# SHUTDOWN LOGGER
# ==========================================================

def log_application_stop():

    logger.info("=" * 70)

    logger.info("Application Shutdown")

    logger.info("=" * 70)
    # ==========================================================
# LOGGER INITIALIZATION
# ==========================================================

def initialize_logger():
    """
    Initialize production logger.
    """

    logger.info("=" * 80)

    logger.info(f"Application : {APP_NAME}")

    logger.info("Logger Initialized Successfully")

    logger.info("=" * 80)

    return logger


# ==========================================================
# LOGGER SHUTDOWN
# ==========================================================

def shutdown_logger():
    """
    Close all logging handlers gracefully.
    """

    logger.info("Logger Shutdown Started")

    handlers = logger.handlers[:]

    for handler in handlers:

        try:

            handler.flush()

            handler.close()

        except Exception:

            pass

        finally:

            logger.removeHandler(handler)


# ==========================================================
# LOGGER STATUS
# ==========================================================

def logger_status():
    """
    Return logger information.
    """

    return {

        "logger_name": logger.name,

        "level": logging.getLevelName(
            logger.level
        ),

        "handlers": len(
            logger.handlers
        ),

        "enabled": not logger.disabled,

    }


# ==========================================================
# LOG SYSTEM INFORMATION
# ==========================================================

def log_system_information():
    """
    Log application information.
    """

    import platform
    import sys

    logger.info("=" * 80)

    logger.info("SYSTEM INFORMATION")

    logger.info(f"Application : {APP_NAME}")

    logger.info(f"Python      : {sys.version}")

    logger.info(f"Platform    : {platform.system()}")

    logger.info(f"Release     : {platform.release()}")

    logger.info(f"Machine     : {platform.machine()}")

    logger.info(f"Processor   : {platform.processor()}")

    logger.info("=" * 80)


# ==========================================================
# STARTUP BANNER
# ==========================================================

def startup_banner():

    banner = f"""

============================================================
                 AI INVOICE EXTRACTOR
============================================================

Application : {APP_NAME}

Status      : READY

Logging     : ENABLED

============================================================

"""

    logger.info(banner)


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "logger",

    "initialize_logger",

    "shutdown_logger",

    "logger_status",

    "startup_banner",

    "log_system_information",

    "log_info",

    "log_debug",

    "log_warning",

    "log_error",

    "log_critical",

    "log_exception",

    "log_ai",

    "log_ai_error",

    "log_ocr",

    "log_ocr_error",

    "log_database",

    "log_database_error",

    "log_api",

    "log_api_error",

    "log_security",

    "log_security_event",

    "log_validation_error",

    "log_json_error",

    "log_performance",

    "log_execution_time",

    "PerformanceTimer",

    "log_memory_usage",

    "log_model_loaded",

    "log_ocr_loaded",

    "log_startup",

    "log_shutdown",

    "log_application_start",

    "log_application_stop",
]

# ==========================================================
# INITIALIZE LOGGER
# ==========================================================

initialize_logger()

startup_banner()

log_system_information()
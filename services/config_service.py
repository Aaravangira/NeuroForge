"""
==========================================================
CONFIGURATION SERVICE
AI Invoice Extractor
Production Version 1.0
==========================================================
"""

from __future__ import annotations

import json
import os
import threading
import time

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

from logger import logger

# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = "Configuration Service"

SERVICE_VERSION = "1.0.0"

# ==========================================================
# CONFIG DIRECTORY
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

CONFIG_DIR = BASE_DIR / "config"

# ==========================================================
# REQUIRED CONFIG FILES
# ==========================================================

CONFIG_FILES = {

    "ai": "ai.json",

    "ocr": "ocr.json",

    "validation": "validation.json",

    "confidence": "confidence.json",

    "invoice": "invoice.json",

    "database": "database.json",

    "business_rules": "business_rules.json",

    "document_types": "document_types.json",

    "logging": "logging.json",

}

# ==========================================================
# METRICS
# ==========================================================

@dataclass
class ConfigMetrics:

    load_count: int = 0

    reload_count: int = 0

    failed_loads: int = 0

    last_loaded: float = 0.0

# ==========================================================
# CONFIG SERVICE
# ==========================================================

class ConfigService:

    """
    Enterprise Configuration Service

    Responsible for

    - Loading configuration
    - Caching configuration
    - Validation
    - Nested lookup
    - Runtime reload
    """

    def __init__(self):

        self._lock = threading.RLock()

        self._configs: Dict[str, Dict[str, Any]] = {}

        self._metrics = ConfigMetrics()

        logger.info(

            "%s %s initialized.",

            SERVICE_NAME,

            SERVICE_VERSION,

        )
            # ======================================================
    # LOAD SINGLE CONFIG
    # ======================================================

    def load_config(
        self,
        name: str,
    ) -> Dict[str, Any]:
        """
        Load one configuration file.
        """

        filename = CONFIG_FILES.get(name)

        if filename is None:

            raise KeyError(

                f"Unknown configuration: {name}"

            )

        filepath = CONFIG_DIR / filename

        if not filepath.exists():

            raise FileNotFoundError(

                f"Configuration file not found: {filepath}"

            )

        with filepath.open(

            "r",

            encoding="utf-8",

        ) as file:

            data = json.load(file)

        return data

    # ======================================================
    # LOAD ALL CONFIGS
    # ======================================================

    def load(self):
        """
        Load every configuration file.
        """

        start = time.perf_counter()

        with self._lock:

            self._configs.clear()

            for name in CONFIG_FILES:

                self._configs[name] = self.load_config(

                    name

                )

            self._metrics.load_count += 1

            self._metrics.last_loaded = time.time()

        elapsed = round(

            time.perf_counter()

            -

            start,

            3,

        )

        logger.info(

            "Loaded %d configuration files in %.3f sec.",

            len(CONFIG_FILES),

            elapsed,

        )

    # ======================================================
    # LOAD IF EMPTY
    # ======================================================

    def ensure_loaded(self):
        """
        Lazy loading.

        Configuration is loaded only once.
        """

        if not self._configs:

            self.load()

    # ======================================================
    # AVAILABLE CONFIGS
    # ======================================================

    def available_configs(self):

        self.ensure_loaded()

        return sorted(

            self._configs.keys()

        )

    # ======================================================
    # GET WHOLE CONFIG
    # ======================================================

    def get_config(
        self,
        name: str,
    ) -> Dict[str, Any]:

        self.ensure_loaded()

        if name not in self._configs:

            raise KeyError(

                f"Configuration '{name}' not loaded."

            )

        return deepcopy(

            self._configs[name]

        )
        # ======================================================
    # GET VALUE
    # ======================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        """
        Get configuration value using dot notation.

        Example

        config.get("ocr.render.dpi")
        """

        self.ensure_loaded()

        if not key:

            return default

        parts = key.split(".")

        config_name = parts[0]

        if config_name not in self._configs:

            return default

        value = self._configs[config_name]

        for part in parts[1:]:

            if not isinstance(value, dict):

                return default

            if part not in value:

                return default

            value = value[part]

        return deepcopy(value)

    # ======================================================
    # EXISTS
    # ======================================================

    def exists(
        self,
        key: str,
    ) -> bool:

        return self.get(

            key,

            default=None,

        ) is not None

    # ======================================================
    # SET VALUE
    # ======================================================

    def set(
        self,
        key: str,
        value: Any,
    ):
        """
        Update cached configuration.

        Does not modify JSON files.
        """

        self.ensure_loaded()

        parts = key.split(".")

        if len(parts) < 2:

            raise ValueError(

                "Key must use dot notation."

            )

        config_name = parts[0]

        if config_name not in self._configs:

            self._configs[config_name] = {}

        current = self._configs[config_name]

        for part in parts[1:-1]:

            if (

                part not in current

                or

                not isinstance(

                    current[part],

                    dict,

                )

            ):

                current[part] = {}

            current = current[part]

        current[parts[-1]] = value

    # ======================================================
    # GET MANY
    # ======================================================

    def get_many(
        self,
        *keys: str,
    ) -> Dict[str, Any]:

        return {

            key: self.get(key)

            for key in keys

        }

    # ======================================================
    # EXPORT CACHE
    # ======================================================

    def export(self) -> Dict[str, Any]:

        self.ensure_loaded()

        return deepcopy(

            self._configs

        )
        # ======================================================
    # ENVIRONMENT
    # ======================================================

    def get_environment(self) -> str:
        """
        Get current application environment.
        """

        return os.getenv(

            "APP_ENV",

            "development",

        ).lower()

    # ======================================================
    # RELOAD CONFIGURATION
    # ======================================================

    def reload(self):
        """
        Reload every configuration file.
        """

        start = time.perf_counter()

        with self._lock:

            temp_configs = {}

            for name in CONFIG_FILES:

                temp_configs[name] = self.load_config(

                    name

                )

            self._configs = temp_configs

            self._metrics.reload_count += 1

            self._metrics.last_loaded = time.time()

        elapsed = round(

            time.perf_counter()

            -

            start,

            3,

        )

        logger.info(

            "Configuration reloaded in %.3f sec.",

            elapsed,

        )

    # ======================================================
    # CLEAR CACHE
    # ======================================================

    def clear_cache(self):

        with self._lock:

            self._configs.clear()

        logger.info(

            "Configuration cache cleared."

        )

    # ======================================================
    # IS LOADED
    # ======================================================

    def is_loaded(self) -> bool:

        return bool(

            self._configs

        )

    # ======================================================
    # LAST LOAD TIME
    # ======================================================

    def last_loaded(self):

        return self._metrics.last_loaded

    # ======================================================
    # CONFIGURATION SUMMARY
    # ======================================================

    def summary(self):

        self.ensure_loaded()

        return {

            "environment": self.get_environment(),

            "loaded": self.is_loaded(),

            "config_files": len(

                self._configs

            ),

            "available": sorted(

                self._configs.keys()

            ),

            "last_loaded": self.last_loaded(),

            "reload_count": self._metrics.reload_count,

        }
        # ======================================================
    # VALIDATE CONFIGURATION
    # ======================================================

    def validate(self):
        """
        Validate loaded configuration.
        """

        self.ensure_loaded()

        errors = []

        # ----------------------------------------------
        # Check required configuration files
        # ----------------------------------------------

        for config_name in CONFIG_FILES:

            if config_name not in self._configs:

                errors.append(

                    f"Missing configuration: {config_name}"

                )

        # ----------------------------------------------
        # Check configuration is dictionary
        # ----------------------------------------------

        for name, config in self._configs.items():

            if not isinstance(config, dict):

                errors.append(

                    f"{name} must be a dictionary."

                )

        if errors:

            raise RuntimeError(

                "\n".join(errors)

            )

        logger.info(

            "Configuration validation successful."

        )

        return True

    # ======================================================
    # REQUIRED KEY
    # ======================================================

    def require(
        self,
        key: str,
    ):
        """
        Return configuration value.

        Raise exception if missing.
        """

        value = self.get(

            key,

            default=None,

        )

        if value is None:

            raise KeyError(

                f"Missing configuration key: {key}"

            )

        return value

    # ======================================================
    # VALIDATE REQUIRED KEYS
    # ======================================================

    def validate_keys(
        self,
        keys,
    ):
        """
        Validate required configuration keys.
        """

        missing = []

        for key in keys:

            if not self.exists(

                key

            ):

                missing.append(

                    key

                )

        if missing:

            raise KeyError(

                "Missing configuration keys:\n"

                +

                "\n".join(missing)

            )

        return True

    # ======================================================
    # CONFIGURATION STATUS
    # ======================================================

    def status(self):

        try:

            self.validate()

            return {

                "healthy": True,

                "errors": [],

            }

        except Exception as exc:

            return {

                "healthy": False,

                "errors": [

                    str(exc)

                ],

            }

    # ======================================================
    # SAFE GET
    # ======================================================

    def safe_get(
        self,
        key,
        default=None,
    ):
        """
        Never raise exceptions.
        """

        try:

            return self.get(

                key,

                default,

            )

        except Exception:

            return default
            # ======================================================
    # METRICS
    # ======================================================

    def get_metrics(self) -> Dict[str, Any]:
        """
        Return service metrics.
        """

        return {

            "load_count": self._metrics.load_count,

            "reload_count": self._metrics.reload_count,

            "failed_loads": self._metrics.failed_loads,

            "last_loaded": self._metrics.last_loaded,

            "loaded_configs": len(self._configs),

        }

    # ======================================================
    # HEALTH
    # ======================================================

    def health(self) -> Dict[str, Any]:
        """
        Service health.
        """

        status = self.status()

        return {

            "service": SERVICE_NAME,

            "version": SERVICE_VERSION,

            "healthy": status["healthy"],

            "environment": self.get_environment(),

            "metrics": self.get_metrics(),

            "loaded": self.is_loaded(),

            "config_count": len(self._configs),

            "errors": status["errors"],

        }

    # ======================================================
    # SELF TEST
    # ======================================================

    def self_test(self) -> Dict[str, Any]:
        """
        Run configuration self-test.
        """

        try:

            self.ensure_loaded()

            self.validate()

            return {

                "success": True,

                "service": SERVICE_NAME,

                "version": SERVICE_VERSION,

            }

        except Exception as exc:

            logger.exception(

                "Configuration self-test failed: %s",

                exc,

            )

            return {

                "success": False,

                "error": str(exc),

            }

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):
        """
        Clear cache and reload configuration.
        """

        with self._lock:

            self.clear_cache()

            self.load()

        logger.info(

            "Configuration service reset."

        )

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(self):
        """
        Shutdown configuration service.
        """

        logger.info(

            "%s shutting down.",

            SERVICE_NAME,

        )

    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(self):

        return self

    def __exit__(

        self,

        exc_type,

        exc_value,

        traceback,

    ):

        self.shutdown()

        return False
    # ==========================================================
# SINGLETON
# ==========================================================

config = ConfigService()

try:

    config.load()

    config.validate()

    logger.info(

        "Configuration initialized successfully."

    )

except Exception as exc:

    logger.exception(

        "Failed to initialize configuration: %s",

        exc,

    )

    raise

# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "ConfigService",

    "config",

]
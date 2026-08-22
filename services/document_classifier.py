"""
==========================================================
DOCUMENT CLASSIFIER
AI Invoice Extractor
Production Version 1.0
==========================================================
"""

from __future__ import annotations

import re
import threading
import time

from copy import deepcopy
from dataclasses import dataclass
from typing import Dict, Any, Optional

from logger import logger

# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = "Document Classifier"

SERVICE_VERSION = "1.0.0"

LOG_SEPARATOR = "=" * 70

# ==========================================================
# DOCUMENT TYPES
# ==========================================================

DOCUMENT_INVOICE = "invoice"

DOCUMENT_TAX_INVOICE = "tax_invoice"

DOCUMENT_RECEIPT = "receipt"

DOCUMENT_CREDIT_NOTE = "credit_note"

DOCUMENT_DEBIT_NOTE = "debit_note"

DOCUMENT_PURCHASE_ORDER = "purchase_order"

DOCUMENT_DELIVERY_CHALLAN = "delivery_challan"

DOCUMENT_QUOTATION = "quotation"

DOCUMENT_UNKNOWN = "unknown"

DOCUMENT_TYPES = [

    DOCUMENT_INVOICE,

    DOCUMENT_TAX_INVOICE,

    DOCUMENT_RECEIPT,

    DOCUMENT_CREDIT_NOTE,

    DOCUMENT_DEBIT_NOTE,

    DOCUMENT_PURCHASE_ORDER,

    DOCUMENT_DELIVERY_CHALLAN,

    DOCUMENT_QUOTATION,

    DOCUMENT_UNKNOWN,

]

# ==========================================================
# LIMITS
# ==========================================================

MAX_INPUT_LENGTH = 50000

MIN_CONFIDENCE = 0.50

HIGH_CONFIDENCE = 0.90

# ==========================================================
# DEFAULT RESULT
# ==========================================================

DEFAULT_RESULT = {

    "document_type": DOCUMENT_UNKNOWN,

    "confidence": 0.0,

    "method": "",

    "matched_keywords": [],

    "matched_patterns": [],

    "processing_time": 0.0,

}

# ==========================================================
# METRICS
# ==========================================================

@dataclass
class ClassifierMetrics:

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    keyword_matches: int = 0

    regex_matches: int = 0

    ai_matches: int = 0

    total_processing_time: float = 0.0

# ==========================================================
# DOCUMENT CLASSIFIER
# ==========================================================

class DocumentClassifier:
    """
    Enterprise Document Classifier

    Responsibilities

    - Normalize OCR text
    - Keyword Classification
    - Regex Classification
    - Rule-based Classification
    - AI Classification (optional)
    - Confidence Calculation
    - Health Monitoring
    """

    def __init__(self):

        self.metrics = ClassifierMetrics()

        self.lock = threading.Lock()

        logger.info(
            "%s %s Initialized",
            SERVICE_NAME,
            SERVICE_VERSION,
        )

    # ======================================================
    # HELPERS
    # ======================================================

    def empty_result(self) -> Dict[str, Any]:

        return deepcopy(DEFAULT_RESULT)

    def normalize_text(
        self,
        text: str,
    ) -> str:

        if not isinstance(text, str):

            raise TypeError(
                "OCR text must be string."
            )

        text = text.replace(
            "\x00",
            "",
        )

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.strip()

        if len(text) > MAX_INPUT_LENGTH:

            logger.warning(
                "Input truncated."
            )

            text = text[:MAX_INPUT_LENGTH]

        return text.lower()

    # ======================================================
    # HEALTH
    # ======================================================

    def health(self):

        return {

            "service": SERVICE_NAME,

            "version": SERVICE_VERSION,

            "status": "healthy",

            "metrics": self.get_metrics(),

        }

    def get_metrics(self):

        average = 0.0

        if self.metrics.successful_requests:

            average = (

                self.metrics.total_processing_time

                / self.metrics.successful_requests

            )

        return {

            "requests": self.metrics.total_requests,

            "success": self.metrics.successful_requests,

            "failed": self.metrics.failed_requests,

            "keyword_matches": self.metrics.keyword_matches,

            "regex_matches": self.metrics.regex_matches,

            "ai_matches": self.metrics.ai_matches,

            "average_processing_time": round(
                average,
                3,
            ),

        }

    def reset_metrics(self):

        self.metrics = ClassifierMetrics()

        logger.info(
            "Classifier metrics reset."
        )
            # ======================================================
    # KEYWORD DATABASE
    # ======================================================

    KEYWORD_DATABASE = {

        DOCUMENT_INVOICE: {

            "invoice": 10,
            "invoice no": 15,
            "invoice number": 15,
            "bill no": 12,
            "bill number": 12,
            "tax invoice": 25,
            "gstin": 10,
            "cgst": 8,
            "sgst": 8,
            "igst": 8,
            "hsn": 8,
            "taxable value": 8,
            "grand total": 10,
            "total amount": 10,

        },

        DOCUMENT_RECEIPT: {

            "receipt": 20,
            "payment received": 18,
            "cash received": 18,
            "receipt no": 15,
            "received with thanks": 20,

        },

        DOCUMENT_PURCHASE_ORDER: {

            "purchase order": 25,
            "po number": 20,
            "po no": 20,
            "supplier": 8,
            "ordered quantity": 8,

        },

        DOCUMENT_DELIVERY_CHALLAN: {

            "delivery challan": 30,
            "challan": 15,
            "delivery note": 15,
            "dispatch": 10,

        },

        DOCUMENT_CREDIT_NOTE: {

            "credit note": 30,
            "credit memo": 20,

        },

        DOCUMENT_DEBIT_NOTE: {

            "debit note": 30,
            "debit memo": 20,

        },

        DOCUMENT_QUOTATION: {

            "quotation": 30,
            "quote": 15,
            "quotation no": 20,
            "valid until": 15,

        },

    }

    # ======================================================
    # KEYWORD CLASSIFIER
    # ======================================================

    def classify_keywords(
        self,
        document_text: str,
    ) -> Dict[str, Any]:

        start_time = time.perf_counter()

        self.metrics.total_requests += 1

        text = self.normalize_text(document_text)

        scores = {}

        matched_keywords = {}

        for document_type, keywords in self.KEYWORD_DATABASE.items():

            score = 0

            matched = []

            for keyword, weight in keywords.items():

                if keyword in text:

                    score += weight

                    matched.append(keyword)

            scores[document_type] = score

            matched_keywords[document_type] = matched

        best_document = DOCUMENT_UNKNOWN

        best_score = 0

        for document_type, score in scores.items():

            if score > best_score:

                best_score = score

                best_document = document_type

        result = self.empty_result()

        if best_score > 0:

            confidence = min(best_score / 100.0, 1.0)

            result["document_type"] = best_document

            result["confidence"] = round(confidence, 2)

            result["method"] = "keywords"

            result["matched_keywords"] = matched_keywords[best_document]

            self.metrics.keyword_matches += 1

        elapsed = time.perf_counter() - start_time

        result["processing_time"] = round(elapsed, 3)

        self.metrics.total_processing_time += elapsed

        self.metrics.successful_requests += 1

        logger.info(

            "Keyword Classification : %s (%.2f)",

            result["document_type"],

            result["confidence"],

        )

        return result
        # ======================================================
    # RULE ENGINE
    # ======================================================

    def classify_rules(
        self,
        document_text: str,
    ) -> Dict[str, Any]:
        """
        Combine keyword and regex classifiers
        to produce a single document classification.
        """

        start_time = time.perf_counter()

        keyword_result = self.classify_keywords(
            document_text
        )

        regex_result = self.classify_regex(
            document_text
        )

        result = self.empty_result()

        keyword_conf = keyword_result["confidence"]

        regex_conf = regex_result["confidence"]

        # ----------------------------------------------
        # Both classifiers agree
        # ----------------------------------------------

        if (

            keyword_result["document_type"]

            ==

            regex_result["document_type"]

            and

            keyword_result["document_type"]

            != DOCUMENT_UNKNOWN

        ):

            result["document_type"] = (

                keyword_result["document_type"]

            )

            result["confidence"] = round(

                max(keyword_conf, regex_conf),

                2,

            )

            result["method"] = "keyword+regex"

            result["matched_keywords"] = (

                keyword_result["matched_keywords"]

            )

            result["matched_patterns"] = (

                regex_result["matched_patterns"]

            )

        # ----------------------------------------------
        # Keyword is stronger
        # ----------------------------------------------

        elif keyword_conf >= regex_conf:

            result = deepcopy(keyword_result)

        # ----------------------------------------------
        # Regex is stronger
        # ----------------------------------------------

        else:

            result = deepcopy(regex_result)

        elapsed = time.perf_counter() - start_time

        result["processing_time"] = round(

            elapsed,

            3,

        )

        logger.info(

            "Rule Engine : %s (%.2f)",

            result["document_type"],

            result["confidence"],

        )

        return result
        # ======================================================
    # AI CLASSIFIER
    # ======================================================

    def classify_ai(
        self,
        document_text: str,
        ai_engine=None,
    ) -> Dict[str, Any]:
        """
        AI-based document classification.

        This is only used as a fallback when
        keyword and regex classification
        are not confident enough.
        """

        start_time = time.perf_counter()

        result = self.empty_result()

        if ai_engine is None:

            logger.warning(
                "AI engine not available. "
                "Skipping AI classification."
            )

            return result

        try:

            prompt = f"""
You are an expert document classifier.

Determine ONLY the document type.

Possible values:

invoice

tax_invoice

receipt

credit_note

debit_note

purchase_order

delivery_challan

quotation

unknown

Return ONLY one value.

Document:

{document_text[:5000]}
"""

            response = ai_engine.generate_response(
                prompt
            )

            prediction = response.strip().lower()

            prediction = prediction.replace(
                '"',
                ""
            )

            prediction = prediction.replace(
                "'",
                ""
            )

            prediction = prediction.strip()

            if prediction in DOCUMENT_TYPES:

                result["document_type"] = prediction

                result["confidence"] = 0.90

                result["method"] = "ai"

                self.metrics.ai_matches += 1

            else:

                logger.warning(
                    "Unknown AI prediction: %s",
                    prediction,
                )

        except Exception:

            logger.exception(
                "AI classification failed."
            )

        elapsed = time.perf_counter() - start_time

        result["processing_time"] = round(
            elapsed,
            3,
        )

        return result
        # ======================================================
    # MASTER CLASSIFICATION PIPELINE
    # ======================================================

    def classify(
        self,
        document_text: str,
        ai_engine=None,
    ) -> Dict[str, Any]:
        """
        Enterprise document classification pipeline.

        Steps

        1. Normalize text
        2. Keyword classification
        3. Regex classification
        4. Rule engine
        5. AI fallback (optional)
        6. Return final result
        """

        pipeline_start = time.perf_counter()

        try:

            document_text = self.normalize_text(
                document_text
            )

            # ----------------------------------------
            # Rule Engine
            # ----------------------------------------

            result = self.classify_rules(
                document_text
            )

            # ----------------------------------------
            # AI Fallback
            # ----------------------------------------

            if (

                result["confidence"] < HIGH_CONFIDENCE

                and

                ai_engine is not None

            ):

                logger.info(

                    "Confidence %.2f below %.2f."

                    " Using AI classifier.",

                    result["confidence"],

                    HIGH_CONFIDENCE,

                )

                ai_result = self.classify_ai(

                    document_text,

                    ai_engine,

                )

                if (

                    ai_result["confidence"]

                    >

                    result["confidence"]

                ):

                    result = ai_result

            elapsed = (

                time.perf_counter()

                - pipeline_start

            )

            result["processing_time"] = round(

                elapsed,

                3,

            )

            logger.info(

                "Document classified as '%s' "

                "(%.2f)",

                result["document_type"],

                result["confidence"],

            )

            return result

        except Exception:

            self.metrics.failed_requests += 1

            logger.exception(

                "Document classification failed."

            )

            result = self.empty_result()

            result["processing_time"] = round(

                time.perf_counter()

                - pipeline_start,

                3,

            )

            return result
            # ======================================================
    # SERVICE STATUS
    # ======================================================

    def info(self) -> Dict[str, Any]:
        """
        Return classifier information.
        """

        return {

            "service": SERVICE_NAME,

            "version": SERVICE_VERSION,

            "supported_documents": DOCUMENT_TYPES,

            "status": "ready",

        }

    # ======================================================
    # SELF TEST
    # ======================================================

    def self_test(self) -> Dict[str, Any]:
        """
        Run internal health checks.
        """

        sample = """
        TAX INVOICE

        Invoice Number : INV-1001

        GSTIN : 07ABCDE1234F1Z5

        CGST

        SGST
        """

        result = self.classify(sample)

        return {

            "success": (

                result["document_type"]

                == DOCUMENT_INVOICE

            ),

            "result": result,

        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.reset_metrics()

        logger.info(

            "Document Classifier Reset."

        )

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(self):

        logger.info(

            "Shutting down Document Classifier."

        )

        self.reset()

    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(self):

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.shutdown()
        # ==========================================================
# SINGLETON
# ==========================================================

document_classifier = DocumentClassifier()

# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "DocumentClassifier",

    "document_classifier",

]
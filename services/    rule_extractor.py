"""
==========================================================
RULE EXTRACTOR
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
from typing import Any, Dict, List

from logger import logger

# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = "Rule Extractor"

SERVICE_VERSION = "1.0.0"

LOG_SEPARATOR = "=" * 70

# ==========================================================
# DEFAULT RESULT
# ==========================================================

DEFAULT_RESULT = {

    "vendor_name": "",

    "invoice_number": "",

    "invoice_date": "",

    "due_date": "",

    "gst_number": "",

    "pan_number": "",

    "currency": "",

    "subtotal": "",

    "cgst": "",

    "sgst": "",

    "igst": "",

    "tax": "",

    "grand_total": "",

    "confidence": {},

}

# ==========================================================
# METRICS
# ==========================================================

@dataclass
class RuleMetrics:

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    total_processing_time: float = 0.0

# ==========================================================
# RULE EXTRACTOR
# ==========================================================

class RuleExtractor:
    """
    Enterprise Rule Extractor

    Responsibilities

    - Regex Extraction

    - Pattern Matching

    - Validation

    - Confidence

    - Structured Output
    """

    def __init__(self):

        self.metrics = RuleMetrics()

        self.lock = threading.Lock()

        logger.info(

            "%s %s Initialized",

            SERVICE_NAME,

            SERVICE_VERSION,

        )

    # ======================================================
    # HELPERS
    # ======================================================

    def empty_result(self):

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

        return text.strip()

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

                /

                self.metrics.successful_requests

            )

        return {

            "requests": self.metrics.total_requests,

            "success": self.metrics.successful_requests,

            "failed": self.metrics.failed_requests,

            "average_processing_time": round(

                average,

                3,

            ),

        }

    def reset_metrics(self):

        self.metrics = RuleMetrics()

        logger.info(

            "Rule Extractor metrics reset."

        )
            # ======================================================
    # REGEX PATTERNS
    # ======================================================

    GST_PATTERNS = [

        r"\b\d{2}[A-Z]{5}\d{4}[A-Z][A-Z\d]Z[A-Z\d]\b",

    ]

    PAN_PATTERNS = [

        r"\b[A-Z]{5}\d{4}[A-Z]\b",

    ]

    INVOICE_PATTERNS = [

        r"(?i)invoice\s*(?:no|number)?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"(?i)bill\s*(?:no|number)?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

        r"(?i)inv\s*(?:no|number)?\s*[:\-]?\s*([A-Z0-9\/\-_]+)",

    ]

    DATE_PATTERNS = [

        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",

        r"\b\d{2}[.-]\d{2}[.-]\d{4}\b",

        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b",

    ]

    # ======================================================
    # GENERIC SEARCH
    # ======================================================

    def first_match(

        self,

        patterns,

        text,

        group=0,

    ):

        for pattern in patterns:

            match = re.search(

                pattern,

                text,

                flags=re.IGNORECASE,

            )

            if match:

                try:

                    return match.group(group).strip()

                except IndexError:

                    return match.group(0).strip()

        return ""

    # ======================================================
    # GST
    # ======================================================

    def extract_gst(

        self,

        text,

    ):

        value = self.first_match(

            self.GST_PATTERNS,

            text,

        )

        confidence = 1.00 if value else 0.0

        return value, confidence

    # ======================================================
    # PAN
    # ======================================================

    def extract_pan(

        self,

        text,

    ):

        value = self.first_match(

            self.PAN_PATTERNS,

            text,

        )

        confidence = 1.00 if value else 0.0

        return value, confidence

    # ======================================================
    # INVOICE NUMBER
    # ======================================================

    def extract_invoice_number(

        self,

        text,

    ):

        value = self.first_match(

            self.INVOICE_PATTERNS,

            text,

            group=1,

        )

        confidence = 0.98 if value else 0.0

        return value, confidence

    # ======================================================
    # DATE
    # ======================================================

    def extract_invoice_date(

        self,

        text,

    ):

        value = self.first_match(

            self.DATE_PATTERNS,

            text,

        )

        confidence = 0.90 if value else 0.0

        return value, confidence
        # ======================================================
    # CURRENCY PATTERNS
    # ======================================================

    CURRENCY_PATTERNS = [

        r"\bINR\b",

        r"\bUSD\b",

        r"\bEUR\b",

        r"\bGBP\b",

        r"\bAED\b",

        r"\bSAR\b",

        r"\bJPY\b",

        r"₹",

        r"\$",

        r"€",

    ]

    # ======================================================
    # AMOUNT PATTERNS
    # ======================================================

    TOTAL_PATTERNS = [

        r"(?i)grand\s*total\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

        r"(?i)total\s*amount\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

        r"(?i)amount\s*payable\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

    ]

    SUBTOTAL_PATTERNS = [

        r"(?i)subtotal\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

        r"(?i)taxable\s*value\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

    ]

    CGST_PATTERNS = [

        r"(?i)cgst\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

    ]

    SGST_PATTERNS = [

        r"(?i)sgst\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

    ]

    IGST_PATTERNS = [

        r"(?i)igst\s*[:\-]?\s*([₹$€]?\s?[\d,]+(?:\.\d{2})?)",

    ]

    # ======================================================
    # VENDOR NAME
    # ======================================================

    def extract_vendor_name(
        self,
        text,
    ):

        lines = [

            line.strip()

            for line in text.splitlines()

            if line.strip()

        ]

        ignore = {

            "invoice",

            "tax invoice",

            "bill",

            "receipt",

            "gstin",

            "cgst",

            "sgst",

            "igst",

        }

        for line in lines[:10]:

            lower = line.lower()

            if any(word in lower for word in ignore):

                continue

            if len(line) > 3:

                return line, 0.75

        return "", 0.0

    # ======================================================
    # CURRENCY
    # ======================================================

    def extract_currency(
        self,
        text,
    ):

        for pattern in self.CURRENCY_PATTERNS:

            match = re.search(

                pattern,

                text,

                flags=re.IGNORECASE,

            )

            if match:

                value = match.group(0)

                if value == "₹":

                    value = "INR"

                elif value == "$":

                    value = "USD"

                elif value == "€":

                    value = "EUR"

                return value.upper(), 0.95

        return "", 0.0

    # ======================================================
    # SUBTOTAL
    # ======================================================

    def extract_subtotal(
        self,
        text,
    ):

        value = self.first_match(

            self.SUBTOTAL_PATTERNS,

            text,

            group=1,

        )

        return value, 0.90 if value else 0.0

    # ======================================================
    # CGST
    # ======================================================

    def extract_cgst(
        self,
        text,
    ):

        value = self.first_match(

            self.CGST_PATTERNS,

            text,

            group=1,

        )

        return value, 0.95 if value else 0.0

    # ======================================================
    # SGST
    # ======================================================

    def extract_sgst(
        self,
        text,
    ):

        value = self.first_match(

            self.SGST_PATTERNS,

            text,

            group=1,

        )

        return value, 0.95 if value else 0.0

    # ======================================================
    # IGST
    # ======================================================

    def extract_igst(
        self,
        text,
    ):

        value = self.first_match(

            self.IGST_PATTERNS,

            text,

            group=1,

        )

        return value, 0.95 if value else 0.0

    # ======================================================
    # GRAND TOTAL
    # ======================================================

    def extract_grand_total(
        self,
        text,
    ):

        value = self.first_match(

            self.TOTAL_PATTERNS,

            text,

            group=1,

        )

        return value, 0.98 if value else 0.0
        # ======================================================
    # MASTER EXTRACTION PIPELINE
    # ======================================================

    def extract(
        self,
        document_text: str,
    ) -> Dict[str, Any]:
        """
        Enterprise Rule Extraction Pipeline

        Steps

        1. Normalize OCR text
        2. Run all rule extractors
        3. Store confidence
        4. Calculate overall confidence
        5. Return structured result
        """

        start = time.perf_counter()

        with self.lock:

            self.metrics.total_requests += 1

        try:

            document_text = self.normalize_text(
                document_text
            )

            result = self.empty_result()

            confidence = {}

            # ------------------------------------------
            # Vendor
            # ------------------------------------------

            value, score = self.extract_vendor_name(
                document_text
            )

            result["vendor_name"] = value

            confidence["vendor_name"] = score

            # ------------------------------------------
            # Invoice Number
            # ------------------------------------------

            value, score = self.extract_invoice_number(
                document_text
            )

            result["invoice_number"] = value

            confidence["invoice_number"] = score

            # ------------------------------------------
            # Invoice Date
            # ------------------------------------------

            value, score = self.extract_invoice_date(
                document_text
            )

            result["invoice_date"] = value

            confidence["invoice_date"] = score

            # ------------------------------------------
            # GST
            # ------------------------------------------

            value, score = self.extract_gst(
                document_text
            )

            result["gst_number"] = value

            confidence["gst_number"] = score

            # ------------------------------------------
            # PAN
            # ------------------------------------------

            value, score = self.extract_pan(
                document_text
            )

            result["pan_number"] = value

            confidence["pan_number"] = score

            # ------------------------------------------
            # Currency
            # ------------------------------------------

            value, score = self.extract_currency(
                document_text
            )

            result["currency"] = value

            confidence["currency"] = score

            # ------------------------------------------
            # Subtotal
            # ------------------------------------------

            value, score = self.extract_subtotal(
                document_text
            )

            result["subtotal"] = value

            confidence["subtotal"] = score

            # ------------------------------------------
            # CGST
            # ------------------------------------------

            value, score = self.extract_cgst(
                document_text
            )

            result["cgst"] = value

            confidence["cgst"] = score

            # ------------------------------------------
            # SGST
            # ------------------------------------------

            value, score = self.extract_sgst(
                document_text
            )

            result["sgst"] = value

            confidence["sgst"] = score

            # ------------------------------------------
            # IGST
            # ------------------------------------------

            value, score = self.extract_igst(
                document_text
            )

            result["igst"] = value

            confidence["igst"] = score

            # ------------------------------------------
            # Grand Total
            # ------------------------------------------

            value, score = self.extract_grand_total(
                document_text
            )

            result["grand_total"] = value

            confidence["grand_total"] = score

            # ------------------------------------------
            # Tax
            # ------------------------------------------

            taxes = []

            for key in ("cgst", "sgst", "igst"):

                if result[key]:

                    taxes.append(result[key])

            result["tax"] = ", ".join(taxes)

            confidence["tax"] = max(

                confidence.get("cgst", 0),

                confidence.get("sgst", 0),

                confidence.get("igst", 0),

            )

            # ------------------------------------------
            # Overall Confidence
            # ------------------------------------------

            scores = [

                score

                for score in confidence.values()

                if score > 0

            ]

            overall = (

                round(

                    sum(scores) / len(scores),

                    3,

                )

                if scores

                else 0.0

            )

            result["confidence"] = {

                **confidence,

                "overall": overall,

            }

            elapsed = (

                time.perf_counter()

                - start

            )

            with self.lock:

                self.metrics.successful_requests += 1

                self.metrics.total_processing_time += elapsed

            logger.info(

                "Rule extraction completed in %.3fs",

                elapsed,

            )

            return result

        except Exception:

            with self.lock:

                self.metrics.failed_requests += 1

            logger.exception(

                "Rule extraction failed."

            )

            return self.empty_result()
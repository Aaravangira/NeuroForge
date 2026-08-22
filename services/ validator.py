"""
==========================================================
VALIDATOR
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
from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict

from logger import logger

# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = "Validation Engine"

SERVICE_VERSION = "1.0.0"

# ==========================================================
# DEFAULT RESULT
# ==========================================================

DEFAULT_RESULT = {

    "valid": True,

    "score": 1.0,

    "errors": [],

    "warnings": [],

    "normalized": {},

}

# ==========================================================
# METRICS
# ==========================================================

@dataclass
class ValidationMetrics:

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    total_processing_time: float = 0.0

# ==========================================================
# VALIDATOR
# ==========================================================

class Validator:

    def __init__(self):

        self.metrics = ValidationMetrics()

        self.lock = threading.Lock()

        logger.info(

            "%s %s Initialized",

            SERVICE_NAME,

            SERVICE_VERSION,

        )

    def empty_result(self):

        return deepcopy(DEFAULT_RESULT)

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

        avg = 0.0

        if self.metrics.successful_requests:

            avg = (

                self.metrics.total_processing_time

                /

                self.metrics.successful_requests

            )

        return {

            "requests": self.metrics.total_requests,

            "success": self.metrics.successful_requests,

            "failed": self.metrics.failed_requests,

            "average_processing_time": round(

                avg,

                3,

            ),

        }

    def reset_metrics(self):

        self.metrics = ValidationMetrics()

        logger.info(

            "Validation metrics reset."

        )
            # ======================================================
    # REGEX PATTERNS
    # ======================================================

    GST_PATTERN = re.compile(
        r"^\d{2}[A-Z]{5}\d{4}[A-Z][A-Z0-9]Z[A-Z0-9]$"
    )

    PAN_PATTERN = re.compile(
        r"^[A-Z]{5}\d{4}[A-Z]$"
    )

    # ======================================================
    # NORMALIZATION
    # ======================================================

    def normalize_identifier(
        self,
        value: str,
    ) -> str:

        if not value:
            return ""

        return (
            str(value)
            .strip()
            .upper()
            .replace(" ", "")
        )

    # ======================================================
    # GST VALIDATION
    # ======================================================

    def validate_gst(
        self,
        gst: str,
    ):

        gst = self.normalize_identifier(gst)

        if not gst:

            return {
                "value": "",
                "valid": False,
                "error": "GSTIN missing",
            }

        if len(gst) != 15:

            return {
                "value": gst,
                "valid": False,
                "error": "GSTIN must contain 15 characters",
            }

        if not self.GST_PATTERN.fullmatch(gst):

            return {
                "value": gst,
                "valid": False,
                "error": "Invalid GSTIN format",
            }

        return {
            "value": gst,
            "valid": True,
            "error": "",
        }

    # ======================================================
    # PAN VALIDATION
    # ======================================================

    def validate_pan(
        self,
        pan: str,
    ):

        pan = self.normalize_identifier(pan)

        if not pan:

            return {
                "value": "",
                "valid": False,
                "error": "PAN missing",
            }

        if len(pan) != 10:

            return {
                "value": pan,
                "valid": False,
                "error": "PAN must contain 10 characters",
            }

        if not self.PAN_PATTERN.fullmatch(pan):

            return {
                "value": pan,
                "valid": False,
                "error": "Invalid PAN format",
            }

        return {
            "value": pan,
            "valid": True,
            "error": "",
        }
        # ======================================================
    # DATE FORMATS
    # ======================================================

    DATE_FORMATS = [

        "%d/%m/%Y",

        "%d-%m-%Y",

        "%d.%m.%Y",

        "%Y/%m/%d",

        "%Y-%m-%d",

        "%Y.%m.%d",

        "%d/%m/%y",

        "%d-%m-%y",

    ]

    # ======================================================
    # DATE VALIDATION
    # ======================================================

    def validate_date(
        self,
        date_value: str,
    ) -> Dict[str, Any]:
        """
        Validate and normalize invoice date.

        Returns ISO format:
        YYYY-MM-DD
        """

        if not date_value:

            return {

                "value": "",

                "normalized": "",

                "valid": False,

                "error": "Invoice date missing",

            }

        date_value = str(date_value).strip()

        parsed_date = None

        for fmt in self.DATE_FORMATS:

            try:

                parsed_date = datetime.strptime(
                    date_value,
                    fmt,
                )

                break

            except ValueError:

                continue

        if parsed_date is None:

            return {

                "value": date_value,

                "normalized": "",

                "valid": False,

                "error": "Unsupported date format",

            }

        today = datetime.today()

        if parsed_date.date() > today.date():

            return {

                "value": date_value,

                "normalized": parsed_date.strftime(
                    "%Y-%m-%d"
                ),

                "valid": False,

                "error": "Invoice date cannot be in the future",

            }

        return {

            "value": date_value,

            "normalized": parsed_date.strftime(
                "%Y-%m-%d"
            ),

            "valid": True,

            "error": "",

        }

    # ======================================================
    # DATE RANGE CHECK
    # ======================================================

    def validate_date_range(
        self,
        invoice_date: str,
        due_date: str,
    ) -> Dict[str, Any]:
        """
        Validate invoice date <= due date.
        """

        if not invoice_date or not due_date:

            return {

                "valid": True,

                "error": "",

            }

        invoice = self.validate_date(
            invoice_date
        )

        due = self.validate_date(
            due_date
        )

        if not invoice["valid"] or not due["valid"]:

            return {

                "valid": False,

                "error": "Unable to validate date range",

            }

        invoice_dt = datetime.strptime(

            invoice["normalized"],

            "%Y-%m-%d",

        )

        due_dt = datetime.strptime(

            due["normalized"],

            "%Y-%m-%d",

        )

        if due_dt < invoice_dt:

            return {

                "valid": False,

                "error": "Due date cannot be before invoice date",

            }

        return {

            "valid": True,

            "error": "",

        }
        # ======================================================
    # AMOUNT NORMALIZATION
    # ======================================================

    def normalize_amount(
        self,
        amount: Any,
    ) -> str:
        """
        Normalize amount string.

        Example:

        ₹12,500.50

        ->

        12500.50
        """

        if amount is None:

            return ""

        amount = str(amount).strip()

        amount = (
            amount
            .replace("₹", "")
            .replace("$", "")
            .replace("€", "")
            .replace("£", "")
            .replace(",", "")
            .strip()
        )

        return amount

    # ======================================================
    # PARSE DECIMAL
    # ======================================================

    def parse_amount(
        self,
        amount: Any,
    ):

        normalized = self.normalize_amount(amount)

        if not normalized:

            return None

        try:

            return Decimal(normalized)

        except InvalidOperation:

            return None

    # ======================================================
    # VALIDATE AMOUNT
    # ======================================================

    def validate_amount(
        self,
        amount: Any,
        field_name: str = "amount",
    ) -> Dict[str, Any]:

        value = self.parse_amount(amount)

        if value is None:

            return {

                "value": amount,

                "normalized": "",

                "decimal": None,

                "valid": False,

                "error": f"Invalid {field_name}",

            }

        if value < Decimal("0"):

            return {

                "value": amount,

                "normalized": str(value),

                "decimal": value,

                "valid": False,

                "error": f"{field_name} cannot be negative",

            }

        value = value.quantize(
            Decimal("0.01")
        )

        return {

            "value": amount,

            "normalized": str(value),

            "decimal": value,

            "valid": True,

            "error": "",

        }

    # ======================================================
    # VALIDATE MULTIPLE AMOUNTS
    # ======================================================

    def validate_amount_fields(
        self,
        invoice: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:

        fields = [

            "subtotal",

            "cgst",

            "sgst",

            "igst",

            "tax",

            "grand_total",

        ]

        results = {}

        for field in fields:

            results[field] = self.validate_amount(

                invoice.get(field),

                field,

            )

        return results
        # ======================================================
    # ARITHMETIC VALIDATION
    # ======================================================

    AMOUNT_TOLERANCE = Decimal("0.01")

    def validate_arithmetic(
        self,
        invoice: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Validate invoice arithmetic.

        Checks

        1. Total Tax
        2. Grand Total
        3. Tax Consistency
        """

        result = {

            "valid": True,

            "errors": [],

            "warnings": [],

        }

        subtotal = self.parse_amount(
            invoice.get("subtotal")
        )

        cgst = self.parse_amount(
            invoice.get("cgst")
        )

        sgst = self.parse_amount(
            invoice.get("sgst")
        )

        igst = self.parse_amount(
            invoice.get("igst")
        )

        grand_total = self.parse_amount(
            invoice.get("grand_total")
        )

        # ------------------------------------------
        # Missing subtotal or total
        # ------------------------------------------

        if subtotal is None or grand_total is None:

            result["warnings"].append(

                "Subtotal or Grand Total missing."

            )

            return result

        cgst = cgst or Decimal("0")

        sgst = sgst or Decimal("0")

        igst = igst or Decimal("0")

        total_tax = cgst + sgst + igst

        expected_total = subtotal + total_tax

        difference = abs(

            expected_total - grand_total

        )

        # ------------------------------------------
        # Total Validation
        # ------------------------------------------

        if difference > self.AMOUNT_TOLERANCE:

            result["valid"] = False

            result["errors"].append(

                (

                    "Grand Total mismatch. "

                    f"Expected {expected_total:.2f}, "

                    f"Found {grand_total:.2f}"

                )

            )

        # ------------------------------------------
        # GST Validation
        # ------------------------------------------

        if igst > 0 and (cgst > 0 or sgst > 0):

            result["valid"] = False

            result["errors"].append(

                "Invoice contains both IGST and CGST/SGST."

            )

        if cgst > 0 and sgst == 0:

            result["warnings"].append(

                "CGST exists but SGST missing."

            )

        if sgst > 0 and cgst == 0:

            result["warnings"].append(

                "SGST exists but CGST missing."

            )

        if cgst > 0 and sgst > 0:

            if abs(cgst - sgst) > self.AMOUNT_TOLERANCE:

                result["warnings"].append(

                    "CGST and SGST amounts differ."

                )

        result["calculated"] = {

            "subtotal": subtotal,

            "cgst": cgst,

            "sgst": sgst,

            "igst": igst,

            "total_tax": total_tax,

            "expected_total": expected_total,

            "actual_total": grand_total,

            "difference": difference,

        }

        return result
        # ======================================================
    # REQUIRED FIELD VALIDATION
    # ======================================================

    REQUIRED_FIELDS = {

        "vendor_name": "Vendor Name",

        "invoice_number": "Invoice Number",

        "invoice_date": "Invoice Date",

        "grand_total": "Grand Total",

    }

    OPTIONAL_FIELDS = {

        "gst_number": "GST Number",

        "pan_number": "PAN Number",

        "currency": "Currency",

        "subtotal": "Subtotal",

        "cgst": "CGST",

        "sgst": "SGST",

        "igst": "IGST",

    }

    # ======================================================
    # EMPTY CHECK
    # ======================================================

    def is_empty(
        self,
        value,
    ) -> bool:

        if value is None:

            return True

        if isinstance(value, str):

            return value.strip() == ""

        return False

    # ======================================================
    # REQUIRED FIELD VALIDATOR
    # ======================================================

    def validate_required_fields(
        self,
        invoice: Dict[str, Any],
    ) -> Dict[str, Any]:

        result = {

            "valid": True,

            "errors": [],

            "warnings": [],

            "missing_required": [],

            "missing_optional": [],

            "completeness_score": 0.0,

        }

        present_required = 0

        total_required = len(

            self.REQUIRED_FIELDS

        )

        # ----------------------------------------
        # Required Fields
        # ----------------------------------------

        for field, label in self.REQUIRED_FIELDS.items():

            value = invoice.get(field)

            if self.is_empty(value):

                result["valid"] = False

                result["errors"].append(

                    f"{label} is required."

                )

                result["missing_required"].append(

                    field

                )

            else:

                present_required += 1

        # ----------------------------------------
        # Optional Fields
        # ----------------------------------------

        for field, label in self.OPTIONAL_FIELDS.items():

            value = invoice.get(field)

            if self.is_empty(value):

                result["warnings"].append(

                    f"{label} not available."

                )

                result["missing_optional"].append(

                    field

                )

        # ----------------------------------------
        # Completeness Score
        # ----------------------------------------

        result["completeness_score"] = round(

            (

                present_required

                /

                total_required

            )

            * 100,

            2,

        )

        return result
        # ======================================================
    # MASTER VALIDATION PIPELINE
    # ======================================================

    def validate(
        self,
        invoice: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Enterprise Validation Pipeline

        Steps

        1. Required fields
        2. GST Validation
        3. PAN Validation
        4. Date Validation
        5. Amount Validation
        6. Arithmetic Validation
        7. Merge Results
        """

        start = time.perf_counter()

        with self.lock:

            self.metrics.total_requests += 1

        report = self.empty_result()

        try:

            # ==========================================
            # Required Fields
            # ==========================================

            required = self.validate_required_fields(
                invoice
            )

            # ==========================================
            # GST
            # ==========================================

            gst = self.validate_gst(

                invoice.get("gst_number", "")

            )

            # ==========================================
            # PAN
            # ==========================================

            pan = self.validate_pan(

                invoice.get("pan_number", "")

            )

            # ==========================================
            # Invoice Date
            # ==========================================

            invoice_date = self.validate_date(

                invoice.get("invoice_date", "")

            )

            due_date = self.validate_date(

                invoice.get("due_date", "")

            )

            date_range = self.validate_date_range(

                invoice.get("invoice_date", ""),

                invoice.get("due_date", ""),

            )

            # ==========================================
            # Amounts
            # ==========================================

            amounts = self.validate_amount_fields(
                invoice
            )

            # ==========================================
            # Arithmetic
            # ==========================================

            arithmetic = self.validate_arithmetic(
                invoice
            )

            # ==========================================
            # Normalized Values
            # ==========================================

            normalized = {

                "gst_number": gst["value"],

                "pan_number": pan["value"],

                "invoice_date": invoice_date.get(

                    "normalized",

                    "",

                ),

                "due_date": due_date.get(

                    "normalized",

                    "",

                ),

            }

            for field, value in amounts.items():

                normalized[field] = value.get(

                    "normalized",

                    "",

                )

            # ==========================================
            # Errors
            # ==========================================

            errors = []

            warnings = []

            errors.extend(

                required["errors"]

            )

            warnings.extend(

                required["warnings"]

            )

            if not gst["valid"]:

                errors.append(

                    gst["error"]

                )

            if not pan["valid"]:

                errors.append(

                    pan["error"]

                )

            if not invoice_date["valid"]:

                errors.append(

                    invoice_date["error"]

                )

            if not due_date["valid"] and invoice.get("due_date"):

                warnings.append(

                    due_date["error"]

                )

            if not date_range["valid"]:

                errors.append(

                    date_range["error"]

                )

            for field, validation in amounts.items():

                if not validation["valid"]:

                    errors.append(

                        validation["error"]

                    )

            errors.extend(

                arithmetic["errors"]

            )

            warnings.extend(

                arithmetic["warnings"]

            )

            # ==========================================
            # Overall Score
            # ==========================================

            score = required["completeness_score"] / 100

            penalty = min(

                len(errors) * 0.10,

                1.0,

            )

            score = max(

                score - penalty,

                0,

            )

            report = {

                "valid": len(errors) == 0,

                "score": round(

                    score,

                    3,

                ),

                "errors": errors,

                "warnings": warnings,

                "normalized": normalized,

                "details": {

                    "required": required,

                    "gst": gst,

                    "pan": pan,

                    "invoice_date": invoice_date,

                    "due_date": due_date,

                    "date_range": date_range,

                    "amounts": amounts,

                    "arithmetic": arithmetic,

                }

            }

            elapsed = (

                time.perf_counter()

                - start

            )

            with self.lock:

                self.metrics.successful_requests += 1

                self.metrics.total_processing_time += elapsed

            logger.info(

                "Validation completed in %.3fs",

                elapsed,

            )

            return report

        except Exception:

            with self.lock:

                self.metrics.failed_requests += 1

            logger.exception(

                "Validation pipeline failed."

            )

            report = self.empty_result()

            report["valid"] = False

            report["errors"].append(

                "Internal validation error."

            )

            return report
            # ======================================================
    # SERVICE INFORMATION
    # ======================================================

    def info(self) -> Dict[str, Any]:
        """
        Return validator information.
        """

        return {

            "service": SERVICE_NAME,

            "version": SERVICE_VERSION,

            "status": "ready",

            "supported_validations": [

                "required_fields",

                "gst",

                "pan",

                "dates",

                "amounts",

                "arithmetic",

            ],

        }

    # ======================================================
    # SELF TEST
    # ======================================================

    def self_test(self) -> Dict[str, Any]:
        """
        Execute an internal validation test.
        """

        sample = {

            "vendor_name": "ABC Technologies Pvt Ltd",

            "invoice_number": "INV-1001",

            "invoice_date": "15/07/2026",

            "gst_number": "07ABCDE1234F1Z5",

            "pan_number": "ABCDE1234F",

            "subtotal": "1000",

            "cgst": "90",

            "sgst": "90",

            "grand_total": "1180",

        }

        result = self.validate(sample)

        return {

            "success": result["valid"],

            "score": result["score"],

            "errors": result["errors"],

        }

    # ======================================================
    # RESET
    # ======================================================

    def reset(self):

        self.reset_metrics()

        logger.info(

            "Validation Engine reset."

        )

    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(self):

        logger.info(

            "Shutting down Validation Engine."

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

validator = Validator()

# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    "Validator",

    "validator",

]

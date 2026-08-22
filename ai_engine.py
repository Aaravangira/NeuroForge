"""
==========================================================
AI ENGINE
AI Invoice Extractor
Production Version 5.0
==========================================================
"""

from __future__ import annotations

import json
import os
import re
import threading
import time

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Dict, Optional

from openai import OpenAI

from logger import logger
import config


# ==========================================================
# SERVICE INFO
# ==========================================================

SERVICE_NAME = config.AI_SERVICE_NAME
SERVICE_VERSION = config.AI_SERVICE_VERSION

LOG_SEPARATOR = "=" * config.AI_LOG_SEPARATOR_WIDTH


# ==========================================================
# CONFIGURATION
# ==========================================================

AI_PROVIDER = config.AI_PROVIDER.strip().lower()
MODEL_NAME = config.MODEL_NAME.strip()
MAX_NEW_TOKENS = config.MAX_NEW_TOKENS
TEMPERATURE = config.TEMPERATURE

# Optional config values.
#
# We intentionally use getattr() so ai_engine.py
# does not crash if these names are not defined
# in config.py.

API_KEY = (
    config.DEEPSEEK_API_KEY
    if AI_PROVIDER == "deepseek"
    else config.OPENAI_API_KEY
)

BASE_URL = (
    config.DEEPSEEK_BASE_URL
    if AI_PROVIDER == "deepseek"
    else config.OPENAI_BASE_URL
)


# ==========================================================
# CONFIGURATION REFERENCES
# ==========================================================

MAX_INPUT_CHARS = config.AI_MAX_INPUT_CHARS
MAX_JSON_SIZE = config.AI_MAX_JSON_SIZE
MAX_RETRIES = config.AI_MAX_RETRIES
MIN_RESPONSE_LENGTH = config.AI_MIN_RESPONSE_LENGTH
MAX_FIELD_LENGTH = config.AI_MAX_FIELD_LENGTH
AI_CONFIDENCE_THRESHOLD = config.AI_CONFIDENCE_THRESHOLD
HUMAN_REVIEW_THRESHOLD = config.HUMAN_REVIEW_THRESHOLD
REQUIRED_FIELD_WEIGHT = config.AI_REQUIRED_FIELD_WEIGHT
OPTIONAL_FIELD_WEIGHT = config.AI_OPTIONAL_FIELD_WEIGHT
RETRY_SLEEP_CAP = config.AI_RETRY_SLEEP_CAP
FIELD_CONFIDENCE_RULES = config.AI_FIELD_CONFIDENCE_RULES


# ==========================================================
# FIELD DEFINITIONS
# ==========================================================

DEFAULT_RESULT: Dict[str, Any] = {
    # Document verification metadata
    "is_valid_document": False,
    "document_type": "",
    "document_confidence": 0.0,
    "document_reason": "",

    # Canonical invoice fields
    "vendor_name": "",
    "invoice_number": "",
    "invoice_date": "",
    "gst_number": "",
    "subtotal": "",
    "tax": "",
    "grand_total": "",
    "payment_method": "",
    "currency": "",
}

# Keep ALL_FIELDS limited to extractable invoice fields so the
# existing confidence engine is not polluted by document-level
# verification metadata.
ALL_FIELDS = [
    "vendor_name",
    "invoice_number",
    "invoice_date",
    "gst_number",
    "subtotal",
    "tax",
    "grand_total",
    "payment_method",
    "currency",
]

VERIFICATION_FIELDS = {
    "is_valid_document",
    "document_type",
    "document_confidence",
    "document_reason",
}

REQUIRED_FIELDS = list(config.REQUIRED_FIELDS)

OPTIONAL_FIELDS = [
    field
    for field in ALL_FIELDS
    if field not in REQUIRED_FIELDS
]


# ==========================================================
# FIELD PATTERNS
# ==========================================================

GST_PATTERN = re.compile(
    r"^[0-9]{2}"
    r"[A-Z0-9]{5}"
    r"[A-Z0-9]{4}"
    r"[A-Z]"
    r"[A-Z0-9]"
    r"Z"
    r"[A-Z0-9]$",
    re.IGNORECASE,
)

DATE_PATTERN = re.compile(
    r"^\d{1,4}[-/.\s]"
    r"\d{1,2}[-/.\s]"
    r"\d{1,4}$"
)


# ==========================================================
# SYSTEM PROMPT
# ==========================================================

SYSTEM_PROMPT = """
You are a production-grade document verification and billing-data extraction AI.

The OCR text supplied by the application is the ONLY source of truth.

============================================================
STAGE 1 — DOCUMENT VERIFICATION
============================================================

Determine whether the document is a genuine commercial billing document.

Valid document types include:
- invoice
- tax_invoice
- sales_invoice
- purchase_invoice
- receipt
- payment_receipt
- bill
- credit_note
- debit_note

Reject documents that are clearly unrelated, for example:
- bank statements
- resumes / CVs
- contracts / agreements
- passports / IDs
- newspaper pages / articles
- research reports
- general letters / emails
- unrelated documents

A valid receipt may not contain GST, subtotal, or an invoice number.
A foreign invoice may use VAT instead of GST.
A valid billing document does not need every optional field.

Strong billing evidence can include:
- invoice / receipt / bill terminology
- invoice or receipt number
- seller / vendor / supplier / merchant
- line items
- quantity / unit price
- subtotal
- tax / GST / VAT / CGST / SGST / IGST
- total / grand total / amount due / amount paid
- payment method / payment terms

Do NOT classify a document as billing merely because it contains a date,
a company name, or arbitrary numbers.

============================================================
STAGE 2 — FIELD EXTRACTION
============================================================

Extract ONLY information explicitly supported by the OCR text.
Never guess, hallucinate, fabricate, calculate, or infer unsupported values.
Missing values MUST be empty strings.

Field mapping:

vendor_name:
- vendor, seller, supplier, merchant, company, issuer, sold by, billed by, from

invoice_number:
- invoice number/no/#, receipt number/no/#, bill number/no, transaction number, document number

invoice_date:
- invoice date, issue date, date, receipt date, transaction date, payment date, date paid

gst_number:
- GST, GSTIN, GST number, GST ID

subtotal:
- subtotal, sub total, net amount, taxable amount, amount before tax, total before tax

tax:
- tax, tax amount, GST amount, VAT amount, CGST, SGST, IGST

grand_total:
- total, grand total, final total, total amount, amount due, amount payable, amount paid

payment_method:
- payment method/type, paid by, card, cash, bank transfer, UPI, RTGS, NEFT, cheque/check

currency:
Extract only explicitly supported currency codes/symbols such as INR, USD, EUR, GBP, CNY, JPY, AED, ₹, $, €, £. Do not guess currency from location.

Special semantic mappings:
- receipt number -> invoice_number
- date paid -> invoice_date
- total -> grand_total
- amount paid -> grand_total only when clearly the final amount paid for the document

============================================================
OUTPUT
============================================================

Return ONLY one valid JSON object.
Do not return Markdown or explanations.
Do not add fields outside this schema.

{
    "is_valid_document": false,
    "document_type": "",
    "document_confidence": 0.0,
    "document_reason": "",
    "vendor_name": "",
    "invoice_number": "",
    "invoice_date": "",
    "gst_number": "",
    "subtotal": "",
    "tax": "",
    "grand_total": "",
    "payment_method": "",
    "currency": ""
}
"""


# ==========================================================
# METRICS
# ==========================================================

@dataclass
class EngineMetrics:

    total_requests: int = 0

    successful_requests: int = 0

    failed_requests: int = 0

    retry_count: int = 0

    total_inference_time: float = 0.0

    model_load_count: int = 0

    validation_failures: int = 0

    json_failures: int = 0

    low_confidence_results: int = 0

    successful_extractions: int = 0

    human_review_required: int = 0

    total_processing_time: float = 0.0


# ==========================================================
# AI ENGINE
# ==========================================================

class AIEngine:
    """
    Production AI Engine.

    Responsibilities:

    - Provider configuration
    - DeepSeek API communication
    - Prompt construction
    - JSON recovery
    - JSON parsing
    - Schema validation
    - Field validation
    - Confidence scoring
    - Retry logic
    - Runtime metrics
    - Health monitoring
    """

    def __init__(self):

        self.client: Optional[
            OpenAI
        ] = None

        self.lock = threading.RLock()

        self.metrics_lock = (
            threading.Lock()
        )

        self.metrics = EngineMetrics()

        self.provider = AI_PROVIDER

        self.model_name = MODEL_NAME

        self.base_url = BASE_URL

        self.api_key = API_KEY

        logger.info(
            "%s %s Initializing",
            SERVICE_NAME,
            SERVICE_VERSION,
        )

        logger.info(
            "AI Provider : %s",
            self.provider,
        )

        logger.info(
            "AI Model : %s",
            self.model_name,
        )


    # ======================================================
    # RESULT HELPERS
    # ======================================================

    def empty_result(
        self,
    ) -> Dict[str, str]:

        return deepcopy(
            DEFAULT_RESULT
        )


    # ======================================================
    # CLIENT STATUS
    # ======================================================

    def is_model_loaded(self) -> bool:
        """
        Compatibility method.

        For API-based providers this means that
        the API client is initialized.
        """

        return self.client is not None


    # ======================================================
    # METRICS
    # ======================================================

    def _increment_metric(
        self,
        metric_name: str,
        amount: int = 1,
    ) -> None:

        with self.metrics_lock:

            current = getattr(
                self.metrics,
                metric_name,
                None,
            )

            if current is None:

                raise AttributeError(
                    f"Unknown metric: {metric_name}"
                )

            setattr(
                self.metrics,
                metric_name,
                current + amount,
            )


    def _add_metric(
        self,
        metric_name: str,
        amount: float,
    ) -> None:

        with self.metrics_lock:

            current = getattr(
                self.metrics,
                metric_name,
                None,
            )

            if current is None:

                raise AttributeError(
                    f"Unknown metric: {metric_name}"
                )

            setattr(
                self.metrics,
                metric_name,
                current + amount,
            )


    # ======================================================
    # DOCUMENT VALIDATION
    # ======================================================

    def validate_document_text(
        self,
        document_text: str,
    ) -> str:

        if not isinstance(
            document_text,
            str,
        ):

            raise TypeError(
                "document_text must be string."
            )

        document_text = (
            document_text
            .replace("\x00", "")
            .replace("\r\n", "\n")
            .replace("\r", "\n")
        )

        document_text = re.sub(
            r"\n{3,}",
            "\n\n",
            document_text,
        )

        document_text = re.sub(
            r"[ \t]{3,}",
            "  ",
            document_text,
        )

        document_text = (
            document_text.strip()
        )

        if not document_text:

            raise ValueError(
                "OCR text is empty."
            )

        if len(document_text) > MAX_INPUT_CHARS:

            logger.warning(
                "OCR text exceeds maximum size. "
                "Truncating."
            )

            document_text = (
                document_text[
                    :MAX_INPUT_CHARS
                ]
            )

        return document_text


    # ======================================================
    # DETERMINISTIC DOCUMENT VERIFICATION
    # ======================================================

    BILLING_KEYWORDS = {
        "invoice",
        "invoice number",
        "invoice no",
        "receipt",
        "receipt number",
        "bill",
        "bill no",
        "tax invoice",
        "sales invoice",
        "purchase invoice",
        "credit note",
        "debit note",
        "subtotal",
        "sub total",
        "grand total",
        "amount due",
        "amount paid",
        "payment method",
        "payment",
        "gst",
        "gstin",
        "vat",
        "tax",
        "unit price",
        "quantity",
        "supplier",
        "vendor",
        "seller",
        "merchant",
    }

    NON_BILLING_KEYWORDS = {
        "resume",
        "curriculum vitae",
        "passport",
        "bank statement",
        "employment agreement",
        "contract",
        "agreement",
        "newspaper",
        "research paper",
    }

    DOCUMENT_TYPE_PATTERNS = {
        "tax_invoice": ["tax invoice"],
        "credit_note": ["credit note"],
        "debit_note": ["debit note"],
        "receipt": ["receipt"],
        "invoice": ["invoice"],
        "bill": ["bill"],
    }

    def verify_document_type(
        self,
        document_text: str,
    ) -> Dict[str, Any]:
        """Conservative, deterministic billing-document pre-check."""

        text = document_text.lower().strip()

        if not text:
            return {
                "is_valid_document": False,
                "document_type": "",
                "document_confidence": 1.0,
                "document_reason": "OCR text is empty.",
            }

        positive_matches = [
            keyword
            for keyword in self.BILLING_KEYWORDS
            if keyword in text
        ]
        negative_matches = [
            keyword
            for keyword in self.NON_BILLING_KEYWORDS
            if keyword in text
        ]

        detected_type = ""
        for document_type, patterns in self.DOCUMENT_TYPE_PATTERNS.items():
            if any(pattern in text for pattern in patterns):
                detected_type = document_type
                break

        has_identifier = bool(
            re.search(
                r"\b(invoice|receipt|bill)\s*(number|no|#|id)?\s*[:#-]?\s*[a-z0-9][a-z0-9/_-]{2,}",
                text,
                re.IGNORECASE,
            )
        )

        has_money = bool(
            re.search(
                r"(?:₹|\$|€|£)\s*\d+(?:[,.]\d+)*|\b\d+(?:[,.]\d{1,2})?\s*(?:INR|USD|EUR|GBP|CNY|JPY|AED)\b",
                text,
                re.IGNORECASE,
            )
        )

        has_total = any(
            term in text
            for term in ("total", "grand total", "amount due", "amount paid", "subtotal")
        )

        has_payment = any(
            term in text
            for term in (
                "payment", "paid", "rtgs", "neft", "upi",
                "cash", "visa", "mastercard", "bank transfer",
            )
        )

        score = 0.0
        if positive_matches:
            score += 0.25
        if detected_type:
            score += 0.25
        if has_identifier:
            score += 0.20
        if has_money:
            score += 0.15
        if has_total:
            score += 0.10
        if has_payment:
            score += 0.05
        if negative_matches:
            score -= 0.40

        score = max(0.0, min(1.0, score))

        # Only reject before AI when evidence is strong.
        is_valid = score >= 0.50 and not (negative_matches and score < 0.70)

        reasons = []
        if positive_matches:
            reasons.append("billing terminology detected")
        if has_identifier:
            reasons.append("document identifier detected")
        if has_money:
            reasons.append("monetary value detected")
        if has_total:
            reasons.append("total/amount field detected")
        if has_payment:
            reasons.append("payment evidence detected")
        if negative_matches:
            reasons.append("non-billing terminology detected")

        return {
            "is_valid_document": is_valid,
            "document_type": detected_type,
            "document_confidence": round(score, 2),
            "document_reason": "; ".join(reasons) if reasons else "Insufficient billing evidence.",
        }


    # ======================================================
    # PROMPT BUILDER
    # ======================================================

    def build_prompt(
        self,
        document_text: str,
        retry_mode: int = 1,
    ) -> str:

        document_text = self.validate_document_text(document_text)
        verification = self.verify_document_type(document_text)

        if retry_mode == 1:
            instruction = (
                "Verify the document first. If it is a valid billing document, "
                "extract all supported fields. Return only JSON."
            )
        elif retry_mode == 2:
            instruction = (
                "Re-check the billing-document classification and field mappings. "
                "Return exactly one valid JSON object."
            )
        else:
            instruction = (
                "Perform strict evidence-based extraction. "
                "Do not invent missing values."
            )

        return (
            f"{SYSTEM_PROMPT}\n\n"
            f"DETERMINISTIC PRECHECK:\n"
            f"valid={verification['is_valid_document']}\n"
            f"type={verification['document_type']}\n"
            f"confidence={verification['document_confidence']}\n"
            f"reason={verification['document_reason']}\n\n"
            f"{instruction}\n\n"
            f"DOCUMENT OCR TEXT:\n"
            f"{document_text}\n\n"
            f"JSON:"
        )


    # ======================================================
    # CLIENT INITIALIZATION
    # ======================================================

    def load_model(self) -> None:
        """
        Initialize API client.

        Kept as load_model() for compatibility with
        the previous Transformers implementation.
        """

        if self.is_model_loaded():

            return

        with self.lock:

            if self.is_model_loaded():

                return

            logger.info(
                LOG_SEPARATOR
            )

            logger.info(
                "Initializing AI Provider"
            )

            logger.info(
                "Provider : %s",
                self.provider,
            )

            logger.info(
                "Model : %s",
                self.model_name,
            )

            if not self.api_key:

                raise RuntimeError(
                    "AI API key is not configured. "
                    "Set DEEPSEEK_API_KEY in .env."
                )

            if self.provider == "deepseek":

                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url,
                )

            elif self.provider == "openai":

                openai_base_url = config.OPENAI_BASE_URL

                self.client = OpenAI(
                    api_key=self.api_key,
                    base_url=openai_base_url,
                )

            else:

                raise RuntimeError(
                    f"Provider '{self.provider}' "
                    f"is not implemented in this AI engine."
                )

            self._increment_metric(
                "model_load_count"
            )

            logger.info(
                "AI Provider initialized successfully."
            )


    # ======================================================
    # UNLOAD
    # ======================================================

    def unload_model(self) -> None:

        with self.lock:

            self.client = None

            logger.info(
                "AI client released."
            )


    # ======================================================
    # AI INFERENCE
    # ======================================================

    def generate_response(
        self,
        prompt: str,
    ) -> str:

        if not isinstance(
            prompt,
            str,
        ):

            raise TypeError(
                "Prompt must be a string."
            )

        prompt = prompt.strip()

        if not prompt:

            raise ValueError(
                "Prompt cannot be empty."
            )

        if not self.is_model_loaded():

            self.load_model()

        self._increment_metric(
            "total_requests"
        )

        start_time = (
            time.perf_counter()
        )

        try:

            response = (
                self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": SYSTEM_PROMPT,
                        },
                        {
                            "role": "user",
                            "content": prompt,
                        },
                    ],
                    temperature=TEMPERATURE,
                    max_tokens=MAX_NEW_TOKENS,
                )
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            self._add_metric(
                "total_inference_time",
                elapsed,
            )

            if not response.choices:

                raise RuntimeError(
                    "AI provider returned no choices."
                )

            content = (
                response
                .choices[0]
                .message
                .content
            )

            if content is None:

                raise RuntimeError(
                    "AI provider returned empty content."
                )

            content = str(
                content
            ).strip()

            if len(content) < MIN_RESPONSE_LENGTH:

                raise ValueError(
                    "AI returned an insufficient response."
                )

            self._increment_metric(
                "successful_requests"
            )

            logger.info(
                "AI inference completed in %.2f sec",
                elapsed,
            )

            return content

        except Exception:

            self._increment_metric(
                "failed_requests"
            )

            logger.exception(
                "AI inference failed."
            )

            raise


    # ======================================================
    # JSON CLEANER
    # ======================================================

    def clean_json(
        self,
        text: str,
    ) -> str:

        if not isinstance(
            text,
            str,
        ):

            raise TypeError(
                "AI response must be string."
            )

        text = text.strip()

        if not text:

            raise ValueError(
                "Empty AI response."
            )

        text = re.sub(
            r"```(?:json)?",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = (
            text
            .replace("```", "")
            .strip()
        )

        if (
            text.startswith("{")
            and text.endswith("}")
        ):

            json_text = text

        else:

            start = text.find("{")

            if start == -1:

                self._increment_metric(
                    "json_failures"
                )

                raise ValueError(
                    "No JSON object found."
                )

            depth = 0
            in_string = False
            escape = False
            end = None

            for index in range(
                start,
                len(text),
            ):

                char = text[index]

                if escape:

                    escape = False
                    continue

                if (
                    char == "\\"
                    and in_string
                ):

                    escape = True
                    continue

                if char == '"':

                    in_string = (
                        not in_string
                    )

                    continue

                if in_string:

                    continue

                if char == "{":

                    depth += 1

                elif char == "}":

                    depth -= 1

                    if depth == 0:

                        end = index + 1

                        break

            if end is None:

                self._increment_metric(
                    "json_failures"
                )

                raise ValueError(
                    "Incomplete JSON returned by AI."
                )

            json_text = text[
                start:end
            ].strip()

        if len(json_text) > MAX_JSON_SIZE:

            self._increment_metric(
                "json_failures"
            )

            raise ValueError(
                "JSON exceeds maximum size."
            )

        return json_text


    # ======================================================
    # JSON PARSER
    # ======================================================

    def parse_json_response(
        self,
        text: str,
    ) -> Dict[str, Any]:

        json_text = (
            self.clean_json(text)
        )

        try:

            data = json.loads(
                json_text
            )

        except json.JSONDecodeError as ex:

            self._increment_metric(
                "json_failures"
            )

            logger.error(
                "JSON parsing failed: %s",
                ex,
            )

            raise ValueError(
                "Invalid JSON returned by AI."
            ) from ex

        if not isinstance(
            data,
            dict,
        ):

            self._increment_metric(
                "json_failures"
            )

            raise ValueError(
                "Root JSON must be an object."
            )

        return data


    # ======================================================
    # VALUE NORMALIZATION
    # ======================================================

    def normalize_value(
        self,
        value: Any,
    ) -> str:

        if value is None:

            return ""

        if isinstance(
            value,
            (
                dict,
                list,
                tuple,
                set,
            ),
        ):

            return ""

        value = str(
            value
        ).strip()

        if len(value) > MAX_FIELD_LENGTH:

            value = value[
                :MAX_FIELD_LENGTH
            ]

        return value


    # ======================================================
    # RESPONSE VALIDATION
    # ======================================================

    def validate_ai_response(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not isinstance(data, dict):
            raise TypeError(
                "AI response must be dictionary."
            )

        result = self.empty_result()

        result["is_valid_document"] = bool(
            data.get("is_valid_document", False)
        )
        result["document_type"] = self.normalize_value(
            data.get("document_type", "")
        )
        result["document_reason"] = self.normalize_value(
            data.get("document_reason", "")
        )

        try:
            document_confidence = float(
                data.get("document_confidence", 0.0)
            )
        except (TypeError, ValueError):
            document_confidence = 0.0

        result["document_confidence"] = round(
            max(0.0, min(1.0, document_confidence)),
            2,
        )

        for field in ALL_FIELDS:
            result[field] = self.normalize_value(
                data.get(field, "")
            )

        return result


    # ======================================================
    # FIELD VALIDATION
    # ======================================================

    def validate_field(
        self,
        field: str,
        value: str,
    ) -> float:

        value = (
            value or ""
        ).strip()

        if not value:
            return FIELD_CONFIDENCE_RULES["empty"]

        if field == "gst_number":

            normalized = (
                value
                .replace(" ", "")
                .upper()
            )

            gst_rules = FIELD_CONFIDENCE_RULES["gst_number"]

            if GST_PATTERN.match(normalized):
                return gst_rules["valid"]

            if len(normalized) >= gst_rules["partial_min_length"]:
                return gst_rules["partial"]

            return gst_rules["invalid"]

        if field == "invoice_date":

            date_rules = FIELD_CONFIDENCE_RULES["invoice_date"]

            if DATE_PATTERN.match(value):
                return date_rules["valid"]

            if len(value) >= date_rules["partial_min_length"]:
                return date_rules["partial"]

            return date_rules["invalid"]

        if field in FIELD_CONFIDENCE_RULES["monetary_fields"]:

            monetary_rules = FIELD_CONFIDENCE_RULES["monetary"]

            cleaned = re.sub(
                r"[^\d.,\-]",
                "",
                value,
            )

            if re.search(
                r"\d",
                cleaned,
            ):
                return monetary_rules["valid"]

            return monetary_rules["invalid"]

        if field in {"vendor_name", "invoice_number"}:

            rules = FIELD_CONFIDENCE_RULES[field]

            return (
                rules["valid"]
                if len(value) >= rules["min_length"]
                else rules["invalid"]
            )

        if field == "currency":

            rules = FIELD_CONFIDENCE_RULES["currency"]

            return (
                rules["valid"]
                if len(value) <= rules["max_length"]
                else rules["invalid"]
            )

        if field == "payment_method":

            rules = FIELD_CONFIDENCE_RULES["payment_method"]

            return (
                rules["valid"]
                if len(value) >= rules["min_length"]
                else rules["invalid"]
            )

        return FIELD_CONFIDENCE_RULES["default"]

    # ======================================================
    # FIELD CONFIDENCE
    # ======================================================

    def calculate_field_confidence(
        self,
        result: Dict[str, str],
    ) -> Dict[str, float]:

        return {
            field: round(
                self.validate_field(
                    field,
                    result.get(
                        field,
                        "",
                    ),
                ),
                2,
            )
            for field in ALL_FIELDS
        }


    # ======================================================
    # OVERALL CONFIDENCE
    # ======================================================

    def calculate_confidence(
        self,
        result: Dict[str, str],
    ) -> float:

        field_scores = (
            self.calculate_field_confidence(
                result
            )
        )

        required_scores = [
            field_scores[field]
            for field in REQUIRED_FIELDS
        ]

        optional_scores = [
            field_scores[field]
            for field in OPTIONAL_FIELDS
            if result.get(field)
        ]

        if not required_scores:

            return 0.0

        required_average = (
            sum(required_scores)
            / len(required_scores)
        )

        if optional_scores:

            optional_average = (
                sum(optional_scores)
                / len(optional_scores)
            )

            overall = (
                required_average * REQUIRED_FIELD_WEIGHT
                + optional_average * OPTIONAL_FIELD_WEIGHT
            )

        else:

            overall = required_average

        return round(
            max(
                0.0,
                min(
                    1.0,
                    overall,
                ),
            ),
            2,
        )


    # ======================================================
    # REQUIRED FIELDS
    # ======================================================

    def get_missing_required_fields(
        self,
        result: Dict[str, str],
    ) -> list[str]:

        return [
            field
            for field in REQUIRED_FIELDS
            if not result.get(
                field,
                "",
            ).strip()
        ]


    # ======================================================
    # STATUS
    # ======================================================

    def determine_status(
        self,
        confidence: float,
        missing_fields: list[str],
    ) -> str:

        if missing_fields:

            return "human_review"

        if confidence >= (
            AI_CONFIDENCE_THRESHOLD
        ):

            return "success"

        if confidence >= (
            HUMAN_REVIEW_THRESHOLD
        ):

            return "human_review"

        return "failed"


    # ======================================================
    # EXTRACTION PIPELINE
    # ======================================================

    def extract_invoice(
        self,
        document_text: str,
    ) -> Dict[str, Any]:

        pipeline_start = time.perf_counter()
        document_text = self.validate_document_text(document_text)

        # --------------------------------------------------
        # Deterministic document pre-check
        # --------------------------------------------------
        verification = self.verify_document_type(
            document_text
        )

        logger.info(
            "Document verification | valid=%s | type=%s | confidence=%.2f",
            verification["is_valid_document"],
            verification["document_type"],
            verification["document_confidence"],
        )

        # Reject only when the pre-check is strongly negative.
        # Ambiguous documents are still sent to the AI verifier.
        if (
            not verification["is_valid_document"]
            and verification["document_confidence"] >= 0.70
        ):
            failure = self.empty_result()
            failure.update({
                "is_valid_document": False,
                "document_type": verification["document_type"],
                "document_confidence": verification["document_confidence"],
                "document_reason": verification["document_reason"],
                "confidence": 0.0,
                "field_confidence": {field: 0.0 for field in ALL_FIELDS},
                "status": "failed",
                "processing_time": round(time.perf_counter() - pipeline_start, 2),
                "model_version": self.model_name,
                "provider": self.provider,
                "attempt": 0,
                "missing_fields": REQUIRED_FIELDS.copy(),
                "error": "Uploaded document does not appear to be a valid billing document.",
            })
            self._increment_metric("validation_failures")
            return failure

        last_exception = None

        for attempt in range(1, MAX_RETRIES + 1):
            logger.info(LOG_SEPARATOR)
            logger.info(
                "Invoice Extraction Attempt %d/%d",
                attempt,
                MAX_RETRIES,
            )
            logger.info(LOG_SEPARATOR)

            try:
                prompt = self.build_prompt(
                    document_text,
                    retry_mode=attempt,
                )

                ai_response = self.generate_response(prompt)
                parsed = self.parse_json_response(ai_response)
                result = self.validate_ai_response(parsed)

                # Merge deterministic evidence with AI classification.
                if not result["document_type"]:
                    result["document_type"] = verification["document_type"]

                result["document_confidence"] = round(
                    max(
                        float(result["document_confidence"]),
                        float(verification["document_confidence"]),
                    ),
                    2,
                )

                if (
                    not result["is_valid_document"]
                    and verification["is_valid_document"]
                ):
                    result["is_valid_document"] = True

                if not result["document_reason"]:
                    result["document_reason"] = verification["document_reason"]

                # --------------------------------------------------
                # Invoice field confidence / status
                # --------------------------------------------------
                missing_fields = self.get_missing_required_fields(result)
                field_confidence = self.calculate_field_confidence(result)
                confidence = self.calculate_confidence(result)

                if not result["is_valid_document"]:
                    status = "failed"
                else:
                    status = self.determine_status(
                        confidence,
                        missing_fields,
                    )

                processing_time = time.perf_counter() - pipeline_start

                result["confidence"] = confidence
                result["field_confidence"] = field_confidence
                result["status"] = status
                result["processing_time"] = round(processing_time, 2)
                result["model_version"] = self.model_name
                result["provider"] = self.provider
                result["attempt"] = attempt
                result["missing_fields"] = missing_fields

                self._add_metric(
                    "total_processing_time",
                    processing_time,
                )
                self._increment_metric(
                    "successful_extractions"
                )

                if status == "human_review":
                    self._increment_metric("human_review_required")
                    self._increment_metric("low_confidence_results")
                elif status == "failed":
                    self._increment_metric("low_confidence_results")

                logger.info("Extraction Completed")
                logger.info("Document Type : %s", result["document_type"])
                logger.info(
                    "Document Confidence : %.2f",
                    result["document_confidence"],
                )
                logger.info("Confidence : %.2f", confidence)
                logger.info("Status : %s", status)

                return result

            except Exception as ex:
                last_exception = ex
                logger.exception(
                    "Extraction attempt %d failed.",
                    attempt,
                )

                if attempt < MAX_RETRIES:
                    self._increment_metric("retry_count")
                    time.sleep(
                        min(attempt, RETRY_SLEEP_CAP)
                    )

        # --------------------------------------------------
        # FINAL FAILURE
        # --------------------------------------------------
        total_time = time.perf_counter() - pipeline_start
        failure = self.empty_result()

        failure["is_valid_document"] = verification["is_valid_document"]
        failure["document_type"] = verification["document_type"]
        failure["document_confidence"] = verification["document_confidence"]
        failure["document_reason"] = verification["document_reason"]
        failure["confidence"] = 0.0
        failure["field_confidence"] = {
            field: 0.0
            for field in ALL_FIELDS
        }
        failure["status"] = "failed"
        failure["processing_time"] = round(total_time, 2)
        failure["model_version"] = self.model_name
        failure["provider"] = self.provider
        failure["attempt"] = MAX_RETRIES
        failure["missing_fields"] = REQUIRED_FIELDS.copy()
        failure["error"] = (
            str(last_exception)
            if last_exception
            else "Unknown extraction error"
        )

        self._add_metric(
            "total_processing_time",
            total_time,
        )
        self._increment_metric("validation_failures")

        return failure


    # ======================================================
    # HEALTH
    # ======================================================

    def health(
        self,
    ) -> Dict[str, Any]:

        with self.metrics_lock:

            successful = (
                self.metrics.successful_requests
            )

            if successful:

                average_time = (
                    self.metrics.total_inference_time
                    / successful
                )

            else:

                average_time = 0.0

            return {

                "service": SERVICE_NAME,

                "version": SERVICE_VERSION,

                "status": (
                    "healthy"
                    if self.is_model_loaded()
                    else "not_loaded"
                ),

                "provider": self.provider,

                "model": self.model_name,

                "base_url": self.base_url,

                "client_loaded": (
                    self.is_model_loaded()
                ),

                "average_inference_time": round(
                    average_time,
                    2,
                ),

                "metrics": {
                    "requests":
                        self.metrics.total_requests,

                    "success":
                        self.metrics.successful_requests,

                    "failed":
                        self.metrics.failed_requests,

                    "retries":
                        self.metrics.retry_count,

                    "client_loads":
                        self.metrics.model_load_count,

                    "validation_failures":
                        self.metrics.validation_failures,

                    "json_failures":
                        self.metrics.json_failures,

                    "low_confidence_results":
                        self.metrics.low_confidence_results,

                    "human_review_required":
                        self.metrics.human_review_required,
                },
            }


    # ======================================================
    # METRICS
    # ======================================================

    def get_metrics(
        self,
    ) -> Dict[str, Any]:

        with self.metrics_lock:

            return {

                "total_requests":
                    self.metrics.total_requests,

                "successful_requests":
                    self.metrics.successful_requests,

                "failed_requests":
                    self.metrics.failed_requests,

                "retry_count":
                    self.metrics.retry_count,

                "model_load_count":
                    self.metrics.model_load_count,

                "validation_failures":
                    self.metrics.validation_failures,

                "json_failures":
                    self.metrics.json_failures,

                "low_confidence_results":
                    self.metrics.low_confidence_results,

                "human_review_required":
                    self.metrics.human_review_required,

                "successful_extractions":
                    self.metrics.successful_extractions,

                "total_inference_time":
                    round(
                        self.metrics.total_inference_time,
                        2,
                    ),

                "total_processing_time":
                    round(
                        self.metrics.total_processing_time,
                        2,
                    ),
            }


    # ======================================================
    # RESET METRICS
    # ======================================================

    def reset_metrics(
        self,
    ) -> None:

        with self.metrics_lock:

            self.metrics = (
                EngineMetrics()
            )

        logger.info(
            "Runtime metrics reset."
        )


    # ======================================================
    # SHUTDOWN
    # ======================================================

    def shutdown(
        self,
    ) -> None:

        logger.info(
            "Shutting down AI Engine..."
        )

        self.unload_model()

        logger.info(
            "AI Engine stopped."
        )


# ==========================================================
# GLOBAL AI ENGINE
# ==========================================================

_ai_engine = AIEngine()


# ==========================================================
# BACKWARD COMPATIBILITY
# ==========================================================

def extract_document(
    document_text: str,
) -> Dict[str, Any]:

    return _ai_engine.extract_invoice(
        document_text
    )
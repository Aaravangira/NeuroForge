
"""
AI Invoice Extractor
Invoice Service

Responsibilities:
    - AI invoice extraction
    - Document normalization
    - Required-field validation
    - Repository-based persistence
    - End-to-end invoice processing
"""

# ==========================================================
# STANDARD LIBRARIES
# ==========================================================

from copy import deepcopy
import time
from typing import Any

# ==========================================================
# PROJECT IMPORTS
# ==========================================================

from ai_engine import extract_document
from logger import logger
from repositories.repositories.invoice_repository import InvoiceRepository
from config import REQUIRED_FIELDS

# ==========================================================
# SERVICE CONFIGURATION
# ==========================================================

SERVICE_NAME = "Invoice Service"
SERVICE_VERSION = "2.0.0"




# ==========================================================
# DEFAULT DOCUMENT
# ==========================================================

DEFAULT_DOCUMENT: dict[str, str] = {
    "vendor_name": "",
    "invoice_number": "",
    "invoice_date": "",
    "gst_number": "",
    "subtotal": "",
    "tax": "",
    "grand_total": "",
    "payment_method": "",
    "currency": "",
    "raw_text": "",
    "filename": "",
}


# ==========================================================
# SERVICE
# ==========================================================

class InvoiceService:
    """
    Production invoice-processing service.

    Architecture:

        OCR
          ↓
        AI Extraction
          ↓
        Validation
          ↓
        InvoiceService
          ↓
        InvoiceRepository
          ↓
        database.save_invoice()
          ↓
        MySQL
    """

    def __init__(
        self,
        repository: InvoiceRepository | None = None,
    ) -> None:

        self.repository = (
            repository
            if repository is not None
            else InvoiceRepository()
        )

        logger.info(
            "%s v%s initialized",
            SERVICE_NAME,
            SERVICE_VERSION,
        )

    # ======================================================
    # VALIDATE DOCUMENT
    # ======================================================

    @staticmethod
    def validate_document(
        document: Any,
    ) -> dict[str, str]:
        """
        Normalize the AI response.

        Missing fields are populated with empty strings.
        """

        output = deepcopy(
            DEFAULT_DOCUMENT
        )

        if not isinstance(
            document,
            dict,
        ):

            logger.warning(
                "AI returned invalid document."
            )

            return output

        for key in DEFAULT_DOCUMENT:

            value = document.get(
                key,
                "",
            )

            if value is None:
                value = ""

            output[key] = str(
                value
            ).strip()

        return output

    # ======================================================
    # REQUIRED FIELD CHECK
    # ======================================================

    @staticmethod
    def check_required_fields(
        document: dict[str, str],
    ) -> list[str]:
        """
        Return missing required fields.
        """

        missing: list[str] = []

        for field in REQUIRED_FIELDS:

            if not document.get(field):

                missing.append(field)

        if missing:

            logger.warning(
                "Missing Required Fields : %s",
                ", ".join(missing),
            )

        return missing

    # ======================================================
    # PROCESS DOCUMENT
    # ======================================================

    def process_document(
        self,
        filename: str,
        document_text: str,
    ) -> dict[str, str]:
        """
        Run AI extraction against OCR text.
        """

        start_time = time.perf_counter()

        # --------------------------------------------------
        # Filename validation
        # --------------------------------------------------

        if not isinstance(
            filename,
            str,
        ):

            raise TypeError(
                "Filename must be string."
            )

        filename = filename.strip()

        if not filename:

            raise ValueError(
                "Filename cannot be empty."
            )

        # --------------------------------------------------
        # OCR validation
        # --------------------------------------------------

        if not isinstance(
            document_text,
            str,
        ):

            raise TypeError(
                "OCR text must be string."
            )

        document_text = document_text.strip()

        if not document_text:

            raise ValueError(
                "OCR returned empty text."
            )

        logger.info(
            "Processing Invoice : %s",
            filename,
        )

        # --------------------------------------------------
        # AI extraction
        # --------------------------------------------------

        try:

            document = extract_document(
                document_text
            )

        except Exception:

            logger.exception(
                "AI Extraction Failed : %s",
                filename,
            )

            raise

        # --------------------------------------------------
        # AI response validation
        # --------------------------------------------------

        if document is None:

            raise ValueError(
                "AI returned None."
            )

        if not isinstance(
            document,
            dict,
        ):

            raise TypeError(
                "AI response must be dictionary."
            )

        # --------------------------------------------------
        # Normalize
        # --------------------------------------------------

        document = self.validate_document(
            document
        )

        # --------------------------------------------------
        # Metadata
        # --------------------------------------------------

        document["filename"] = filename
        document["raw_text"] = document_text

        # --------------------------------------------------
        # Required fields
        # --------------------------------------------------

        self.check_required_fields(
            document
        )

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "AI Processing Completed : %s",
            filename,
        )

        logger.info(
            "Processing Time : %.3f sec",
            elapsed,
        )

        return document

    # ======================================================
    # SAVE DOCUMENT
    # ======================================================

    def save_document(
        self,
        filename: str,
        document: dict[str, Any],
    ) -> int | None:
        """
        Persist invoice through InvoiceRepository.
        """

        start_time = time.perf_counter()

        # --------------------------------------------------
        # Filename validation
        # --------------------------------------------------

        if not isinstance(
            filename,
            str,
        ):

            raise TypeError(
                "Filename must be string."
            )

        filename = filename.strip()

        if not filename:

            raise ValueError(
                "Filename cannot be empty."
            )

        # --------------------------------------------------
        # Document validation
        # --------------------------------------------------

        if not isinstance(
            document,
            dict,
        ):

            raise TypeError(
                "Document must be dictionary."
            )

        document = self.validate_document(
            document
        )

        document["filename"] = filename

        # --------------------------------------------------
        # Required field check
        # --------------------------------------------------

        missing = self.check_required_fields(
            document
        )

        if missing:

            logger.warning(
                "Invoice has missing required fields: %s",
                ", ".join(missing),
            )

        # --------------------------------------------------
        # Repository persistence
        # --------------------------------------------------

        try:

            invoice_id = self.repository.create(
                invoice=document,
                filename=filename,
                raw_text=document.get(
                    "raw_text",
                    "",
                ),
            )

        except Exception:

            logger.exception(
                "Database Save Failed : %s",
                filename,
            )

            raise

        # --------------------------------------------------
        # Result
        # --------------------------------------------------

        if invoice_id is None:

            logger.warning(
                "Invoice was not saved : %s",
                filename,
            )

            return None

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "Invoice Saved Successfully"
        )

        logger.info(
            "Invoice ID : %s",
            invoice_id,
        )

        logger.info(
            "Filename : %s",
            filename,
        )

        logger.info(
            "Vendor : %s",
            document.get(
                "vendor_name",
            ),
        )

        logger.info(
            "Invoice No : %s",
            document.get(
                "invoice_number",
            ),
        )

        logger.info(
            "Database Save Time : %.3f sec",
            elapsed,
        )

        return int(
            invoice_id
        )

    # ======================================================
    # PROCESS + SAVE
    # ======================================================

    def process_and_save(
        self,
        filename: str,
        document_text: str,
    ) -> dict[str, Any]:
        """
        Complete invoice pipeline.
        """

        start_time = time.perf_counter()

        logger.info(
            "=" * 60
        )

        logger.info(
            "Invoice Processing Started : %s",
            filename,
        )

        try:

            # ----------------------------------------------
            # AI extraction
            # ----------------------------------------------

            document = self.process_document(
                filename,
                document_text,
            )

            # ----------------------------------------------
            # Database persistence
            # ----------------------------------------------

            invoice_id = self.save_document(
                filename,
                document,
            )

            elapsed = (
                time.perf_counter()
                - start_time
            )

            # ----------------------------------------------
            # Summary
            # ----------------------------------------------

            logger.info(
                "Invoice Summary | "
                "Vendor=%s | "
                "InvoiceNo=%s | "
                "Date=%s | "
                "GrandTotal=%s | "
                "Currency=%s",
                document.get(
                    "vendor_name"
                ),
                document.get(
                    "invoice_number"
                ),
                document.get(
                    "invoice_date"
                ),
                document.get(
                    "grand_total"
                ),
                document.get(
                    "currency"
                ),
            )

            logger.info(
                "Invoice Processing Completed : %s",
                filename,
            )

            logger.info(
                "Total Processing Time : %.3f sec",
                elapsed,
            )

            logger.info(
                "=" * 60
            )

            return {
                "success": True,
                "invoice_id": invoice_id,
                "document": document,
            }

        except Exception:

            elapsed = (
                time.perf_counter()
                - start_time
            )

            logger.exception(
                "Invoice Processing Failed : %s",
                filename,
            )

            logger.error(
                "Failed After : %.3f sec",
                elapsed,
            )

            logger.info(
                "=" * 60
            )

            raise


# ==========================================================
# SERVICE INSTANCE
# ==========================================================

invoice_service = InvoiceService()


## ==========================================================
# BACKWARD-COMPATIBLE FUNCTIONS
# ==========================================================

def validate_document(
    document: Any,
) -> dict[str, str]:

    return invoice_service.validate_document(
        document
    )


def check_required_fields(
    document: dict[str, str],
) -> list[str]:

    return invoice_service.check_required_fields(
        document
    )


# ==========================================================
# BACKWARD-COMPATIBLE AI EXTRACTION
# ==========================================================

def extract_invoice_information(
    document_text: str,
) -> dict[str, str]:
    """
    Backward-compatible invoice extraction API.

    Delegates to the existing DeepSeek extraction pipeline.
    """

    if not isinstance(
        document_text,
        str,
    ):
        raise TypeError(
            "document_text must be a string."
        )

    document_text = document_text.strip()

    if not document_text:
        raise ValueError(
            "document_text cannot be empty."
        )

    # Existing AI extraction pipeline
    document = extract_document(
        document_text
    )

    # Existing service normalization
    document = invoice_service.validate_document(
        document
    )

    return document


def process_document(
    filename: str,
    document_text: str,
) -> dict[str, str]:

    return invoice_service.process_document(
        filename,
        document_text,
    )


def save_document(
    filename: str,
    document: dict[str, Any],
) -> int | None:

    return invoice_service.save_document(
        filename,
        document,
    )


def process_and_save(
    filename: str,
    document_text: str,
) -> dict[str, Any]:

    return invoice_service.process_and_save(
        filename,
        document_text,
    )
# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [
    "SERVICE_NAME",
    "SERVICE_VERSION",
    "REQUIRED_FIELDS",
    "DEFAULT_DOCUMENT",
    "InvoiceService",
    "invoice_service",
    "extract_invoice_information",
    "validate_document",
    "check_required_fields",
    "process_document",
    "save_document",
    "process_and_save",
]
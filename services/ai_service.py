from logger import logger
from fastapi import HTTPException

# Existing AI Extraction Module
from invoice_service import (
    extract_invoice_information,
)


class AIService:
    """
    AI Invoice Extraction Service
    """

    def extract_invoice(self, raw_text: str) -> dict:
        """
        Extract invoice fields from OCR text.
        """

        if not raw_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Empty OCR text."
            )

        try:

            logger.info("Running AI Invoice Extraction...")

            invoice = extract_invoice_information(raw_text)

            if invoice is None:
                raise ValueError("AI returned None")

            logger.info("AI Extraction Completed")

            return invoice

        except Exception as e:

            logger.exception(e)

            raise HTTPException(
                status_code=500,
                detail="AI Extraction Failed"
            )
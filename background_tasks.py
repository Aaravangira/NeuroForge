"""
==========================================
BACKGROUND TASKS
AI Invoice Extractor
==========================================
"""

import os

from config import (
    EXPORT_FOLDER,
    EXCEL_FILENAME
)

from logger import logger

from invoice_service import process_and_save

from excel_export import export_to_excel


# ==========================================
# PROCESS INVOICE
# ==========================================

def process_invoice(
    filename: str,
    document_text: str
):

    try:

        logger.info(f"Background Processing Started : {filename}")

        # -----------------------------
        # AI + Database
        # -----------------------------

        result = process_and_save(
            filename,
            document_text
        )

        document = result["document"]

        # -----------------------------
        # Excel Export
        # -----------------------------

        excel_path = os.path.join(
            EXPORT_FOLDER,
            EXCEL_FILENAME
        )

        export_to_excel(
            document,
            excel_path
        )

        logger.info(
            f"Background Processing Completed : {filename}"
        )

    except Exception:

        logger.exception(
            "Background Processing Failed"
        )
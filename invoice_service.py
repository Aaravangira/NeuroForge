"""
==========================================
INVOICE SERVICE
AI Invoice Extractor
==========================================
"""

from copy import deepcopy

from ai_engine import extract_document
from database import save_invoice
from logger import logger


# ==========================================
# DEFAULT DATA
# ==========================================

DEFAULT_DOCUMENT = {

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

    "filename": ""

}


# ==========================================
# VALIDATE DOCUMENT
# ==========================================

def validate_document(document: dict):

    output = deepcopy(DEFAULT_DOCUMENT)

    if isinstance(document, dict):

        output.update(document)

    return output


# ==========================================
# PROCESS DOCUMENT
# ==========================================

def process_document(

    filename: str,

    document_text: str

):

    logger.info(f"Processing : {filename}")

    document = extract_document(document_text)

    document = validate_document(document)

    document["filename"] = filename

    document["raw_text"] = document_text

    logger.info("AI Processing Completed")

    return document


# ==========================================
# SAVE DOCUMENT
# ==========================================

def save_document(

    filename: str,

    document: dict

):

    try:

        document = validate_document(document)

        document["filename"] = filename

        invoice_id = save_invoice(document)

        logger.info(

            f"Invoice Saved Successfully : {invoice_id}"

        )

        return invoice_id

    except Exception:

        logger.exception(

            "Database Save Failed"

        )

        raise


# ==========================================
# PROCESS + SAVE
# ==========================================

def process_and_save(

    filename: str,

    document_text: str

):

    document = process_document(

        filename,

        document_text

    )

    invoice_id = save_document(

        filename,

        document

    )

    return {

        "invoice_id": invoice_id,

        "document": document

    }
"""
==========================================================
OCR ENGINE
AI Invoice Extractor
Production Version
==========================================================
"""

from __future__ import annotations

from pathlib import Path

import fitz
from paddleocr import PaddleOCR

from config import (
    ALLOWED_EXTENSIONS,
    OCR_DPI,
    OCR_LANGUAGE,
    OCR_USE_DOC_ORIENTATION_CLASSIFY,
    OCR_USE_DOC_UNWARPING,
    OCR_USE_TEXTLINE_ORIENTATION,
    TEMP_FOLDER,
)

from logger import logger


# ==========================================================
# SERVICE INFORMATION
# ==========================================================

SERVICE_NAME = "OCR Engine"
SERVICE_VERSION = "2.0.0"


# ==========================================================
# OCR ENGINE INITIALIZATION
# ==========================================================

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
    lang=OCR_LANGUAGE,
)


# ==========================================================
# IMAGE OCR
# ==========================================================

def image_to_text(
    image_path: str | Path,
) -> str:
    """
    Extract text from an image using PaddleOCR.
    """

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    extension = image_path.suffix.lower()

    if extension == ".pdf":
        raise ValueError(
            "image_to_text() expects an image file, "
            "not a PDF."
        )

    if extension not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {extension}"
        )

    logger.info(
        "OCR started: %s",
        image_path.name,
    )

    try:

        result = ocr.predict(
            str(image_path)
        )

        text_parts: list[str] = []

        for page in result:

            # ------------------------------------------
            # PaddleOCR dictionary-style response
            # ------------------------------------------

            if isinstance(page, dict):

                rec_texts = page.get(
                    "rec_texts",
                    [],
                )

            # ------------------------------------------
            # PaddleOCR object-style response
            # ------------------------------------------

            else:

                rec_texts = getattr(
                    page,
                    "rec_texts",
                    [],
                )

            if not rec_texts:
                continue

            for line in rec_texts:

                if line is None:
                    continue

                text = str(
                    line
                ).strip()

                if text:
                    text_parts.append(
                        text
                    )

        extracted_text = "\n".join(
            text_parts
        ).strip()

        logger.info(
            "OCR completed: %s | Characters=%d",
            image_path.name,
            len(extracted_text),
        )

        return extracted_text

    except Exception:

        logger.exception(
            "OCR failed: %s",
            image_path.name,
        )

        raise


# ==========================================================
# PDF OCR
# ==========================================================

def pdf_to_text_with_ocr(
    pdf_path: str | Path,
) -> str:
    """
    Convert PDF pages to temporary images and
    extract text with PaddleOCR.

    Production-safe behavior:
    - Open PDF once.
    - Capture page count while document is open.
    - Process pages sequentially.
    - Delete each temporary image immediately.
    - Close PDF exactly once.
    - Never access the closed document.
    """

    pdf_path = Path(pdf_path)

    # ------------------------------------------------------
    # Validate PDF
    # ------------------------------------------------------

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "pdf_to_text_with_ocr() expects a PDF file."
        )

    # ------------------------------------------------------
    # Prepare temporary directory
    # ------------------------------------------------------

    TEMP_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    text_parts: list[str] = []

    logger.info(
        "PDF OCR started: %s",
        pdf_path.name,
    )

    document = None
    page_count = 0

    try:
        # --------------------------------------------------
        # Open PDF
        # --------------------------------------------------

        document = fitz.open(
            str(pdf_path)
        )

        # IMPORTANT:
        # Read page count BEFORE document.close().
        page_count = document.page_count

        logger.info(
            "PDF opened successfully: %s | Pages=%d",
            pdf_path.name,
            page_count,
        )

        # --------------------------------------------------
        # Process pages
        # --------------------------------------------------

        for page_number in range(
            page_count
        ):

            image_path = (
                TEMP_FOLDER
                / (
                    f"{pdf_path.stem}"
                    f"_page_{page_number + 1}.png"
                )
            )

            try:
                # ------------------------------------------
                # Load page
                # ------------------------------------------

                page = document.load_page(
                    page_number
                )

                # ------------------------------------------
                # Render page
                # ------------------------------------------

                pixmap = page.get_pixmap(
                    dpi=OCR_DPI,
                    alpha=False,
                )

                pixmap.save(
                    str(image_path)
                )

                logger.info(
                    "PDF page rendered: %s | Page=%d/%d",
                    pdf_path.name,
                    page_number + 1,
                    page_count,
                )

                # ------------------------------------------
                # OCR
                # ------------------------------------------

                page_text = image_to_text(
                    image_path
                )

                if page_text:
                    text_parts.append(
                        page_text
                    )

            finally:
                # ------------------------------------------
                # Remove temporary OCR image
                # ------------------------------------------

                if image_path.exists():

                    try:
                        image_path.unlink()

                    except OSError:

                        logger.warning(
                            "Unable to remove temporary OCR image: %s",
                            image_path,
                        )

        # --------------------------------------------------
        # Build final OCR text
        # --------------------------------------------------

        extracted_text = "\n".join(
            text_parts
        ).strip()

        logger.info(
            "PDF OCR completed: %s | Pages=%d | Characters=%d",
            pdf_path.name,
            page_count,
            len(extracted_text),
        )

        return extracted_text

    except Exception:

        logger.exception(
            "PDF OCR failed: %s",
            pdf_path.name,
        )

        raise

    finally:
        # --------------------------------------------------
        # Close PDF
        # --------------------------------------------------

        if document is not None:

            try:
                document.close()

            except Exception:

                logger.exception(
                    "Failed to close PDF document: %s",
                    pdf_path.name,
                )
                # ==========================================================
# HEALTH
# ==========================================================

def health() -> dict[str, object]:
    """
    Return OCR engine health information.
    """

    return {
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "engine": "paddleocr",
        "language": OCR_LANGUAGE,
        "dpi": OCR_DPI,
        "orientation_classification": (
            OCR_USE_DOC_ORIENTATION_CLASSIFY
        ),
        "document_unwarping": (
            OCR_USE_DOC_UNWARPING
        ),
        "textline_orientation": (
            OCR_USE_TEXTLINE_ORIENTATION
        ),
    }


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [
    "SERVICE_NAME",
    "SERVICE_VERSION",
    "ocr",
    "image_to_text",
    "pdf_to_text_with_ocr",
    "health",
]
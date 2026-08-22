from pathlib import Path

import fitz

from logger import logger
from ocr_engine import (
    pdf_to_text_with_ocr,
    image_to_text,
)


class OCRService:
    """
    OCR Service
    Responsible for extracting text from
    PDF and Image documents.
    """

    def extract_text(self, filepath: Path) -> str:

        extension = filepath.suffix.lower()

        if extension == ".pdf":
            return self.extract_pdf(filepath)

        return self.extract_image(filepath)

    # --------------------------------------------------

    def extract_pdf(self, filepath: Path) -> str:

        logger.info(f"Reading PDF : {filepath.name}")

        text = self.read_native_pdf(filepath)

        if text.strip():

            logger.info("Native PDF text found.")

            return text

        logger.info("Running OCR...")

        return pdf_to_text_with_ocr(str(filepath))

    # --------------------------------------------------

    def extract_image(self, filepath: Path) -> str:

        logger.info(f"Reading Image : {filepath.name}")

        return image_to_text(str(filepath))

    # --------------------------------------------------

    def read_native_pdf(self, filepath: Path) -> str:

        document = fitz.open(filepath)

        try:

            text = ""

            for page in document:
                text += page.get_text()

            return text

        finally:
            document.close()
"""
==========================================
OCR ENGINE
AI Invoice Extractor
==========================================
"""

import os
import fitz
import pytesseract

from PIL import Image

from config import TESSERACT_CMD
from logger import logger

# ==========================================
# Configure Tesseract
# ==========================================

if TESSERACT_CMD:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


# ==========================================
# OCR CONFIGURATION
# ==========================================

OCR_LANG = "eng"

OCR_CONFIG = r"--oem 3 --psm 6"


# ==========================================
# IMAGE -> TEXT
# ==========================================

def image_to_text(image_path: str) -> str:

    try:

        image = Image.open(image_path)

        text = pytesseract.image_to_string(

            image,

            lang=OCR_LANG,

            config=OCR_CONFIG

        )

        logger.info(f"OCR Success : {image_path}")

        return text.strip()

    except Exception:

        logger.exception("Image OCR Failed")

        return ""


# ==========================================
# PDF TEXT
# ==========================================

def pdf_to_text(pdf_path: str) -> str:

    text = ""

    try:

        pdf = fitz.open(pdf_path)

        for page in pdf:

            text += page.get_text()

        pdf.close()

        return text.strip()

    except Exception:

        logger.exception("PDF Text Extraction Failed")

        return ""


# ==========================================
# PDF OCR
# ==========================================

def pdf_to_text_with_ocr(pdf_path: str) -> str:

    complete_text = ""

    try:

        pdf = fitz.open(pdf_path)

        for page_number in range(len(pdf)):

            page = pdf.load_page(page_number)

            pix = page.get_pixmap(dpi=300)

            temp_image = f"page_{page_number}.png"

            pix.save(temp_image)

            try:

                image = Image.open(temp_image)

                text = pytesseract.image_to_string(

                    image,

                    lang=OCR_LANG,

                    config=OCR_CONFIG

                )

                complete_text += text + "\n"

            finally:

                if os.path.exists(temp_image):
                    os.remove(temp_image)

        pdf.close()

        logger.info("PDF OCR Completed")

        return complete_text.strip()

    except Exception:

        logger.exception("PDF OCR Failed")

        return ""


# ==========================================
# SMART EXTRACTION
# ==========================================

def extract_text(file_path: str) -> str:

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":

        text = pdf_to_text(file_path)

        if len(text.strip()) > 30:

            logger.info("Digital PDF Detected")

            return text

        logger.info("Scanned PDF Detected")

        return pdf_to_text_with_ocr(file_path)

    if extension in [

        ".png",

        ".jpg",

        ".jpeg",

        ".bmp",

        ".tiff"

    ]:

        return image_to_text(file_path)

    logger.warning(f"Unsupported File : {file_path}")

    return ""
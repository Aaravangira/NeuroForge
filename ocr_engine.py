"""
==========================================================
OCR ENGINE
AI Invoice Extractor
Layout-Preserving Production Version
==========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
SERVICE_VERSION = "3.0.0"


# ==========================================================
# OCR INITIALIZATION
# ==========================================================

ocr = PaddleOCR(
    text_detection_model_name="PP-OCRv5_mobile_det",
    text_recognition_model_name="PP-OCRv5_mobile_rec",
    use_doc_orientation_classify=OCR_USE_DOC_ORIENTATION_CLASSIFY,
    use_doc_unwarping=OCR_USE_DOC_UNWARPING,
    use_textline_orientation=OCR_USE_TEXTLINE_ORIENTATION,
    lang=OCR_LANGUAGE,
)


# ==========================================================
# HELPERS
# ==========================================================

def _to_list(value: Any) -> list:
    """Convert PaddleOCR/numpy values safely to Python lists."""

    if value is None:
        return []

    if hasattr(value, "tolist"):
        try:
            return value.tolist()
        except Exception:
            pass

    if isinstance(value, list):
        return value

    try:
        return list(value)
    except Exception:
        return []


def _get_result_value(page: Any, key: str) -> Any:
    """Read a value from PaddleOCR dictionary/object result."""

    if isinstance(page, dict):
        return page.get(key)

    try:
        return getattr(page, key, None)
    except Exception:
        return None


def _box_to_rect(box: Any) -> tuple[float, float, float, float] | None:
    """
    Convert OCR box/polygon into:
        x_min, y_min, x_max, y_max
    """

    try:
        points = _to_list(box)

        # Polygon:
        # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
        if (
            points
            and isinstance(points[0], (list, tuple))
            and len(points[0]) >= 2
        ):
            xs = [float(point[0]) for point in points]
            ys = [float(point[1]) for point in points]

            return (
                min(xs),
                min(ys),
                max(xs),
                max(ys),
            )

        # Rectangle:
        # [x1, y1, x2, y2]
        if len(points) >= 4:
            return (
                float(points[0]),
                float(points[1]),
                float(points[2]),
                float(points[3]),
            )

    except Exception:
        pass

    return None


def _reconstruct_layout(
    texts: list[Any],
    boxes: list[Any],
) -> str:
    """
    Reconstruct OCR text using bounding-box coordinates.

    The important difference from the old implementation is:
    text position is preserved instead of simply joining
    recognized strings.
    """

    items: list[dict[str, float | str]] = []

    for index, text in enumerate(texts):

        if text is None:
            continue

        text = str(text).strip()

        if not text:
            continue

        if index >= len(boxes):
            continue

        rect = _box_to_rect(boxes[index])

        if rect is None:
            continue

        x1, y1, x2, y2 = rect

        items.append(
            {
                "text": text,
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "center_y": (y1 + y2) / 2.0,
                "height": max(1.0, y2 - y1),
            }
        )

    if not items:
        # Fallback if bounding boxes are unavailable.
        return "\n".join(
            str(text).strip()
            for text in texts
            if text is not None and str(text).strip()
        ).strip()

    # ------------------------------------------------------
    # Sort approximately top-to-bottom first.
    # ------------------------------------------------------

    items.sort(
        key=lambda item: (
            float(item["center_y"]),
            float(item["x1"]),
        )
    )

    # ------------------------------------------------------
    # Group OCR elements into visual lines.
    # ------------------------------------------------------

    lines: list[list[dict[str, float | str]]] = []

    for item in items:

        center_y = float(item["center_y"])
        height = float(item["height"])

        placed = False

        for line in reversed(lines):

            line_center_y = sum(
                float(part["center_y"])
                for part in line
            ) / len(line)

            average_height = sum(
                float(part["height"])
                for part in line
            ) / len(line)

            tolerance = max(
                average_height * 0.55,
                height * 0.55,
                5.0,
            )

            if abs(center_y - line_center_y) <= tolerance:
                line.append(item)
                placed = True
                break

        if not placed:
            lines.append([item])

    # ------------------------------------------------------
    # Sort each line from left to right.
    # ------------------------------------------------------

    for line in lines:
        line.sort(
            key=lambda item: float(item["x1"])
        )

    # ------------------------------------------------------
    # Reconstruct horizontal spacing.
    # ------------------------------------------------------

    output_lines: list[str] = []

    for line in lines:

        if not line:
            continue

        # Estimate average character width.
        total_width = sum(
            float(item["x2"]) - float(item["x1"])
            for item in line
        )

        total_chars = sum(
            max(
                1,
                len(str(item["text"]))
            )
            for item in line
        )

        average_char_width = max(
            total_width / total_chars,
            3.0,
        )

        output = ""
        current_x = 0.0

        for item in line:

            text = str(item["text"])
            x1 = float(item["x1"])

            if current_x > 0:

                gap = x1 - current_x

                spaces = max(
                    1,
                    min(
                        30,
                        round(
                            gap / average_char_width
                        ),
                    ),
                )

                output += " " * spaces

            output += text

            current_x = float(item["x2"])

        output_lines.append(
            output.rstrip()
        )

    return "\n".join(
        line
        for line in output_lines
        if line.strip()
    ).strip()


# ==========================================================
# IMAGE OCR
# ==========================================================

def image_to_text(
    image_path: str | Path,
) -> str:

    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(
            f"Image file not found: {image_path}"
        )

    if image_path.suffix.lower() == ".pdf":
        raise ValueError(
            "image_to_text() expects an image, not PDF."
        )

    if image_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported image format: {image_path.suffix}"
        )

    logger.info(
        "Layout-aware OCR started: %s",
        image_path.name,
    )

    try:

        result = ocr.predict(
            str(image_path)
        )

        page_texts: list[str] = []

        for page in result:

            rec_texts = _to_list(
                _get_result_value(
                    page,
                    "rec_texts",
                )
            )

            # PaddleOCR normally exposes rec_boxes.
            rec_boxes = _to_list(
                _get_result_value(
                    page,
                    "rec_boxes",
                )
            )

            # Some PaddleOCR versions/results may expose
            # rec_polys instead.
            if not rec_boxes:

                rec_boxes = _to_list(
                    _get_result_value(
                        page,
                        "rec_polys",
                    )
                )

            page_text = _reconstruct_layout(
                rec_texts,
                rec_boxes,
            )

            if page_text:
                page_texts.append(
                    page_text
                )

        extracted_text = (
            "\n\n".join(page_texts)
            .strip()
        )

        logger.info(
            "Layout-aware OCR completed: %s | Characters=%d",
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

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(
            f"PDF file not found: {pdf_path}"
        )

    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError(
            "pdf_to_text_with_ocr() expects a PDF."
        )

    TEMP_FOLDER.mkdir(
        parents=True,
        exist_ok=True,
    )

    text_parts: list[str] = []

    logger.info(
        "PDF layout-aware OCR started: %s",
        pdf_path.name,
    )

    document = None

    try:

        document = fitz.open(
            str(pdf_path)
        )

        page_count = document.page_count

        logger.info(
            "PDF opened: %s | Pages=%d",
            pdf_path.name,
            page_count,
        )

        for page_number in range(page_count):

            image_path = (
                TEMP_FOLDER
                / (
                    f"{pdf_path.stem}"
                    f"_page_{page_number + 1}.png"
                )
            )

            try:

                page = document.load_page(
                    page_number
                )

                pixmap = page.get_pixmap(
                    dpi=OCR_DPI,
                    alpha=False,
                )

                pixmap.save(
                    str(image_path)
                )

                logger.info(
                    "Rendered page %d/%d",
                    page_number + 1,
                    page_count,
                )

                page_text = image_to_text(
                    image_path
                )

                if page_text:

                    text_parts.append(
                        f"========== PAGE {page_number + 1} ==========\n"
                        f"{page_text}"
                    )

            finally:

                if image_path.exists():

                    try:
                        image_path.unlink()

                    except OSError:

                        logger.warning(
                            "Unable to remove temporary image: %s",
                            image_path,
                        )

        extracted_text = (
            "\n\n".join(text_parts)
            .strip()
        )

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

        if document is not None:

            try:
                document.close()

            except Exception:

                logger.exception(
                    "Failed to close PDF: %s",
                    pdf_path.name,
                )


# ==========================================================
# HEALTH
# ==========================================================

def health() -> dict[str, object]:

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
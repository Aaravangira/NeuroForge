"""
==========================================================
UPLOAD SERVICE
AI Invoice Extractor
Production Version
==========================================================
"""

from __future__ import annotations

from pathlib import Path
import shutil
import uuid

from fastapi import (
    HTTPException,
    UploadFile,
)

# ==========================================================
# LOCAL IMPORTS
# ==========================================================

from logger import logger

from config import (
    UPLOAD_FOLDER,
    EXPORT_FOLDER,
    EXCEL_FILENAME,
    ALLOWED_EXTENSIONS,
    SUPPORTED_MIME_TYPES,
    MAX_UPLOAD_SIZE,
)

from ocr_engine import (
    pdf_to_text_with_ocr,
    image_to_text,
)

from invoice_service import (
    extract_invoice_information,
)

from excel_export import (
    export_to_excel,
)

from database import (
    save_invoice,
)


# ==========================================================
# UPLOAD SERVICE
# ==========================================================

class UploadService:
    """
    Handles the complete invoice upload pipeline:

        Validate
            ↓
        Save file
            ↓
        OCR
            ↓
        AI extraction
            ↓
        Database save
            ↓
        Excel export
    """

    # ======================================================
    # MAIN PROCESSING PIPELINE
    # ======================================================

    async def process_invoice(
        self,
        file: UploadFile,
    ):
        """
        Upload and process a single invoice.

        Background processing is intentionally not used here.
        The invoice is processed exactly once.
        """

        # --------------------------------------------------
        # Validate input
        # --------------------------------------------------

        self.validate_file(file)

        # --------------------------------------------------
        # Save original file
        # --------------------------------------------------

        filepath = self.save_file(file)

        try:

            # ----------------------------------------------
            # OCR
            # ----------------------------------------------

            raw_text = self.extract_text(
                filepath
            )

            if not raw_text or not raw_text.strip():
                raise HTTPException(
                    status_code=422,
                    detail=(
                        "Unable to extract text "
                        "from document."
                    ),
                )

            # ----------------------------------------------
            # AI EXTRACTION
            # ----------------------------------------------

            invoice = extract_invoice_information(
                raw_text
            )

            if not invoice:
                raise HTTPException(
                    status_code=422,
                    detail="Invoice extraction failed.",
                )

            # ----------------------------------------------
            # DATABASE SAVE
            # ----------------------------------------------

            invoice_id = save_invoice(
                invoice,
                filepath.name,
                raw_text,
            )

            invoice["invoice_id"] = invoice_id

            # ----------------------------------------------
            # EXCEL EXPORT
            # ----------------------------------------------

            excel_file = self.export_excel(
                invoice
            )

            # ----------------------------------------------
            # SUCCESS
            # ----------------------------------------------

            logger.info(
                "Invoice processing completed successfully: %s",
                filepath.name,
            )

            return {
                "success": True,
                "invoice": invoice,
                "excel_file": str(
                    excel_file
                ),
            }

        except HTTPException:
            raise

        except Exception:
            logger.exception(
                "Invoice processing failed: %s",
                filepath.name,
            )
            raise

    # ======================================================
    # VALIDATE FILE
    # ======================================================

    def validate_file(
        self,
        file: UploadFile,
    ) -> None:
        """
        Validate uploaded file name and extension.
        """

        if file is None:
            raise HTTPException(
                status_code=400,
                detail="No file uploaded.",
            )

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="No file selected.",
            )

        filename = Path(
            file.filename
        ).name.strip()

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename.",
            )

        extension = Path(
            filename
        ).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported file format. "
                    f"Allowed: "
                    f"{', '.join(sorted(ALLOWED_EXTENSIONS))}"
                ),
            )

    # ======================================================
    # SAVE FILE
    # ======================================================

    def save_file(
        self,
        file: UploadFile,
    ) -> Path:
        """
        Save the original uploaded file.
        """

        filename = Path(
            file.filename
        ).name.strip()

        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Invalid filename.",
            )

        UPLOAD_FOLDER.mkdir(
            parents=True,
            exist_ok=True,
        )

        # Never trust the client filename for the stored path.
        # Preserve the original name in the database/response while
        # using a UUID-backed filename to prevent collisions/overwrites.
        stored_filename = f"{uuid.uuid4().hex}{Path(filename).suffix.lower()}"
        filepath = UPLOAD_FOLDER / stored_filename

        total_size = 0
        chunk_size = 1024 * 1024

        try:

            with open(
                filepath,
                "wb",
            ) as buffer:

                while True:
                    chunk = file.file.read(chunk_size)
                    if not chunk:
                        break

                    total_size += len(chunk)
                    if total_size > MAX_UPLOAD_SIZE:
                        buffer.close()
                        filepath.unlink(missing_ok=True)
                        raise HTTPException(
                            status_code=413,
                            detail=(
                                f"File too large. Maximum allowed size is "
                                f"{MAX_UPLOAD_SIZE} bytes."
                            ),
                        )

                    buffer.write(chunk)

        except OSError as exc:

            logger.exception(
                "Failed to save uploaded file: %s",
                filename,
            )

            raise HTTPException(
                status_code=500,
                detail="Failed to save uploaded file.",
            ) from exc

        finally:

            try:
                file.file.close()
            except Exception:
                logger.warning(
                    "Failed to close upload file: %s",
                    filename,
                )

        logger.info(
            "Uploaded : %s",
            filepath.name,
        )

        return filepath

    # ======================================================
    # EXTRACT TEXT
    # ======================================================

    def extract_text(
        self,
        filepath: Path,
    ) -> str:
        """
        Extract OCR text from PDF or image.
        """

        if not filepath.exists():
            raise FileNotFoundError(
                f"Uploaded file not found: {filepath}"
            )

        extension = (
            filepath.suffix.lower()
        )

        logger.info(
            "Starting text extraction: %s",
            filepath.name,
        )

        if extension == ".pdf":

            return pdf_to_text_with_ocr(
                str(filepath)
            )

        return image_to_text(
            str(filepath)
        )

    # ======================================================
    # EXPORT EXCEL
    # ======================================================

    def export_excel(
        self,
        invoice,
    ) -> Path:
        """
        Export extracted invoice to Excel.
        """

        EXPORT_FOLDER.mkdir(
            parents=True,
            exist_ok=True,
        )

        excel_path = (
            EXPORT_FOLDER
            / EXCEL_FILENAME
        )

        export_to_excel(
            invoice,
            excel_path,
        )

        logger.info(
            "Excel export completed: %s",
            excel_path,
        )

        return excel_path


# ==========================================================
# GLOBAL SERVICE INSTANCE
# ==========================================================

upload_service = UploadService()
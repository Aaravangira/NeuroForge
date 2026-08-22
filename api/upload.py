"""
==========================================================
UPLOAD API
AI Invoice Extractor
Production Version
==========================================================
"""

from __future__ import annotations

import traceback

from fastapi import (
    APIRouter,
    File,
    HTTPException,
    UploadFile,
)

from services.upload_service import (
    upload_service,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/upload",
    tags=["Upload"],
)


# ==========================================================
# UPLOAD INVOICE
# ==========================================================

@router.post("/")
async def upload_invoice(
    file: UploadFile = File(...),
):
    """
    Upload and process an invoice.
    """

    try:

        return await upload_service.process_invoice(
            file=file,
        )

    except HTTPException:
        raise

    except Exception as exc:

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                f"Invoice processing failed: "
                f"{type(exc).__name__}: {exc}"
            ),
        ) from exc
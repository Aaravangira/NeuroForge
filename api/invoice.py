"""
==========================================================
INVOICE API
AI Invoice Extractor
Production Version
==========================================================
"""

from __future__ import annotations

from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
    Query,
)

from repositories.repositories.invoice_repository import (
    invoice_repository,
)


# ==========================================================
# ROUTER
# ==========================================================

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"],
)


# ==========================================================
# GET SINGLE INVOICE
# ==========================================================

@router.get("/{invoice_id}")
def get_invoice(
    invoice_id: int,
) -> dict[str, Any]:
    """
    Get a single invoice by ID.
    """

    try:
        invoice = invoice_repository.get(
            invoice_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch invoice.",
        ) from exc

    if invoice is None:

        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_id} not found.",
        )

    return {
        "success": True,
        "data": invoice,
    }


# ==========================================================
# GET ALL INVOICES
# ==========================================================

@router.get("/")
def get_invoices(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
) -> dict[str, Any]:
    """
    Get invoices with a safe API response limit.
    """

    try:
        invoices = invoice_repository.get_all()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to fetch invoices.",
        ) from exc

    limited_invoices = invoices[:limit]

    return {
        "success": True,
        "count": len(limited_invoices),
        "data": limited_invoices,
    }


# ==========================================================
# SEARCH INVOICES
# ==========================================================

@router.get("/search/")
def search_invoices(
    q: str = Query(
        ...,
        min_length=1,
        max_length=255,
    ),
) -> dict[str, Any]:
    """
    Search invoices.
    """

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=400,
            detail="Search query cannot be empty.",
        )

    try:
        results = invoice_repository.search(
            query
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to search invoices.",
        ) from exc

    return {
        "success": True,
        "query": query,
        "count": len(results),
        "data": results,
    }


# ==========================================================
# DELETE INVOICE
# ==========================================================

@router.delete("/{invoice_id}")
def delete_invoice(
    invoice_id: int,
) -> dict[str, Any]:
    """
    Delete an invoice by ID.
    """

    try:
        deleted = invoice_repository.delete(
            invoice_id
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail="Failed to delete invoice.",
        ) from exc

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail=f"Invoice {invoice_id} not found.",
        )

    return {
        "success": True,
        "message": "Invoice deleted successfully.",
    }
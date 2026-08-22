"""
==========================================================
INVOICE REPOSITORY
AI Invoice Extractor
Production Version 1.0
==========================================================
"""

from __future__ import annotations

from typing import Any

from database import (
    delete_invoice_by_id,
    fetch_all_invoices,
    fetch_invoice,
    save_invoice,
    search_invoice_database,
)
from logger import logger


# ==========================================================
# REPOSITORY
# ==========================================================

class InvoiceRepository:
    """
    Repository abstraction for invoice persistence.

    The repository provides a stable interface to the
    service layer while database.py owns the current
    low-level persistence implementation.
    """

    def create(
        self,
        invoice: dict[str, Any],
        filename: str | None = None,
        raw_text: str | None = None,
    ) -> int:
        """
        Persist an invoice.
        """

        logger.info(
            "Saving invoice to database."
        )

        return save_invoice(
            invoice_data=invoice,
            filename=filename,
            raw_text=raw_text,
        )

    def get(
        self,
        invoice_id: int,
    ) -> dict[str, Any] | None:
        """
        Fetch a single invoice.
        """

        return fetch_invoice(
            invoice_id
        )

    def get_all(self) -> list[dict[str, Any]]:
        """
        Fetch all invoices.
        """

        return fetch_all_invoices()

    def search(
        self,
        keyword: str,
    ) -> list[dict[str, Any]]:
        """
        Search invoices.
        """

        return search_invoice_database(
            keyword
        )

    def delete(
        self,
        invoice_id: int,
    ) -> bool:
        """
        Delete an invoice.
        """

        return delete_invoice_by_id(
            invoice_id
        )


# ==========================================================
# SINGLE REPOSITORY INSTANCE
# ==========================================================

invoice_repository = InvoiceRepository()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "InvoiceRepository",
    "invoice_repository",
]
"""
==========================================================
AI INVOICE EXTRACTOR
Invoice Database Model
Production Version 1.0
==========================================================
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    Numeric,
    String,
)
from sqlalchemy.dialects.mysql import JSON

from database import Base


# ==========================================================
# MODEL INFORMATION
# ==========================================================

MODEL_NAME = "Invoice"
MODEL_VERSION = "1.0.0"
TABLE_NAME = "invoices"


# ==========================================================
# INVOICE MODEL
# ==========================================================

class Invoice(Base):
    """
    SQLAlchemy representation of the existing
    MySQL `invoices` table.
    """

    __tablename__ = TABLE_NAME

    # ======================================================
    # PRIMARY KEY
    # ======================================================

    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        nullable=False,
    )

    # ======================================================
    # SOURCE DOCUMENT
    # ======================================================

    filename = Column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # DOCUMENT INFORMATION
    # ======================================================

    document_number = Column(
        String(255),
        nullable=True,
    )

    document_date = Column(
        String(100),
        nullable=True,
    )

    document_type = Column(
        String(100),
        nullable=True,
    )

    # ======================================================
    # PARTIES
    # ======================================================

    vendor_name = Column(
        String(255),
        nullable=True,
    )

    buyer_name = Column(
        String(255),
        nullable=True,
    )

    # ======================================================
    # FINANCIAL INFORMATION
    # ======================================================

    grand_total = Column(
        Numeric(
            precision=12,
            scale=2,
        ),
        nullable=True,
    )

    currency = Column(
        String(20),
        nullable=True,
    )

    payment_method = Column(
        String(100),
        nullable=True,
    )

    # ======================================================
    # COMPLETE AI EXTRACTION
    # ======================================================

    json_data = Column(
        JSON,
        nullable=True,
    )

    # ======================================================
    # TIMESTAMP
    # ======================================================

    created_at = Column(
        DateTime,
        nullable=True,
    )

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:
        return (
            f"<Invoice("
            f"id={self.id}, "
            f"filename={self.filename!r}, "
            f"document_number="
            f"{self.document_number!r}, "
            f"vendor_name="
            f"{self.vendor_name!r}, "
            f"grand_total="
            f"{self.grand_total!r}"
            f")>"
        )

    # ======================================================
    # SERIALIZATION
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert database invoice to a
        JSON-compatible dictionary.
        """

        return {
            "id": self.id,
            "filename": self.filename,
            "document_number": self.document_number,
            "document_date": self.document_date,
            "document_type": self.document_type,
            "vendor_name": self.vendor_name,
            "buyer_name": self.buyer_name,
            "grand_total": (
                str(self.grand_total)
                if self.grand_total is not None
                else None
            ),
            "currency": self.currency,
            "payment_method": self.payment_method,
            "json_data": self.json_data,
            "created_at": (
                self.created_at.isoformat()
                if self.created_at
                else None
            ),
        }


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [
    "Invoice",
    "MODEL_NAME",
    "MODEL_VERSION",
    "TABLE_NAME",
]
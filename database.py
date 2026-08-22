"""
==========================================================
AI INVOICE EXTRACTOR
Production Database Manager
Version 4.0
==========================================================
"""

from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Callable, Generator, Optional, Type

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    inspect,
    text,
    create_engine,
    or_,
)
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    scoped_session,
    sessionmaker,
)

from config import (
    DATABASE_URL,
    DATABASE_ECHO,
    DATABASE_AUTOFLUSH,
    DATABASE_EXPIRE_ON_COMMIT,
    DB_POOL_SIZE,
    DB_MAX_OVERFLOW,
    DB_POOL_TIMEOUT,
    DB_POOL_RECYCLE,
    DB_POOL_PRE_PING,
)

from logger import logger


# ==========================================================
# SERVICE INFORMATION
# ==========================================================

SERVICE_NAME = "Database Manager"
SERVICE_VERSION = "4.0.0"

LOG_SEPARATOR = "=" * 70


# ==========================================================
# DATABASE ENGINE
# ==========================================================

def _create_engine() -> Engine:
    """
    Create the SQLAlchemy engine.

    Production features:
        - Connection pooling
        - Connection pre-ping
        - Pool recycling
        - Configurable pool size
        - Configurable overflow
        - SQL echo configuration
    """

    database_url = str(
        DATABASE_URL
    ).strip()

    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not configured."
        )

    engine_kwargs: dict[str, Any] = {
        "echo": DATABASE_ECHO,
        "future": True,
    }

    # ------------------------------------------------------
    # SQLite
    # ------------------------------------------------------

    if database_url.startswith(
        "sqlite"
    ):

        # SQLite does not use the same
        # production pool configuration
        # as MySQL/PostgreSQL.

        engine_kwargs[
            "connect_args"
        ] = {
            "check_same_thread": False,
        }

    # ------------------------------------------------------
    # MySQL / PostgreSQL / other pooled DB
    # ------------------------------------------------------

    else:

        engine_kwargs.update({

            "pool_size": DB_POOL_SIZE,

            "max_overflow":
                DB_MAX_OVERFLOW,

            "pool_timeout":
                DB_POOL_TIMEOUT,

            "pool_recycle":
                DB_POOL_RECYCLE,

            "pool_pre_ping":
                DB_POOL_PRE_PING,
        })

    engine = create_engine(
        database_url,
        **engine_kwargs,
    )

    return engine


ENGINE = _create_engine()


# ==========================================================
# SESSION FACTORY
# ==========================================================

SessionFactory = sessionmaker(
    bind=ENGINE,
    autoflush=DATABASE_AUTOFLUSH,
    expire_on_commit=DATABASE_EXPIRE_ON_COMMIT,
)


# ==========================================================
# THREAD-SAFE SESSION
# ==========================================================

SessionLocal = scoped_session(
    SessionFactory
)


# ==========================================================
# DECLARATIVE BASE
# ==========================================================

class Base(DeclarativeBase):
    """
    SQLAlchemy declarative base.
    """

    pass


# ==========================================================
# DATABASE INITIALIZATION LOG
# ==========================================================

logger.info(
    "%s v%s loaded",
    SERVICE_NAME,
    SERVICE_VERSION,
)

logger.info(
    "Database dialect : %s",
    ENGINE.dialect.name,
)

logger.info(
    "Database driver  : %s",
    ENGINE.dialect.driver,
)


# ==========================================================
# SESSION MANAGEMENT
# ==========================================================

def get_db() -> Generator[
    Session,
    None,
    None,
]:
    """
    FastAPI database dependency.

    Usage:

        db: Session = Depends(get_db)
    """

    db = SessionLocal()

    try:

        yield db

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ==========================================================
# CONTEXT MANAGER
# ==========================================================

@contextmanager
def get_db_session() -> Generator[
    Session,
    None,
    None,
]:
    """
    Backward-compatible transactional session context.

    Delegates to the single transaction implementation to avoid
    duplicated commit/rollback/close logic.
    """

    with transaction() as session:

        yield session


# ==========================================================
# TRANSACTION CONTEXT
# ==========================================================

@contextmanager
def transaction() -> Generator[
    Session,
    None,
    None,
]:
    """
    Transaction-safe session.

    Use when multiple database operations
    must succeed or fail together.

    Example:

        with transaction() as db:
            db.add(invoice)
            db.add(audit)
    """

    session = SessionLocal()

    try:

        yield session

        session.commit()

    except Exception:

        session.rollback()

        logger.exception(
            "Transaction rolled back."
        )

        raise

    finally:

        session.close()


# ==========================================================
# SESSION UTILITIES
# ==========================================================

def create_session() -> Session:
    """
    Create a new database session.
    """

    return SessionLocal()


def close_session(
    session: Optional[Session],
) -> None:
    """
    Safely close a database session.
    """

    if session is not None:

        session.close()


def commit_session(
    session: Session,
) -> None:
    """
    Commit current transaction.
    """

    try:

        session.commit()

    except Exception:

        session.rollback()

        logger.exception(
            "Database commit failed."
        )

        raise


def rollback_session(
    session: Session,
) -> None:
    """
    Roll back current transaction.
    """

    session.rollback()


def refresh_object(
    session: Session,
    instance: Any,
) -> None:
    """
    Refresh an SQLAlchemy object.
    """

    session.refresh(
        instance
    )


def flush_session(
    session: Session,
) -> None:
    """
    Flush pending changes without committing.
    """

    session.flush()


# ==========================================================
# SESSION INFORMATION
# ==========================================================

def session_info() -> dict[str, Any]:
    """
    Return session configuration.
    """

    return {

        "autoflush":
            DATABASE_AUTOFLUSH,

        "expire_on_commit":
            DATABASE_EXPIRE_ON_COMMIT,

    }


# ==========================================================
# BASE MODEL
# ==========================================================

class BaseModel(Base):
    """
    Base model inherited by application tables.

    Provides:

        - id
        - created_at
        - updated_at
        - is_active
        - is_deleted
        - serialization
        - soft delete
        - restore
    """

    __abstract__ = True

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    created_at = Column(
        DateTime,
        default=lambda:
            datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime,
        default=lambda:
            datetime.now(timezone.utc),
        onupdate=lambda:
            datetime.now(timezone.utc),
        nullable=False,
    )

    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
    )

    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ======================================================
    # PERSISTENCE
    # ======================================================

    def save(
        self,
        session: Session,
    ) -> "BaseModel":
        """
        Add object to current transaction.

        Important:
        This method does NOT commit.

        The caller controls the transaction.
        """

        session.add(self)

        session.flush()

        return self

    # ======================================================
    # UPDATE
    # ======================================================

    def update(
        self,
        session: Session,
        **kwargs: Any,
    ) -> "BaseModel":
        """
        Update allowed model attributes.

        Does not commit automatically.
        """

        for key, value in kwargs.items():

            if hasattr(
                self,
                key,
            ):

                setattr(
                    self,
                    key,
                    value,
                )

        session.flush()

        return self

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        session: Session,
    ) -> None:
        """
        Permanently delete object.

        Use carefully.
        """

        session.delete(self)

        session.flush()

    # ======================================================
    # SOFT DELETE
    # ======================================================

    def soft_delete(
        self,
        session: Session,
    ) -> "BaseModel":
        """
        Soft delete record.
        """

        self.is_deleted = True
        self.is_active = False

        session.flush()

        return self

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(
        self,
        session: Session,
    ) -> "BaseModel":
        """
        Restore soft-deleted record.
        """

        self.is_deleted = False
        self.is_active = True

        session.flush()

        return self

    # ======================================================
    # SERIALIZATION
    # ======================================================

    def to_dict(self) -> dict[str, Any]:
        """
        Convert model into dictionary.
        """

        return {
            column.name:
                getattr(
                    self,
                    column.name,
                )
            for column
            in self.__table__.columns
        }

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(self) -> str:

        return (
            f"<{self.__class__.__name__}"
            f"(id={self.id})>"
        )


# ==========================================================
# DATABASE MANAGER
# ==========================================================

class DatabaseManager:
    """
    Production database manager.

    Handles:

        - Sessions
        - CRUD
        - Transactions
        - Table creation
        - Health
        - Database lifecycle
    """

    def __init__(
        self,
        engine: Engine = ENGINE,
    ) -> None:

        self.engine = engine

        self.session_factory = (
            SessionLocal
        )

    # ======================================================
    # SESSION
    # ======================================================

    def get_session(self) -> Session:
        """
        Return a new scoped session.
        """

        return self.session_factory()

    # ======================================================
    # CREATE TABLES
    # ======================================================

    def create_tables(self) -> None:
        """
        Create all registered tables.
        """

        Base.metadata.create_all(
            bind=self.engine
        )

        logger.info(
            "Database tables initialized."
        )

    # ======================================================
    # DROP TABLES
    # ======================================================

    def drop_tables(self) -> None:
        """
        Drop all registered tables.

        WARNING:
        Development/testing only.
        """

        logger.warning(
            "Dropping all database tables."
        )

        Base.metadata.drop_all(
            bind=self.engine
        )

    # ======================================================
    # EXECUTE TRANSACTION
    # ======================================================

    def execute(
        self,
        callback: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """
        Execute callback inside transaction.
        """

        with transaction() as session:

            return callback(
                session,
                *args,
                **kwargs,
            )

    # ======================================================
    # SAVE
    # ======================================================

    def save(
        self,
        instance: BaseModel,
    ) -> BaseModel:
        """
        Save object transactionally.
        """

        with transaction() as session:

            session.add(instance)

            session.flush()

            session.refresh(
                instance
            )

            return instance

    # ======================================================
    # DELETE
    # ======================================================

    def delete(
        self,
        instance: BaseModel,
    ) -> None:
        """
        Permanently delete object.
        """

        with transaction() as session:

            session.delete(instance)

    # ======================================================
    # SOFT DELETE
    # ======================================================

    def soft_delete(
        self,
        instance: BaseModel,
    ) -> BaseModel:
        """
        Soft delete object.
        """

        with transaction() as session:

            instance.is_deleted = True
            instance.is_active = False

            session.flush()

            session.refresh(
                instance
            )

            return instance

    # ======================================================
    # RESTORE
    # ======================================================

    def restore(
        self,
        instance: BaseModel,
    ) -> BaseModel:
        """
        Restore object.
        """

        with transaction() as session:

            instance.is_deleted = False
            instance.is_active = True

            session.flush()

            session.refresh(
                instance
            )

            return instance

    # ======================================================
    # GET BY ID
    # ======================================================

    def get_by_id(
        self,
        model: Type[BaseModel],
        object_id: int,
    ) -> Optional[BaseModel]:
        """
        Get active record by primary key.
        """

        with get_db_session() as session:

            return session.get(
                model,
                object_id,
            )

    # ======================================================
    # GET ALL
    # ======================================================

    def get_all(
        self,
        model: Type[BaseModel],
        include_deleted: bool = False,
    ) -> list[BaseModel]:
        """
        Return records.

        By default soft-deleted records
        are excluded.
        """

        with get_db_session() as session:

            query = session.query(
                model
            )

            if not include_deleted:

                query = query.filter(
                    model.is_deleted.is_(False)
                )

            return query.all()

    # ======================================================
    # COUNT
    # ======================================================

    def count(
        self,
        model: Type[BaseModel],
        include_deleted: bool = False,
    ) -> int:
        """
        Count records.
        """

        with get_db_session() as session:

            query = session.query(
                model
            )

            if not include_deleted:

                query = query.filter(
                    model.is_deleted.is_(False)
                )

            return query.count()

    # ======================================================
    # INFO
    # ======================================================

    def info(self) -> dict[str, Any]:
        """
        Return safe database information.

        Credentials are never exposed.
        """

        return {

            "dialect":
                self.engine.dialect.name,

            "driver":
                self.engine.dialect.driver,

            "pool":
                self.engine.pool.__class__.__name__,

        }


# ==========================================================
# GLOBAL DATABASE MANAGER
# ==========================================================

db_manager = DatabaseManager()

# ==========================================================
# INVOICE PERSISTENCE
# ==========================================================

def save_invoice(
    invoice_data: dict[str, Any],
    filename: Optional[str] = None,
    raw_text: Optional[str] = None,
) -> int:
    """
    Save extracted invoice data into the existing
    MySQL `invoices` table.

    Compatible with:

        save_invoice(
            invoice,
            filepath.name,
            raw_text,
        )

    Returns:
        int: Newly created invoice ID.
    """

    if not isinstance(invoice_data, dict):
        raise TypeError(
            "invoice_data must be a dictionary."
        )

    # Import here to avoid circular import problems.
    from models.invoice_model import Invoice
        # ======================================================
    # FILENAME
    # ======================================================

    resolved_filename = (
        str(filename).strip()
        if filename is not None
        else str(
            invoice_data.get(
                "filename",
                ""
            )
        ).strip()
    )

    # ======================================================
    # DOCUMENT NUMBER
    # ======================================================

    document_number = (
        invoice_data.get("document_number")
        or invoice_data.get("invoice_number")
        or ""
    )

    document_number = str(
        document_number
    ).strip()

    # ======================================================
    # DOCUMENT DATE
    # ======================================================

    document_date = (
        invoice_data.get("document_date")
        or invoice_data.get("invoice_date")
        or ""
    )

    document_date = str(
        document_date
    ).strip()

    # ======================================================
    # DOCUMENT TYPE
    # ======================================================

    document_type = (
        invoice_data.get("document_type")
        or "invoice"
    )

    document_type = str(
        document_type
    ).strip()

    # ======================================================
    # VENDOR
    # ======================================================

    vendor_name = str(
        invoice_data.get(
            "vendor_name",
            ""
        ) or ""
    ).strip()

    # ======================================================
    # BUYER
    # ======================================================

    buyer_name = str(
        invoice_data.get(
            "buyer_name",
            ""
        ) or ""
    ).strip()

    # ======================================================
# PAYMENT METHOD
# ======================================================

    payment_method = str(
    invoice_data.get(
        "payment_method",
        ""
    ) or ""
    ).strip()
    # ======================================================
    # CURRENCY
    # ======================================================

    currency = str(
         invoice_data.get(
            "currency",
            ""
        ) or ""
    ).strip()

    # ======================================================
    # GRAND TOTAL
    # ======================================================

    grand_total = invoice_data.get(
        "grand_total"
    )

    if grand_total in (None, ""):

        grand_total = None

    else:

        from decimal import (
            Decimal,
            InvalidOperation,
        )

        try:

            cleaned_total = (
                str(grand_total)
                .replace(",", "")
                .replace("₹", "")
                .replace("$", "")
                .replace("€", "")
                .replace("£", "")
                .strip()
            )

            grand_total = Decimal(
                cleaned_total
            )

            if not grand_total.is_finite():
                raise ValueError(
                    "grand_total must be finite."
                )

            grand_total = grand_total.quantize(
                Decimal("0.01")
            )

        except (
            InvalidOperation,
            ValueError,
        ) as exc:

            raise ValueError(
                f"Invalid grand_total: "
                f"{grand_total}"
            ) from exc

    # ======================================================
    # RAW OCR TEXT
    # ======================================================

    resolved_raw_text = (
        raw_text
        if raw_text is not None
        else invoice_data.get(
            "raw_text",
            ""
        )
    )

    resolved_raw_text = str(
        resolved_raw_text or ""
    )

    # ======================================================
    # COMPLETE AI DATA
    # ======================================================

    json_data = dict(
        invoice_data
    )

    if resolved_raw_text:

        json_data["raw_text"] = (
            resolved_raw_text
        )

    # ======================================================
    # DATABASE TRANSACTION
    # ======================================================

    try:

        with transaction() as session:

            # ------------------------------------------------
            # DUPLICATE CHECK
            # ------------------------------------------------

            existing_invoice = None

            if (
                resolved_filename
                and document_number
            ):

                existing_invoice = (
                    session.query(Invoice)
                    .filter(
                        Invoice.filename
                        == resolved_filename,
                        Invoice.document_number
                        == document_number,
                    )
                    .first()
                )

            if existing_invoice is not None:

                logger.warning(
                    "Duplicate invoice detected."
                )

                logger.warning(
                    "Existing Invoice ID : %s",
                    existing_invoice.id,
                )

                return int(
                    existing_invoice.id
                )

            # ------------------------------------------------
            # CREATE MODEL
            # ------------------------------------------------

            invoice = Invoice(
                filename=(
                    resolved_filename
                    or None
                ),
                document_number=(
                    document_number
                    or None
                ),
                document_date=(
                    document_date
                    or None
                ),
                document_type=(
                    document_type
                    or None
                ),
                vendor_name=(
                    vendor_name
                    or None
                ),
                buyer_name=(
                    buyer_name
                    or None
                ),
                grand_total=grand_total,
                currency=(
                    currency
                    or None
                ),
                payment_method=(
                    payment_method
                    or None
                ),
                json_data=json_data,
                created_at=datetime.now(
                    timezone.utc
                ).replace(
                    tzinfo=None
                ),
            )

            # ------------------------------------------------
            # SAVE
            # ------------------------------------------------

            session.add(
                invoice
            )

            session.flush()

            invoice_id = invoice.id

        # ==================================================
        # SUCCESS LOGGING
        # ==================================================

        logger.info(
            "Invoice saved successfully."
        )

        logger.info(
            "Invoice ID : %s",
            invoice_id,
        )

        logger.info(
            "Filename : %s",
            resolved_filename,
        )

        logger.info(
            "Vendor : %s",
            vendor_name,
        )

        logger.info(
            "Document Number : %s",
            document_number,
        )

        logger.info(
            "Grand Total : %s",
            grand_total,
        )

        return int(
            invoice_id
        )

    except SQLAlchemyError:

        logger.exception(
            "Invoice database save failed."
        )

        raise

# ==========================================================
# INVOICE SERIALIZATION
# ==========================================================

def invoice_to_dict(
    invoice: Any,
) -> dict[str, Any]:
    """
    Convert an Invoice SQLAlchemy object into a JSON-safe dictionary.
    """

    if invoice is None:
        return {}

    return {
    "id": invoice.id,
    "filename": invoice.filename,
    "document_number": invoice.document_number,
    "document_date": invoice.document_date,
    "document_type": invoice.document_type,

    # Parties
    "vendor_name": invoice.vendor_name,
    "buyer_name": invoice.buyer_name,

    # Financial information
    "grand_total": (
        str(invoice.grand_total)
        if invoice.grand_total is not None
        else None
    ),
    "currency": invoice.currency,

    # Payment information
    "payment_method": invoice.payment_method,

    # Complete AI extraction
    "json_data": invoice.json_data,

    # Timestamp
    "created_at": (
        invoice.created_at.isoformat()
        if invoice.created_at is not None
        else None
    ),
}


# ==========================================================
# FETCH INVOICE
# ==========================================================

def fetch_invoice(
    invoice_id: int,
) -> Optional[dict[str, Any]]:
    """Fetch a single invoice by primary key."""

    if not isinstance(invoice_id, int):
        raise TypeError("invoice_id must be an integer.")

    if invoice_id <= 0:
        raise ValueError("invoice_id must be greater than zero.")

    from models.invoice_model import Invoice

    session = SessionLocal()

    try:
        invoice = (
            session.query(Invoice)
            .filter(Invoice.id == invoice_id)
            .first()
        )

        return invoice_to_dict(invoice) if invoice else None

    except SQLAlchemyError:
        logger.exception(
            "Failed to fetch invoice ID: %s",
            invoice_id,
        )
        raise

    finally:
        session.close()


# ==========================================================
# FETCH ALL INVOICES
# ==========================================================

def fetch_all_invoices() -> list[dict[str, Any]]:
    """Fetch all invoices ordered newest first."""

    from models.invoice_model import Invoice

    session = SessionLocal()

    try:
        invoices = (
            session.query(Invoice)
            .order_by(Invoice.id.desc())
            .all()
        )

        return [invoice_to_dict(invoice) for invoice in invoices]

    except SQLAlchemyError:
        logger.exception("Failed to fetch invoices.")
        raise

    finally:
        session.close()


# ==========================================================
# SEARCH INVOICES
# ==========================================================

def search_invoice_database(
    keyword: str,
) -> list[dict[str, Any]]:
    """Search invoice text fields using a case-insensitive match."""

    if not isinstance(keyword, str):
        raise TypeError("keyword must be a string.")

    keyword = keyword.strip()

    if not keyword:
        return []

    from models.invoice_model import Invoice

    pattern = f"%{keyword}%"
    session = SessionLocal()

    try:
        invoices = (
            session.query(Invoice)
            .filter(
                or_(
                    Invoice.filename.ilike(pattern),
                    Invoice.document_number.ilike(pattern),
                    Invoice.document_date.ilike(pattern),
                    Invoice.document_type.ilike(pattern),
                    Invoice.vendor_name.ilike(pattern),
                    Invoice.buyer_name.ilike(pattern),
                    Invoice.currency.ilike(pattern),
                )
            )
            .order_by(Invoice.id.desc())
            .all()
        )

        return [invoice_to_dict(invoice) for invoice in invoices]

    except SQLAlchemyError:
        logger.exception(
            "Invoice search failed. Keyword: %s",
            keyword,
        )
        raise

    finally:
        session.close()


# ==========================================================
# DELETE INVOICE
# ==========================================================

def delete_invoice_by_id(
    invoice_id: int,
) -> bool:
    """Permanently delete an invoice by primary key."""

    if not isinstance(invoice_id, int):
        raise TypeError("invoice_id must be an integer.")

    if invoice_id <= 0:
        raise ValueError("invoice_id must be greater than zero.")

    from models.invoice_model import Invoice

    try:
        with transaction() as session:
            invoice = (
                session.query(Invoice)
                .filter(Invoice.id == invoice_id)
                .first()
            )

            if invoice is None:
                logger.warning(
                    "Invoice not found for deletion: %s",
                    invoice_id,
                )
                return False

            session.delete(invoice)
            session.flush()

        logger.info(
            "Invoice deleted successfully. ID: %s",
            invoice_id,
        )
        return True

    except SQLAlchemyError:
        logger.exception(
            "Failed to delete invoice ID: %s",
            invoice_id,
        )
        raise


# ==========================================================
# DATABASE HEALTH
# ==========================================================

def check_database_health() -> dict[str, Any]:
    """
    Return detailed database connectivity health.
    """

    connected = test_connection()

    result: dict[str, Any] = {
        "status": "healthy" if connected else "unhealthy",
        "database": ENGINE.dialect.name,
        "driver": ENGINE.dialect.driver,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
    }

    if not connected:
        result["error"] = "Database connectivity check failed."

    return result


# ==========================================================
# CONNECTION TEST
# ==========================================================

def test_connection() -> bool:
    """
    Return True when database is reachable.
    """

    session = SessionLocal()

    try:

        session.execute(
            text("SELECT 1")
        )

        return True

    except SQLAlchemyError:

        logger.exception(
            "Database connection test failed."
        )

        return False

    finally:

        session.close()


# ==========================================================
# DATABASE VERSION
# ==========================================================

def get_database_version() -> str:
    """
    Return database server version.
    """

    session = SessionLocal()

    try:

        dialect = (
            ENGINE.dialect.name
        )

        if dialect == "mysql":

            result = session.execute(
                text(
                    "SELECT VERSION()"
                )
            )

            return str(
                result.scalar()
            )

        if dialect == "sqlite":

            result = session.execute(
                text(
                    "SELECT sqlite_version()"
                )
            )

            return str(
                result.scalar()
            )

        if dialect == "postgresql":

            result = session.execute(
                text(
                    "SELECT version()"
                )
            )

            return str(
                result.scalar()
            )

        return "Unknown"

    finally:

        session.close()


# ==========================================================
# DATABASE STATISTICS
# ==========================================================

def database_statistics() -> dict[str, Any]:
    """
    Return database configuration and pool statistics.
    """

    return {

        "database":
            ENGINE.dialect.name,

        "driver":
            ENGINE.dialect.driver,

        "pool_size":
            DB_POOL_SIZE,

        "max_overflow":
            DB_MAX_OVERFLOW,

        "pool_timeout":
            DB_POOL_TIMEOUT,

        "pool_recycle":
            DB_POOL_RECYCLE,

        "pool_pre_ping":
            DB_POOL_PRE_PING,

        "connected":
            test_connection(),

    }


# ==========================================================
# ENGINE INFORMATION
# ==========================================================

def engine_information() -> dict[str, Any]:
    """
    Return safe SQLAlchemy engine information.

    IMPORTANT:
    Passwords and connection credentials are
    intentionally excluded.
    """

    return {

        "dialect":
            ENGINE.dialect.name,

        "driver":
            ENGINE.dialect.driver,

        "echo":
            DATABASE_ECHO,

        "pool":
            ENGINE.pool.__class__.__name__,

    }


# ==========================================================
# POOL STATUS
# ==========================================================

def active_connections() -> str:
    """
    Return SQLAlchemy connection pool status.
    """

    try:

        return str(
            ENGINE.pool.status()
        )

    except Exception:

        return "Unavailable"


# ==========================================================
# CLOSE DATABASE
# ==========================================================

def close_database() -> None:
    """
    Gracefully close database resources.
    """

    logger.info(
        "Closing database..."
    )

    SessionLocal.remove()

    ENGINE.dispose()

    logger.info(
        "Database closed."
    )


# ==========================================================
# RECONNECT DATABASE
# ==========================================================

def reconnect_database() -> bool:
    """
    Dispose existing pool and test
    a fresh connection.
    """

    logger.info(
        "Reconnecting database..."
    )

    SessionLocal.remove()

    ENGINE.dispose()

    result = test_connection()

    if result:

        logger.info(
            "Database reconnected successfully."
        )

    else:

        logger.error(
            "Database reconnection failed."
        )

    return result


# ==========================================================
# DATABASE SUMMARY
# ==========================================================

def database_summary() -> dict[str, Any]:
    """
    Return complete operational database summary.
    """

    return {

        "healthy":
            test_connection(),

        "version":
            get_database_version(),

        "statistics":
            database_statistics(),

        "pool":
            active_connections(),

        "engine":
            engine_information(),

    }


# ==========================================================
# INITIALIZE DATABASE
# ==========================================================

def initialize_database() -> bool:
    """
    Initialize all registered database tables.
    """

    try:

        db_manager.create_tables()

        logger.info(
            "Database initialization successful."
        )

        return True

    except SQLAlchemyError:

        logger.exception(
            "Database initialization failed."
        )

        raise


# ==========================================================
# RESET DATABASE
# ==========================================================

def reset_database() -> None:
    """
    Drop and recreate all tables.

    WARNING:
    Development/testing only.
    Never expose this through production API.
    """

    logger.warning(
        "RESETTING DATABASE."
    )

    Base.metadata.drop_all(
        bind=ENGINE
    )

    Base.metadata.create_all(
        bind=ENGINE
    )

    logger.warning(
        "Database reset completed."
    )


# ==========================================================
# TABLE EXISTS
# ==========================================================

def table_exists(
    table_name: str,
) -> bool:
    """
    Check whether a table exists.
    """

    if not table_name:

        raise ValueError(
            "table_name cannot be empty."
        )

    inspector = inspect(
        ENGINE
    )

    return inspector.has_table(
        table_name
    )


# ==========================================================
# LIST TABLES
# ==========================================================

def list_tables() -> list[str]:
    """
    Return all database table names.
    """

    inspector = inspect(
        ENGINE
    )

    return inspector.get_table_names()


# ==========================================================
# DATABASE READY
# ==========================================================

def database_ready() -> bool:
    """
    Verify that the database is reachable
    and tables can be inspected.
    """

    try:

        if not test_connection():

            return False

        inspect(
            ENGINE
        ).get_table_names()

        return True

    except Exception:

        logger.exception(
            "Database readiness check failed."
        )

        return False


# ==========================================================
# STARTUP
# ==========================================================

def startup() -> dict[str, Any]:
    """
    Initialize database during application startup.
    """

    initialize_database()

    ready = database_ready()

    result = {

        "ready":
            ready,

        "tables":
            list_tables(),

        "database":
            ENGINE.dialect.name,

        "version":
            get_database_version(),

    }

    if ready:

        logger.info(
            "Database startup completed successfully."
        )

    else:

        logger.error(
            "Database startup completed but "
            "database is not ready."
        )

    return result


# ==========================================================
# SHUTDOWN
# ==========================================================

def shutdown() -> None:
    """
    Gracefully shutdown database.
    """

    close_database()


# ==========================================================
# STARTUP VALIDATION
# ==========================================================

def validate_database() -> bool:
    """
    Validate database connectivity.
    """

    if not test_connection():

        raise RuntimeError(
            "Database connection failed."
        )

    return True


# ==========================================================
# DATABASE STATUS
# ==========================================================

DATABASE_STATUS = {

    "initialized": False,

    "healthy": False,

}


def refresh_database_status() -> dict[str, bool]:
    """
    Refresh runtime database status.
    """

    global DATABASE_STATUS

    try:

        DATABASE_STATUS = {

            "initialized":
                True,

            "healthy":
                test_connection(),

        }

    except Exception:

        DATABASE_STATUS = {

            "initialized":
                False,

            "healthy":
                False,

        }

    return DATABASE_STATUS.copy()


# ==========================================================
# EXPORTS
# ==========================================================

__all__ = [

    # Engine
    "ENGINE",

    # SQLAlchemy
    "Base",

    "SessionFactory",

    "SessionLocal",

    # Session helpers
    "get_db",

    "get_db_session",

    "transaction",

    "create_session",

    "close_session",

    "commit_session",

    "rollback_session",

    "refresh_object",

    "flush_session",

    "session_info",

    # Base model
    "BaseModel",

    # Manager
    "DatabaseManager",

    "db_manager",

    # Invoice persistence
    "save_invoice",
    "invoice_to_dict",
    "fetch_invoice",
    "fetch_all_invoices",
    "search_invoice_database",
    "delete_invoice_by_id",

    # Health
    "check_database_health",

    "test_connection",

    "get_database_version",

    "database_statistics",

    "engine_information",

    "active_connections",

    "database_summary",

    # Lifecycle
    "initialize_database",

    "database_ready",

    "validate_database",

    "startup",

    "shutdown",

    "close_database",

    "reconnect_database",

    # Tables
    "table_exists",

    "list_tables",

    # Development
    "reset_database",

    # Status
    "DATABASE_STATUS",

    "refresh_database_status",
]
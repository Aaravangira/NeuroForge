"""
==========================================================
AI INVOICE EXTRACTOR
FastAPI Application
Production Configuration-Driven Version
==========================================================
"""

from __future__ import annotations

import os
import time

from contextlib import asynccontextmanager
from decimal import Decimal, InvalidOperation
from typing import Any

from fastapi import (
    FastAPI,
    HTTPException,
    Request,
)

from fastapi.exceptions import RequestValidationError

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
    JSONResponse,
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware


# ==========================================================
# CONFIGURATION
# ==========================================================

from config import (
    APP_NAME,
    APP_VERSION,
    EXPORT_FOLDER,
    EXCEL_FILENAME,
    STATIC_FOLDER,
    TEMPLATE_FOLDER,
)


# ==========================================================
# DATABASE
# ==========================================================

from database import (
    db_manager,
)


# ==========================================================
# LOGGER
# ==========================================================

from logger import logger


# ==========================================================
# REPOSITORIES
# ==========================================================

from repositories.repositories.invoice_repository import (
    invoice_repository,
)


# ==========================================================
# API ROUTERS
# ==========================================================

from api.upload import router as upload_router
from api.invoice import router as invoice_router


# ==========================================================
# MODELS
# ==========================================================

from models.invoice_model import Invoice
from models.user_model import User


# ==========================================================
# APPLICATION PATHS
# ==========================================================

STATIC_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)

TEMPLATE_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)

EXPORT_FOLDER.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# STARTUP / SHUTDOWN
# ==========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifecycle.

    Database initialization is performed once at startup.
    """

    logger.info("=" * 60)
    logger.info("AI Invoice Extractor Starting...")
    logger.info("=" * 60)

    try:

        db_manager.create_tables()

        logger.info(
            "Database initialization completed."
        )

        logger.info(
            "Application startup completed successfully."
        )

    except Exception:

        logger.exception(
            "Application startup failed."
        )

        raise

    yield

    logger.info(
        "AI Invoice Extractor shutting down."
    )

    try:

        from database import close_database

        close_database()

    except Exception:

        logger.exception(
            "Database shutdown failed."
        )


# ==========================================================
# FASTAPI APPLICATION
# ==========================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI-powered invoice extraction service.",
    lifespan=lifespan,
)


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        (
            "http://localhost:8000,"
            "http://127.0.0.1:8000,"
            "https://aiinvoiceextractor.live,"
            "https://www.aiinvoiceextractor.live"
        ),
    ).split(",")
    if origin.strip()
]


app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],

    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
    ],
)


# ==========================================================
# TRUSTED HOST CONFIGURATION
# ==========================================================

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        (
            "localhost,"
            "127.0.0.1,"
            "aiinvoiceextractor.live,"
            "www.aiinvoiceextractor.live"
        ),
    ).split(",")
    if host.strip()
]


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS,
)


# ==========================================================
# GZIP COMPRESSION
# ==========================================================

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,
)


# ==========================================================
# STATIC FILES
# ==========================================================

app.mount(
    "/static",
    StaticFiles(
        directory=str(STATIC_FOLDER)
    ),
    name="static",
)


# ==========================================================
# TEMPLATES
# ==========================================================

templates = Jinja2Templates(
    directory=str(TEMPLATE_FOLDER)
)


# ==========================================================
# API ROUTERS
# ==========================================================

app.include_router(
    upload_router
)

app.include_router(
    invoice_router
)


# ==========================================================
# DASHBOARD HELPERS
# ==========================================================

def _safe_decimal(
    value: Any,
) -> Decimal:
    """
    Convert a numeric value safely to Decimal.

    Invalid or empty values become zero.
    """

    if value is None:
        return Decimal("0")

    if isinstance(value, Decimal):
        return value

    try:

        text = (
            str(value)
            .strip()
            .replace(",", "")
        )

        if not text:
            return Decimal("0")

        return Decimal(text)

    except (
        InvalidOperation,
        ValueError,
        TypeError,
    ):

        return Decimal("0")


def get_dashboard_data() -> dict[str, Any]:
    """
    Build dashboard statistics from persisted invoices.

    Database access remains behind InvoiceRepository.
    """

    invoices = (
        invoice_repository.get_all()
    )

    total_invoices = len(
        invoices
    )

    total_amount = sum(
        (
            _safe_decimal(
                invoice.get(
                    "grand_total"
                )
            )
            for invoice in invoices
        ),
        Decimal("0"),
    )

    return {
        "total_invoices": total_invoices,

        "total_amount": float(
            total_amount
        ),
    }


# ==========================================================
# HOME PAGE
# ==========================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home(
    request: Request,
):
    """
    Main InvoiceAI application page.

    Uses the new modern upload interface.
    """

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
        },
    )


# ==========================================================
# DASHBOARD PAGE
# ==========================================================

@app.get(
    "/dashboard",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
):
    """
    Render the dashboard page.
    """

    dashboard_data = (
        get_dashboard_data()
    )

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "dashboard": dashboard_data,
        },
    )


# ==========================================================
# MODERN FRONTEND PAGE ROUTES
# ==========================================================

@app.get(
    "/upload-page",
    response_class=HTMLResponse,
)
async def upload_page(
    request: Request,
):
    """
    Render the invoice processing page.
    """

    return templates.TemplateResponse(
        "upload.html",
        {
            "request": request,
        },
    )


@app.get(
    "/history-page",
    response_class=HTMLResponse,
)
async def history_page(
    request: Request,
):
    """
    Render the invoice history page.
    """

    return templates.TemplateResponse(
        "history.html",
        {
            "request": request,
        },
    )


@app.get(
    "/reports",
    response_class=HTMLResponse,
)
async def reports_page(
    request: Request,
):
    """
    Render the analytics page.
    """

    return templates.TemplateResponse(
        "reports.html",
        {
            "request": request,
        },
    )


@app.get(
    "/settings",
    response_class=HTMLResponse,
)
async def settings_page(
    request: Request,
):
    """
    Render the application settings page.
    """

    return templates.TemplateResponse(
        "settings.html",
        {
            "request": request,
        },
    )


# ==========================================================
# DASHBOARD API
# ==========================================================

@app.get(
    "/api/dashboard"
)
async def dashboard_api() -> dict[str, Any]:
    """
    Return dashboard statistics as JSON.
    """

    return {
        "success": True,
        "data": get_dashboard_data(),
    }


# ==========================================================
# HISTORY API
# ==========================================================

@app.get(
    "/api/history"
)
async def history_api() -> dict[str, Any]:
    """
    Return invoice history as JSON.
    """

    invoices = (
        invoice_repository.get_all()
    )

    return {
        "success": True,
        "count": len(invoices),
        "data": invoices,
    }


# ==========================================================
# BACKWARD-COMPATIBLE HISTORY ROUTE
# ==========================================================

@app.get(
    "/history"
)
async def history_compatibility() -> dict[str, Any]:
    """
    Backward-compatible history endpoint.

    Existing frontend clients can continue
    using /history.
    """

    return await history_api()


# ==========================================================
# BACKWARD-COMPATIBLE DASHBOARD JSON ROUTE
# ==========================================================

@app.get(
    "/dashboard/data"
)
async def dashboard_data_compatibility() -> dict[str, Any]:
    """
    Backward-compatible dashboard data endpoint.
    """

    return await dashboard_api()


# ==========================================================
# EXCEL DOWNLOAD
# ==========================================================

@app.get(
    "/download/excel"
)
async def download_excel():
    """
    Download the configured Excel export.
    """

    excel_path = (
        EXPORT_FOLDER
        /
        EXCEL_FILENAME
    )

    if not excel_path.exists():

        return JSONResponse(
            status_code=404,

            content={
                "success": False,
                "message": (
                    "Excel file not found."
                ),
            },
        )

    return FileResponse(
        path=str(excel_path),

        filename=EXCEL_FILENAME,

        media_type=(
            "application/"
            "vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
    )


# ==========================================================
# BACKWARD-COMPATIBLE EXCEL DOWNLOAD
# ==========================================================

@app.get(
    "/download-excel"
)
async def download_excel_compatibility():
    """
    Backward-compatible Excel download endpoint.
    """

    return await download_excel()


# ==========================================================
# SEARCH API
# ==========================================================

@app.get(
    "/search"
)
async def search_compatibility(
    keyword: str,
) -> dict[str, Any]:
    """
    Search invoices by keyword.
    """

    keyword = keyword.strip()

    if not keyword:

        raise HTTPException(
            status_code=400,
            detail=(
                "Search keyword cannot be empty."
            ),
        )

    results = (
        invoice_repository.search(
            keyword
        )
    )

    return {
        "success": True,
        "query": keyword,
        "count": len(results),
        "data": results,
    }


# ==========================================================
# READINESS CHECK
# ==========================================================

@app.get(
    "/ready"
)
async def readiness() -> JSONResponse:
    """
    Readiness endpoint for Docker/orchestrators.

    Checks database connectivity.
    """

    try:

        from database import test_connection

        if not test_connection():

            return JSONResponse(
                status_code=503,

                content={
                    "ready": False,
                    "database": "unavailable",
                },
            )

        return JSONResponse(
            status_code=200,

            content={
                "ready": True,
                "database": "available",
            },
        )

    except Exception:

        logger.exception(
            "Readiness check failed."
        )

        return JSONResponse(
            status_code=503,

            content={
                "ready": False,
                "database": "unavailable",
            },
        )


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get(
    "/health"
)
async def health() -> dict[str, Any]:
    """
    Liveness endpoint.

    This endpoint intentionally does not fail
    if the database is temporarily unavailable.
    """

    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
    }


# ==========================================================
# REQUEST LOGGING
# ==========================================================

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next,
):
    """
    Central HTTP request logging.
    """

    start_time = time.perf_counter()

    try:

        response = await call_next(
            request
        )

        return response

    finally:

        elapsed = (
            time.perf_counter()
            - start_time
        )

        logger.info(
            "%s %s %.3fs",
            request.method,
            request.url.path,
            elapsed,
        )


# ==========================================================
# SECURITY HEADERS
# ==========================================================

@app.middleware("http")
async def security_headers(
    request: Request,
    call_next,
):
    """
    Add baseline browser security headers.
    """

    response = await call_next(
        request
    )

    # Prevent MIME sniffing
    response.headers[
        "X-Content-Type-Options"
    ] = "nosniff"

    # Prevent clickjacking
    response.headers[
        "X-Frame-Options"
    ] = "DENY"

    # Referrer control
    response.headers[
        "Referrer-Policy"
    ] = (
        "strict-origin-when-cross-origin"
    )

    # Browser permissions
    response.headers[
        "Permissions-Policy"
    ] = (
        "camera=(), "
        "microphone=(), "
        "geolocation=(), "
        "payment=()"
    )

    # Content Security Policy
    response.headers[
        "Content-Security-Policy"
    ] = (
        "default-src 'self'; "

        "script-src "
        "'self' "
        "'unsafe-inline' "
        "https://cdn.jsdelivr.net; "

        "style-src "
        "'self' "
        "'unsafe-inline' "
        "https://cdn.jsdelivr.net "
        "https://fonts.googleapis.com; "

        "font-src "
        "'self' "
        "https://fonts.gstatic.com "
        "https://cdn.jsdelivr.net; "

        "img-src "
        "'self' "
        "data: "
        "blob:; "

        "connect-src "
        "'self'; "

        "frame-ancestors "
        "'none'; "

        "base-uri "
        "'self'; "

        "form-action "
        "'self';"
    )

    # HSTS only when HTTPS is actually being used
    if request.url.scheme == "https":

        response.headers[
            "Strict-Transport-Security"
        ] = (
            "max-age=31536000; "
            "includeSubDomains"
        )

    return response


# ==========================================================
# HTTP EXCEPTION HANDLER
# ==========================================================

@app.exception_handler(
    HTTPException
)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    """
    Return consistent API error responses.
    """

    logger.warning(
        "%s %s -> %s: %s",
        request.method,
        request.url.path,
        exc.status_code,
        exc.detail,
    )

    return JSONResponse(
        status_code=exc.status_code,

        content={
            "success": False,
            "message": str(
                exc.detail
            ),
        },
    )


# ==========================================================
# REQUEST VALIDATION ERROR
# ==========================================================

@app.exception_handler(
    RequestValidationError
)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
):
    """
    Return consistent validation responses.
    """

    logger.warning(
        "Validation error on %s %s: %s",
        request.method,
        request.url.path,
        exc.errors(),
    )

    return JSONResponse(
        status_code=422,

        content={
            "success": False,
            "message": "Validation failed.",
            "errors": exc.errors(),
        },
    )


# ==========================================================
# GLOBAL EXCEPTION HANDLER
# ==========================================================

@app.exception_handler(
    Exception
)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Never expose internal exception details
    to clients.
    """

    logger.exception(
        "Unhandled application exception: %s %s",
        request.method,
        request.url.path,
    )

    return JSONResponse(
        status_code=500,

        content={
            "success": False,
            "message": "Internal Server Error",
        },
    )


# ==========================================================
# APPLICATION READY
# ==========================================================

logger.info("=" * 60)

logger.info(
    "%s %s ready.",
    APP_NAME,
    APP_VERSION,
)

logger.info("=" * 60)


# ==========================================================
# PUBLIC EXPORTS
# ==========================================================

__all__ = [
    "app",
    "get_dashboard_data",
]
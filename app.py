"""
==========================================
AI Invoice Extractor
FastAPI Application
==========================================
"""

import os
import shutil
from contextlib import asynccontextmanager

import fitz

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    BackgroundTasks
)

from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    FileResponse
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv

from config import (
    APP_NAME,
    APP_VERSION,
    UPLOAD_FOLDER,
    EXPORT_FOLDER,
    STATIC_FOLDER,
    TEMPLATE_FOLDER,
    EXCEL_FILENAME
)

from logger import logger

from database import (
    create_table,
    get_all_invoices,
    get_invoice,
    search_invoice,
    delete_invoice
)

from ocr_engine import (
    image_to_text,
    pdf_to_text_with_ocr
)

from invoice_service import (
    process_document,
    save_document
)

from excel_export import (
    export_to_excel
)

from background_tasks import (
    process_invoice
)

# ==========================================
# LOAD ENVIRONMENT
# ==========================================

load_dotenv()

# ==========================================
# CREATE REQUIRED FOLDERS
# ==========================================

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
EXPORT_FOLDER.mkdir(parents=True, exist_ok=True)
STATIC_FOLDER.mkdir(parents=True, exist_ok=True)
TEMPLATE_FOLDER.mkdir(parents=True, exist_ok=True)

# ==========================================
# FASTAPI LIFESPAN
# ==========================================

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_table()

    logger.info("Database Connected")

    yield

    logger.info("Application Closed")

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(

    title=APP_NAME,

    version=APP_VERSION,

    lifespan=lifespan

)

# ==========================================
# TEMPLATE
# ==========================================

templates = Jinja2Templates(

    directory=str(TEMPLATE_FOLDER)

)

# ==========================================
# STATIC
# ==========================================

app.mount(

    "/static",

    StaticFiles(directory=str(STATIC_FOLDER)),

    name="static"

)

# ==========================================
# READ PDF
# ==========================================

def read_pdf(pdf_path: str):

    text = ""

    pdf = fitz.open(pdf_path)

    for page in pdf:

        text += page.get_text()

    pdf.close()

    return text

# ==========================================
# HOME PAGE
# ==========================================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "request": request
        }
    )

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")

def health():

    return {

        "success": True,

        "status": "Running",

        "application": APP_NAME,

        "version": APP_VERSION

    }
# ==========================================
# UPLOAD DOCUMENT
# ==========================================

@app.post("/upload")
async def upload_document(

    background_tasks: BackgroundTasks,

    file: UploadFile = File(...)

):

    try:

        # ----------------------------------
        # Validate File
        # ----------------------------------

        if file.filename == "":

            return JSONResponse(

                status_code=400,

                content={

                    "success": False,

                    "message": "No file selected."

                }

            )

        extension = os.path.splitext(

            file.filename

        )[1].lower()

        allowed = {

            ".pdf",

            ".png",

            ".jpg",

            ".jpeg"

        }

        if extension not in allowed:

            return JSONResponse(

                status_code=400,

                content={

                    "success": False,

                    "message": "Unsupported file format."

                }

            )

        # ----------------------------------
        # Save Upload
        # ----------------------------------

        filepath = UPLOAD_FOLDER / file.filename

        with open(

            filepath,

            "wb"

        ) as buffer:

            shutil.copyfileobj(

                file.file,

                buffer

            )

        logger.info(

            f"Uploaded : {file.filename}"

        )

        # ----------------------------------
        # OCR
        # ----------------------------------

        if extension == ".pdf":

            document_text = read_pdf(

                str(filepath)

            )

            if document_text.strip() == "":

                logger.info(

                    "Running OCR..."

                )

                document_text = pdf_to_text_with_ocr(

                    str(filepath)

                )

        else:

            document_text = image_to_text(

                str(filepath)

            )

        if document_text.strip() == "":

            return JSONResponse(

                status_code=400,

                content={

                    "success": False,

                    "message": "Unable to read document."

                }

            )

        # ----------------------------------
        # AI Processing
        # ----------------------------------

        document = process_document(

            file.filename,

            document_text

        )

        # ----------------------------------
        # Save Database
        # ----------------------------------

        save_document(

            file.filename,

            document

        )

        # ----------------------------------
        # Export Excel
        # ----------------------------------

        excel_path = EXPORT_FOLDER / EXCEL_FILENAME

        export_to_excel(

            document,

            excel_path

        )

        # ----------------------------------
        # Background Processing
        # ----------------------------------

        background_tasks.add_task(

            process_invoice,

            file.filename,

            document_text

        )

        logger.info(

            "Upload Completed"

        )

        return {

            "success": True,

            "filename": file.filename,

            "document": document,

            "excel": "/download-excel"

        }

    except Exception as e:

        logger.exception(

            "Upload Error"

        )

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )
    # ==========================================
# DOWNLOAD EXCEL
# ==========================================

@app.get("/download-excel")
def download_excel():

    excel_file = EXPORT_FOLDER / EXCEL_FILENAME

    if not excel_file.exists():

        return JSONResponse(
            status_code=404,
            content={
                "success": False,
                "message": "Excel file not found."
            }
        )

    return FileResponse(
        path=str(excel_file),
        filename=EXCEL_FILENAME,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ==========================================
# HISTORY
# ==========================================

@app.get("/history")
def history():

    try:

        invoices = get_all_invoices()

        return {

            "success": True,

            "count": len(invoices),

            "data": invoices

        }

    except Exception as e:

        logger.exception("History Error")

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )


# ==========================================
# SEARCH
# ==========================================

@app.get("/search")
def search(keyword: str):

    try:

        invoices = search_invoice(keyword)

        return {

            "success": True,

            "count": len(invoices),

            "data": invoices

        }

    except Exception as e:

        logger.exception("Search Error")

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )


# ==========================================
# GET SINGLE INVOICE
# ==========================================

@app.get("/invoice/{invoice_id}")
def get_single_invoice(invoice_id: int):

    try:

        invoice = get_invoice(invoice_id)

        if invoice is None:

            return JSONResponse(

                status_code=404,

                content={

                    "success": False,

                    "message": "Invoice not found."

                }

            )

        return {

            "success": True,

            "data": invoice

        }

    except Exception as e:

        logger.exception("Invoice Error")

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )


# ==========================================
# DELETE
# ==========================================

@app.delete("/invoice/{invoice_id}")
def remove_invoice(invoice_id: int):

    try:

        delete_invoice(invoice_id)

        return {

            "success": True,

            "message": "Invoice deleted successfully."

        }

    except Exception as e:

        logger.exception("Delete Error")

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )


# ==========================================
# DASHBOARD
# ==========================================

@app.get("/dashboard")
def dashboard():

    try:

        invoices = get_all_invoices()

        total_invoices = len(invoices)

        total_amount = 0.0

        for invoice in invoices:

            try:

                total_amount += float(
                    invoice.get("grand_total") or 0
                )

            except:

                pass

        return {

            "success": True,

            "total_invoices": total_invoices,

            "total_amount": round(total_amount, 2),

            "data": invoices

        }

    except Exception as e:

        logger.exception("Dashboard Error")

        return JSONResponse(

            status_code=500,

            content={

                "success": False,

                "message": str(e)

            }

        )
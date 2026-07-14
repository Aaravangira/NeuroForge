"""
==========================================
DATABASE
AI Invoice Extractor
==========================================
"""

import sqlite3
from typing import Optional

from config import DATABASE_PATH
from logger import logger

# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    conn = sqlite3.connect(DATABASE_PATH)

    conn.row_factory = sqlite3.Row

    return conn


# ==========================================
# CREATE TABLE
# ==========================================

def create_table():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS invoices (

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        filename TEXT,

        vendor_name TEXT,

        invoice_number TEXT,

        invoice_date TEXT,

        gst_number TEXT,

        subtotal TEXT,

        tax TEXT,

        grand_total TEXT,

        payment_method TEXT,

        currency TEXT,

        raw_text TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.commit()

    conn.close()

    logger.info("Database table ready.")


# ==========================================
# SAVE INVOICE
# ==========================================

def save_invoice(data: dict):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO invoices(

        filename,

        vendor_name,

        invoice_number,

        invoice_date,

        gst_number,

        subtotal,

        tax,

        grand_total,

        payment_method,

        currency,

        raw_text

    )

    VALUES(?,?,?,?,?,?,?,?,?,?,?)

    """, (

        data.get("filename"),

        data.get("vendor_name"),

        data.get("invoice_number"),

        data.get("invoice_date"),

        data.get("gst_number"),

        data.get("subtotal"),

        data.get("tax"),

        data.get("grand_total"),

        data.get("payment_method"),

        data.get("currency"),

        data.get("raw_text")

    ))

    conn.commit()

    invoice_id = cursor.lastrowid

    conn.close()

    logger.info(f"Invoice Saved : {invoice_id}")

    return invoice_id


# ==========================================
# GET ALL
# ==========================================

def get_all_invoices():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM invoices

    ORDER BY id DESC

    """)

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================
# GET SINGLE
# ==========================================

def get_invoice(invoice_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    SELECT *

    FROM invoices

    WHERE id=?

    """, (invoice_id,))

    row = cursor.fetchone()

    conn.close()

    if row:

        return dict(row)

    return None


# ==========================================
# SEARCH
# ==========================================

def search_invoice(keyword: str):

    conn = get_connection()

    cursor = conn.cursor()

    like = f"%{keyword}%"

    cursor.execute("""

    SELECT *

    FROM invoices

    WHERE

        vendor_name LIKE ?

        OR invoice_number LIKE ?

        OR filename LIKE ?

        OR gst_number LIKE ?

    ORDER BY id DESC

    """,

    (

        like,

        like,

        like,

        like

    ))

    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# ==========================================
# DELETE
# ==========================================

def delete_invoice(invoice_id: int):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    DELETE FROM invoices

    WHERE id=?

    """, (invoice_id,))

    conn.commit()

    conn.close()

    logger.info(f"Invoice Deleted : {invoice_id}")
import sqlite3
import json
from datetime import datetime

DB_NAME = "documents.db"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            document_type TEXT,
            extracted_data TEXT,
            raw_text TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_document(filename, document_type, extracted_data, raw_text):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO documents (filename, document_type, extracted_data, raw_text, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (
        filename,
        document_type,
        json.dumps(extracted_data, ensure_ascii=False),
        raw_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_all_documents(document_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    if document_type:
        cursor.execute("""
            SELECT id, filename, document_type, extracted_data, raw_text, created_at
            FROM documents
            WHERE document_type = ?
            ORDER BY id DESC
        """, (document_type,))
    else:
        cursor.execute("""
            SELECT id, filename, document_type, extracted_data, raw_text, created_at
            FROM documents
            ORDER BY id DESC
        """)

    rows = cursor.fetchall()
    conn.close()

    documents = []
    for row in rows:
        documents.append({
            "id": row["id"],
            "filename": row["filename"],
            "document_type": row["document_type"],
            "extracted_data": json.loads(row["extracted_data"]) if row["extracted_data"] else {},
            "raw_text": row["raw_text"],
            "created_at": row["created_at"]
        })

    return documents


def get_document_by_id(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, document_type, extracted_data, raw_text, created_at
        FROM documents
        WHERE id = ?
    """, (document_id,))

    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "filename": row["filename"],
        "document_type": row["document_type"],
        "extracted_data": json.loads(row["extracted_data"]) if row["extracted_data"] else {},
        "raw_text": row["raw_text"],
        "created_at": row["created_at"]
    }


def delete_document_by_id(document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM documents WHERE id = ?", (document_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False

    cursor.execute("DELETE FROM documents WHERE id = ?", (document_id,))
    conn.commit()
    conn.close()
    return True


def get_document_summary():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_type, COUNT(*) as count
        FROM documents
        GROUP BY document_type
        ORDER BY count DESC
    """)

    rows = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) as total FROM documents")
    total_row = cursor.fetchone()

    conn.close()

    breakdown = []
    for row in rows:
        breakdown.append({
            "document_type": row["document_type"] if row["document_type"] else "unknown",
            "count": row["count"]
        })

    return {
        "total_documents": total_row["total"],
        "breakdown": breakdown
    }


def get_documents_table(document_type=None):
    documents = get_all_documents(document_type=document_type)

    table_rows = []
    for doc in documents:
        extracted = doc["extracted_data"]

        table_rows.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "document_type": doc["document_type"],
            "created_at": doc["created_at"],
            "summary": build_summary(doc["document_type"], extracted)
        })

    return table_rows


def build_summary(document_type, extracted_data):
    if not isinstance(extracted_data, dict):
        return {}

    if document_type == "receipt":
        return {
            "vendor": extracted_data.get("vendor", {}).get("name"),
            "date": extracted_data.get("transaction", {}).get("date"),
            "total": extracted_data.get("total")
        }

    if document_type == "invoice":
        invoice_details = extracted_data.get("invoice_details", {})
        return {
            "vendor": invoice_details.get("company_name") or extracted_data.get("vendor_name"),
            "invoice_number": invoice_details.get("invoice_number") or extracted_data.get("invoice_number"),
            "total": invoice_details.get("invoice_total") or extracted_data.get("total")
        }

    if document_type == "paystub":
        return {
            "employee": extracted_data.get("employee", {}).get("name"),
            "company": extracted_data.get("company", {}).get("name"),
            "net_pay": extracted_data.get("net_pay", {}).get("current"),
            "cheque_date": extracted_data.get("pay_period", {}).get("cheque_date")
        }

    return {
        "note": "No summary available"
    }


def get_chart_data():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_type, COUNT(*) as count
        FROM documents
        GROUP BY document_type
        ORDER BY count DESC
    """)

    type_rows = cursor.fetchall()

    cursor.execute("""
        SELECT substr(created_at, 1, 10) as day, COUNT(*) as count
        FROM documents
        GROUP BY day
        ORDER BY day ASC
    """)

    day_rows = cursor.fetchall()

    conn.close()

    by_type = []
    for row in type_rows:
        by_type.append({
            "label": row["document_type"] if row["document_type"] else "unknown",
            "value": row["count"]
        })

    by_day = []
    for row in day_rows:
        by_day.append({
            "date": row["day"],
            "count": row["count"]
        })

    return {
        "by_type": by_type,
        "by_day": by_day
    }
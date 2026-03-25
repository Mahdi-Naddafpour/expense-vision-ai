import os
import sqlite3
import json
from datetime import datetime

DB_NAME = os.getenv("DB_NAME", "documents.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            filename TEXT NOT NULL,
            document_type TEXT,
            extracted_data TEXT,
            raw_text TEXT,
            created_at TEXT NOT NULL,
            document_date TEXT,
            total_amount REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()

    cursor.execute("PRAGMA table_info(documents)")
    columns = [row["name"] for row in cursor.fetchall()]

    if "user_id" not in columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")

    if "document_date" not in columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN document_date TEXT")

    if "total_amount" not in columns:
        cursor.execute("ALTER TABLE documents ADD COLUMN total_amount REAL")

    conn.commit()
    conn.close()


def create_user(username, password_hash):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO users (username, password_hash, created_at)
        VALUES (?, ?, ?)
    """, (
        username,
        password_hash,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, username, password_hash, created_at
        FROM users
        WHERE username = ?
    """, (username,))

    row = cursor.fetchone()
    conn.close()
    return row


def extract_date_and_amount(document_type, extracted_data):
    document_date = None
    total_amount = None

    if not isinstance(extracted_data, dict):
        return document_date, total_amount

    document_date = (
        extracted_data.get("document_date")
        or extracted_data.get("date")
    )

    total_amount = (
        extracted_data.get("total_amount")
        or extracted_data.get("total")
        or extracted_data.get("amount")
        or extracted_data.get("grand_total")
    )

    if document_type == "receipt":
        document_date = (
            document_date
            or extracted_data.get("transaction", {}).get("date")
        )
        total_amount = (
            total_amount
            or extracted_data.get("total")
        )

    elif document_type == "invoice":
        invoice_details = extracted_data.get("invoice_details", {})
        document_date = (
            document_date
            or invoice_details.get("date")
            or extracted_data.get("invoice_date")
        )
        total_amount = (
            total_amount
            or invoice_details.get("invoice_total")
        )

    elif document_type == "paystub":
        document_date = (
            document_date
            or extracted_data.get("pay_period", {}).get("cheque_date")
        )
        net_pay = extracted_data.get("net_pay", {})
        if isinstance(net_pay, dict):
            total_amount = total_amount or net_pay.get("current")

    try:
        if total_amount is not None and str(total_amount).strip() != "":
            total_amount = float(
                str(total_amount)
                .replace(",", "")
                .replace("$", "")
                .replace("CAD", "")
                .strip()
            )
        else:
            total_amount = None
    except Exception:
        total_amount = None

    return document_date, total_amount


def save_document(user_id, filename, document_type, extracted_data, raw_text):
    conn = get_connection()
    cursor = conn.cursor()

    document_date, total_amount = extract_date_and_amount(document_type, extracted_data)

    cursor.execute("""
        INSERT INTO documents (
            user_id,
            filename,
            document_type,
            extracted_data,
            raw_text,
            created_at,
            document_date,
            total_amount
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        filename,
        document_type,
        json.dumps(extracted_data, ensure_ascii=False),
        raw_text,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        document_date,
        total_amount
    ))

    conn.commit()
    conn.close()


def get_all_documents(user_id, document_type=None):
    conn = get_connection()
    cursor = conn.cursor()

    if document_type:
        cursor.execute("""
            SELECT id, filename, document_type, extracted_data, raw_text, created_at, document_date, total_amount
            FROM documents
            WHERE user_id = ? AND document_type = ?
            ORDER BY id DESC
        """, (user_id, document_type))
    else:
        cursor.execute("""
            SELECT id, filename, document_type, extracted_data, raw_text, created_at, document_date, total_amount
            FROM documents
            WHERE user_id = ?
            ORDER BY id DESC
        """, (user_id,))

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
            "created_at": row["created_at"],
            "document_date": row["document_date"],
            "total_amount": row["total_amount"]
        })

    return documents


def get_document_by_id(user_id, document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, filename, document_type, extracted_data, raw_text, created_at, document_date, total_amount
        FROM documents
        WHERE user_id = ? AND id = ?
    """, (user_id, document_id))

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
        "created_at": row["created_at"],
        "document_date": row["document_date"],
        "total_amount": row["total_amount"]
    }


def delete_document_by_id(user_id, document_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id
        FROM documents
        WHERE user_id = ? AND id = ?
    """, (user_id, document_id))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return False

    cursor.execute("""
        DELETE FROM documents
        WHERE user_id = ? AND id = ?
    """, (user_id, document_id))

    conn.commit()
    conn.close()
    return True


def get_document_summary(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_type, COUNT(*) as count
        FROM documents
        WHERE user_id = ?
        GROUP BY document_type
        ORDER BY count DESC
    """, (user_id,))

    rows = cursor.fetchall()

    cursor.execute("""
        SELECT COUNT(*) as total
        FROM documents
        WHERE user_id = ?
    """, (user_id,))
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


def build_summary(document_type, extracted_data):
    if not isinstance(extracted_data, dict):
        return {}

    if document_type == "receipt":
        return {
            "vendor": extracted_data.get("vendor_name") or extracted_data.get("vendor", {}).get("name"),
            "date": extracted_data.get("transaction", {}).get("date") or extracted_data.get("document_date"),
            "total": extracted_data.get("total_amount") or extracted_data.get("total")
        }

    if document_type == "invoice":
        invoice_details = extracted_data.get("invoice_details", {})
        return {
            "vendor": invoice_details.get("company_name") or extracted_data.get("vendor_name"),
            "invoice_number": invoice_details.get("invoice_number") or extracted_data.get("invoice_number"),
            "total": extracted_data.get("total_amount") or invoice_details.get("invoice_total") or extracted_data.get("total")
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


def get_documents_table(user_id, document_type=None):
    documents = get_all_documents(user_id=user_id, document_type=document_type)

    table_rows = []
    for doc in documents:
        extracted = doc["extracted_data"]

        table_rows.append({
            "id": doc["id"],
            "filename": doc["filename"],
            "document_type": doc["document_type"],
            "created_at": doc["created_at"],
            "document_date": doc["document_date"],
            "total_amount": doc["total_amount"],
            "summary": build_summary(doc["document_type"], extracted)
        })

    return table_rows


def get_chart_data(user_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_type, COUNT(*) as count
        FROM documents
        WHERE user_id = ?
        GROUP BY document_type
        ORDER BY count DESC
    """, (user_id,))
    type_rows = cursor.fetchall()

    cursor.execute("""
        SELECT substr(created_at, 1, 10) as day, COUNT(*) as count
        FROM documents
        WHERE user_id = ?
        GROUP BY day
        ORDER BY day ASC
    """, (user_id,))
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


def get_analytics(user_id, date_from=None, date_to=None):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
        SELECT
            document_type,
            COUNT(*) as count,
            COALESCE(SUM(total_amount), 0) as total_amount
        FROM documents
        WHERE user_id = ?
    """
    params = [user_id]

    if date_from:
        query += " AND created_at >= ?"
        params.append(date_from + " 00:00:00")

    if date_to:
        query += " AND created_at <= ?"
        params.append(date_to + " 23:59:59")

    query += " GROUP BY document_type ORDER BY document_type"

    cursor.execute(query, params)
    rows = cursor.fetchall()

    result = []
    for row in rows:
        result.append({
            "document_type": row["document_type"] if row["document_type"] else "unknown",
            "count": row["count"],
            "total_amount": float(row["total_amount"]) if row["total_amount"] is not None else 0.0
        })

    conn.close()
    return result
from fastapi import FastAPI, File, UploadFile, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import shutil
import os
import csv
import io

from PIL import Image
import pytesseract
from pdf2image import convert_from_path

from app.ai.extractor_ai import ai_extract
from app.database import (
    init_db,
    get_connection,
    save_document,
    get_all_documents,
    get_document_by_id,
    get_document_summary,
    get_documents_table,
    get_chart_data,
    delete_document_by_id
)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key="super-secret-login-key-change-this")

UPLOAD_FOLDER = "temp"
STATIC_FOLDER = "static"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(STATIC_FOLDER, exist_ok=True)

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
POPPLER_PATH = r"C:\poppler\Library\bin"

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory=STATIC_FOLDER), name="static")

# demo credentials for portfolio project
DEMO_USERNAME = "admin"
DEMO_PASSWORD = "1234"


def is_logged_in(request: Request) -> bool:
    return request.session.get("user") is not None


def require_login(request: Request):
    if not is_logged_in(request):
        raise HTTPException(status_code=401, detail="Not authenticated")


def ocr_image(image_path: str) -> str:
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text


def ocr_pdf(pdf_path: str) -> str:
    images = convert_from_path(pdf_path, poppler_path=POPPLER_PATH)
    text = ""

    for img in images:
        text += pytesseract.image_to_string(img) + "\n"

    return text


def get_file_type(filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        return "pdf"
    elif filename.lower().endswith((".png", ".jpg", ".jpeg")):
        return "image"
    return "unknown"


@app.on_event("startup")
def startup_event():
    init_db()


@app.get("/")
def read_root():
    return RedirectResponse(url="/login", status_code=302)


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if is_logged_in(request):
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": None
        }
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    if username == DEMO_USERNAME and password == DEMO_PASSWORD:
        request.session["user"] = username
        return RedirectResponse(url="/dashboard", status_code=302)

    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "Invalid username or password"
        }
    )


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    if not is_logged_in(request):
        return RedirectResponse(url="/login", status_code=302)

    summary = get_document_summary()
    rows = get_documents_table()
    chart_data = get_chart_data()

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "summary": summary,
            "rows": rows,
            "chart_data": chart_data,
            "user": request.session.get("user")
        }
    )


@app.post("/upload")
async def upload_file(request: Request, file: UploadFile = File(...)):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_type = get_file_type(file.filename)

        if file_type == "image":
            text = ocr_image(file_path)
        elif file_type == "pdf":
            text = ocr_pdf(file_path)
        else:
            return {"error": "Unsupported file type"}

        ai_result = ai_extract(text)

        document_type = (
            ai_result.get("document_type", "unknown")
            if isinstance(ai_result, dict)
            else "unknown"
        )

        save_document(
            filename=file.filename,
            document_type=document_type,
            extracted_data=ai_result,
            raw_text=text
        )

        return {
            "filename": file.filename,
            "document_type": document_type,
            "data": ai_result,
            "raw_text": text[:1000],
            "message": "Document processed and saved to database"
        }

    except Exception as e:
        return {"error": str(e)}


@app.get("/documents")
def list_documents(request: Request, document_type: str | None = None):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        documents = get_all_documents(document_type=document_type)
        return {
            "count": len(documents),
            "documents": documents
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/documents/table")
def documents_table(request: Request, document_type: str | None = None):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        rows = get_documents_table(document_type=document_type)
        return {
            "count": len(rows),
            "rows": rows
        }
    except Exception as e:
        return {"error": str(e)}


@app.get("/documents/summary")
def documents_summary(request: Request):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        return get_document_summary()
    except Exception as e:
        return {"error": str(e)}


@app.get("/documents/chart-data")
def documents_chart_data(request: Request):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        return get_chart_data()
    except Exception as e:
        return {"error": str(e)}


@app.get("/documents/{document_id}")
def get_single_document(request: Request, document_id: int):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        document = get_document_by_id(document_id)

        if not document:
            return {"error": "Document not found"}

        return document
    except Exception as e:
        return {"error": str(e)}


@app.delete("/delete/{doc_id}")
def delete_document(request: Request, doc_id: int):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        deleted = delete_document_by_id(doc_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Document not found")

        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        return {"error": str(e)}


@app.get("/export/csv")
def export_csv(request: Request):
    if not is_logged_in(request):
        return {"error": "Not authenticated"}

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, filename, document_type, created_at
            FROM documents
            ORDER BY id DESC
        """)
        rows = cursor.fetchall()
        conn.close()

        output = io.StringIO()
        writer = csv.writer(output)

        writer.writerow(["ID", "Filename", "Type", "Created At"])

        for row in rows:
            writer.writerow([
                row["id"],
                row["filename"],
                row["document_type"],
                row["created_at"]
            ])

        output.seek(0)

        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=documents.csv"}
        )

    except Exception as e:
        return {"error": str(e)}
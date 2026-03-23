# Expense Vision AI

An AI-powered document processing system built with FastAPI.

## 🚀 Features

- Upload receipts, invoices, and paystubs
- OCR text extraction (Tesseract)
- AI-based structured data extraction
- SQLite database storage
- Interactive dashboard with charts
- Search and filter documents
- Delete documents
- Export data to CSV

## 🧠 Tech Stack

- Python
- FastAPI
- SQLite
- Tesseract OCR
- OpenAI API
- HTML / CSS / JavaScript
- Chart.js

## 📸 Dashboard

![Dashboard](screenshot.png)

## ⚙️ Installation

```bash
git clone https://github.com/YOUR_USERNAME/expense-vision.git
cd expense-vision

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
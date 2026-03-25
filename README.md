# 🚀 Expense Vision AI

An AI-powered web application for extracting, organizing, and analyzing financial documents such as invoices, receipts, and paystubs.

🔗 **Live Demo:**
https://expense-vision-ai.onrender.com

---

## ✨ Overview

Expense Vision AI is a full-stack intelligent document processing system designed to simplify financial tracking.

Users can upload documents, automatically extract key data using AI, and visualize insights through an interactive analytics dashboard.

This project demonstrates real-world backend development skills combined with AI integration and production deployment.

---

## 🔥 Key Features

* 🧠 **AI Document Extraction**
  Automatically detects document type (invoice, receipt, paystub) and extracts structured data

* 🔐 **User Authentication System**
  Secure registration & login with hashed passwords

* 📊 **Analytics Dashboard**

  * Document count by type
  * Total amount summaries
  * Interactive charts

* 🧾 **Multi-Document Support**
  Handles invoices, receipts, and paystubs seamlessly

* 📅 **Date Filtering**
  Analyze documents within a specific time range

* 🗂 **User-Based Data Isolation**
  Each user only sees their own data

* ☁️ **Deployed to Production**
  Fully deployed using Render

---

## 🛠 Tech Stack

**Backend:**

* Python
* FastAPI
* SQLite

**AI:**

* OpenAI API (GPT-based extraction)

**Frontend:**

* HTML
* CSS
* Chart.js

**Deployment:**

* Render

---

## 🧠 What This Project Demonstrates

* Real-world backend architecture
* REST API development
* AI integration into production systems
* Authentication & session handling
* Data processing & analytics
* Clean project structure
* Deployment & DevOps basics

---

## ⚙️ How to Run Locally

```bash
git clone https://github.com/Mahdi-Naddafpour/expense-vision-ai.git
cd expense-vision-ai

python -m venv venv
venv\Scripts\activate

pip install -r requirements.txt

uvicorn app.main:app --reload
```

---

## 🔐 Environment Variables

Create a `.env` file:

```
Leveraging OpenAI GPT models to transform unstructured financial documents (invoices, receipts, paystubs) into structured, queryable data
```

---

## 🚧 Future Improvements

* PostgreSQL instead of SQLite
* Cloud file storage (AWS S3 / Cloudinary)
* JWT Authentication
* Better UI/UX (React frontend)
* Advanced analytics

---

## 👨‍💻 Author

**Mahdi Naddafpour**

* Backend Developer (Python / FastAPI)
* Passionate about building real-world AI applications

---

## ⭐ Why This Project Stands Out

Unlike simple CRUD apps, this project combines:

* AI + Backend Engineering
* Real-world use case (financial document processing)
* Authentication + analytics
* Production deployment

This reflects practical skills required in modern software engineering roles.

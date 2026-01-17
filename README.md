KTU Result PDF → Excel Processor

A backend-focused web application that converts KTU result PDFs (text-layer) into structured Excel workbooks for academic analysis and reporting.

This project emphasizes deterministic data processing using regex and structured parsing — no OCR, no machine learning.

✨ Features

Upload KTU result PDF

Parse student-wise results (USN → subjects → grades)

Department-aware extraction

Generate Excel workbook:

Master sheet

Department-wise sheets

Audit-ready structure (planned)

Backend API built with FastAPI

Frontend kept minimal and framework-agnostic

🏗️ Architecture Overview
KTU Result PDF
      ↓
Text Extraction
      ↓
Regex Parsing (Student-Level)
      ↓
Structured Python Objects
      ↓
Excel Workbook Generation


The backend is designed to be UI-independent — any frontend (HTML, React, etc.) can consume the API.

📁 Project Structure
ktu-result-processor/
├── backend/
│   ├── main.py               # FastAPI entry point
│   ├── pdf_parser.py         # PDF parsing logic
│   ├── excel_generator.py    # Excel generation logic
│   ├── data/                 # Uploaded files (git-ignored)
│   └── output/               # Generated reports (git-ignored)
│
├── frontend/
│   ├── index.html            # Upload UI
│   └── script.js             # API interaction
│
├── README.md
└── .gitignore

🔧 Tech Stack

Backend

Python

FastAPI

PyPDF2

regex

pandas

openpyxl

Frontend

HTML

CSS

Vanilla JavaScript

Planned

SQLite (for persistence & audit)

Charts for statistics

🎯 Project Goals

Convert KTU result PDFs into a clean, analyzable Excel format

Keep parsing deterministic and explainable

Avoid OCR and probabilistic methods

Build something college-friendly but internship-worthy

🚧 Project Status
✅ Completed

Backend setup and API scaffolding

PDF parsing logic (student-level extraction)

Department detection and normalization

Health check endpoint

🔄 In Progress

File upload UI (PDF + master file)

Frontend → backend integration (/upload)

⏳ Planned

Excel download endpoint

Statistics API (pass/fail, department-wise)

Graphical result visualization

Basic UI polish and validations
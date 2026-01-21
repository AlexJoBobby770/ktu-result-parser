KTU Result PDF → Excel Processor

A backend-focused web application that converts KTU result PDFs (text-layer) into structured Excel workbooks for academic analysis and reporting.

This project uses deterministic parsing with regex — no OCR, no machine learning.

✨ Features

Upload KTU result PDF

Parse student-wise results (USN → subjects → grades)

Department-aware extraction

Generate Excel workbook (master & department-wise)

FastAPI backend

Minimal, framework-agnostic frontend

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

📁 Project Structure

ktu-result-processor/
├── backend/
│ ├── main.py # FastAPI entry point
│ ├── pdf_parser.py # PDF parsing logic
│ ├── excel_generator.py # Excel generation logic
│ ├── data/ # Uploaded files (git-ignored)
│ └── output/ # Generated reports (git-ignored)
│
├── frontend/
│ ├── index.html # Upload UI
│ └── script.js # API interaction
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

🎯 Project Goal

Build a backend system that converts KTU result PDFs (text-layer) into a clean, analyzable Excel workbook.

No OCR

No ML / NLP

Deterministic and explainable parsing

Designed for college-level academic use

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

UI polish and basic validations
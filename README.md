KTU Result PDF → Excel Processor

Backend system to convert KTU result PDFs (text-layer) into structured Excel reports.

No OCR. No ML. Deterministic parsing using regex.

Tech Stack

Backend: Python, FastAPI

PDF Parsing: PyPDF2 + regex

Excel: pandas, openpyxl

Frontend: React (Vite)

DB (planned): SQLite

Current Status
✅ Working

FastAPI backend running

/upload endpoint implemented

PDF parsing works (student-level)

Excel generation works

React frontend connected and usable

🔄 In Progress

Frontend UI improvements

Better upload feedback & UX

⏳ Planned

Excel download endpoint polish

Stats API (pass/fail, dept-wise)

Charts & visualization

Basic error handling

Project Structure
backend/    → FastAPI, parsing, Excel generation
frontend/   → React (Vite)

Running (Dev)

Backend

cd backend
uvicorn main:app --reload


Frontend

cd frontend
npm install
npm run dev

Notes

PDFs, outputs, and node_modules are git-ignored

Backend is frontend-agnostic

Focus is correctness first, UI later
# backend/main.py
import os
import uuid
import shutil

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.pdf_parser import parse_ktu_pdf
from backend.internal_parser import parse_sessional_pdf
from backend.excel_generator import generate_external_excel, generate_merged_excel

app = FastAPI(title="KTU Result Processor API")

# In production, replace "*" with your Vercel frontend URL
# e.g. ["https://ktu-result-parser.vercel.app"]
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")


# ── static frontend ───────────────────────────────────────────────────────────

@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

@app.get("/static/styles.css")
def get_styles():
    return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"), media_type="text/css")

@app.get("/static/script.js")
def get_script():
    return FileResponse(os.path.join(FRONTEND_DIR, "script.js"), media_type="application/javascript")


# ── health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


# ── upload & process ──────────────────────────────────────────────────────────

@app.post("/upload")
async def upload_result(
    pdf_file:      UploadFile = File(...),
    batch_year:    str        = Form(""),          # e.g. "22"  — optional
    internal_file: UploadFile = File(None),
):
    # Sanitise batch_year: keep only 2 digits, strip whitespace
    batch_year = batch_year.strip().lstrip("20")   # "2022" → "22", "22" → "22"
    batch_year = batch_year[:2] if batch_year.isdigit() else ""

    session_id = uuid.uuid4().hex[:8]

    # Save KTU result PDF
    ext_path = os.path.join(UPLOAD_DIR, f"{session_id}_result.pdf")
    with open(ext_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    print(f"\n[{session_id}] Parsing KTU result PDF...")
    external_records = parse_ktu_pdf(ext_path)

    # Quick stats
    from backend.models import PASSING_GRADES
    student_dept    = {}
    student_arrears = {}
    for r in external_records:
        student_dept[r.usn] = r.department
        student_arrears.setdefault(r.usn, 0)
        if r.grade not in PASSING_GRADES and r.grade != "":
            student_arrears[r.usn] += 1

    total_students  = len(student_dept)
    passed_students = sum(1 for v in student_arrears.values() if v == 0)

    excel_filename = f"{session_id}_results.xlsx"
    excel_path     = os.path.join(OUTPUT_DIR, excel_filename)

    if internal_file and internal_file.filename:
        int_path = os.path.join(UPLOAD_DIR, f"{session_id}_sessional.pdf")
        with open(int_path, "wb") as f:
            shutil.copyfileobj(internal_file.file, f)

        print(f"[{session_id}] Parsing sessional PDF...")
        internal_records, name_mapping, detected_year = parse_sessional_pdf(int_path)

        # Sessional PDF auto-detects batch year; manual entry overrides if provided
        effective_year = batch_year if batch_year else detected_year
        print(f"[{session_id}] Batch year: 20{effective_year} "
              f"({'manual' if batch_year else 'auto-detected'})")

        generate_merged_excel(
            external_records, internal_records, name_mapping,
            excel_path, batch_year=effective_year
        )
        mode = "merged"
    else:
        print(f"[{session_id}] Batch year: "
              f"{'20' + batch_year if batch_year else 'not filtered'}")
        generate_external_excel(external_records, excel_path, batch_year=batch_year)
        mode = "external_only"

    print(f"[{session_id}] Done. Mode={mode}")

    return {
        "status":          "success",
        "session_id":      session_id,
        "message":         "Files processed successfully",
        "total_students":  total_students,
        "passed_students": passed_students,
        "mode":            mode,
    }


# ── download ──────────────────────────────────────────────────────────────────

@app.get("/download/{session_id}")
def download_excel(session_id: str):
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="File not found. Process files first.")
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx",
    )


if __name__ == "__main__":
    import uvicorn
    print("🚀 KTU Result Processor")
    print("   http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
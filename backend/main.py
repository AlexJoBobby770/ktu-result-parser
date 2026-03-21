# backend/main.py
import os
import uuid
import shutil

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

try:
    from backend.pdf_parser import parse_ktu_pdf
    from backend.internal_parser import parse_sessional_pdf
    from backend.excel_generator import generate_external_excel, generate_merged_excel
    from backend.models import PASSING_GRADES
except ModuleNotFoundError:
    from pdf_parser import parse_ktu_pdf
    from internal_parser import parse_sessional_pdf
    from excel_generator import generate_external_excel, generate_merged_excel
    from models import PASSING_GRADES

app = FastAPI(title="KTU Result Processor API")

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


@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/upload")
async def upload_result(
    pdf_file:      UploadFile = File(...),
    batch_year:    str        = Form(""),
    internal_file: UploadFile = File(None),
):
    batch_year = batch_year.strip()
    if len(batch_year) == 4 and batch_year.isdigit():
        batch_year = batch_year[2:]
    elif len(batch_year) == 2 and batch_year.isdigit():
        pass
    else:
        batch_year = ""

    session_id = uuid.uuid4().hex[:8]

    ext_path = os.path.join(UPLOAD_DIR, f"{session_id}_result.pdf")
    with open(ext_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    print(f"\n[{session_id}] Parsing KTU result PDF...")
    external_records = parse_ktu_pdf(ext_path)

    # PASSING_GRADES is now imported at the top — not inside this function
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

        effective_year = batch_year if batch_year else detected_year
        print(f"[{session_id}] Batch year: 20{effective_year}")

        generate_merged_excel(
            external_records, internal_records, name_mapping,
            excel_path, batch_year=effective_year
        )
        mode = "merged"
    else:
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


@app.get("/download/{session_id}")
def download_excel(session_id: str):
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx",
    )
# backend/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil

from pdf_parser import parse_ktu_results
from excel_generator import generate_excel_report
from excel_generator_v2 import generate_merged_excel
from internal_parser import parse_internal_marks
from data_merger import merge_results
from models import ExternalRecord, grade_to_marks

app = FastAPI(title="KTU Result Processor API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================== PUBLIC ROUTES ====================

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


# ==================== FILE PROCESSING (NO AUTH) ====================

@app.post("/upload")
async def upload_result(
    pdf_file: UploadFile = File(...),
    internal_file: UploadFile = File(None)
):
    """Process KTU result PDF with optional internal marks - NO AUTH REQUIRED"""
    
    session_id = uuid.uuid4().hex[:8]
    external_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_external.pdf")
    
    # Save external PDF
    external_filename = f"result_{session_id}.pdf"
    external_path = os.path.join(UPLOAD_DIR, external_filename)
    
    with open(external_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    
    print(f"📄 Parsing external PDF: {external_filename}")
    external_students = parse_ktu_results(external_path)
    
    # Calculate pass/fail statistics
    student_results = {}
    for record in external_students:
        regno = record.register_no
        if regno not in student_results:
            student_results[regno] = {"passed": True}
        
        if record.grade in ["F", "FE", "Absent", "Withheld"]:
            student_results[regno]["passed"] = False
    
    total_students = len(student_results)
    passed_students = sum(1 for s in student_results.values() if s["passed"])
    
    # TWO MODES: Internal + External OR External only
    if internal_file:
        print(f"📄 Parsing internal PDF...")
        
        # Save internal PDF
        internal_filename = f"internal_{session_id}.pdf"
        internal_path = os.path.join(UPLOAD_DIR, internal_filename)
        
        with open(internal_path, "wb") as f:
            shutil.copyfileobj(internal_file.file, f)
        
        # Parse internal marks - RETURNS TUPLE!
        internal_students, name_mapping = parse_internal_marks(internal_path)
        
        print(f"🔗 Merging internal + external data...")
        print(f"   📊 Internal: {len(internal_students)} records")
        print(f"   📊 External: {len(external_students)} records")
        print(f"   👥 Names: {len(name_mapping)} students")
        
        # Merge data - NEEDS 3 ARGUMENTS!
        merged_students, merge_stats = merge_results(
            internal_students, 
            external_students,
            name_mapping
        )
        
        print(f"   ✅ Merged: {merge_stats['total_merged']} records")
        
        # Generate BEAUTIFUL Excel with charts
        excel_filename = f"{session_id}_results.xlsx"
        excel_path = os.path.join(OUTPUT_DIR, excel_filename)
        
        print(f"📊 Generating beautiful Excel with charts...")
        generate_merged_excel(merged_students, excel_path)
        
        has_internal = True
        
    else:
        # Generate SIMPLE Excel (external only)
        excel_filename = f"{session_id}_results.xlsx"
        excel_path = os.path.join(OUTPUT_DIR, excel_filename)
        
        print(f"📊 Generating simple Excel...")
        generate_excel_report(external_students, excel_path)
        
        has_internal = False
    
    print(f"✅ Processing complete! Session: {session_id}")
    
    return {
        "status": "success",
        "session_id": session_id,
        "message": "Files processed successfully",
        "total_students": total_students,
        "passed_students": passed_students,
        "has_internal_marks": has_internal
    }


@app.get("/download/{session_id}")
def download_excel(session_id: str):
    """Download processed Excel file - NO AUTH REQUIRED"""
    
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    
    if not os.path.exists(excel_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx"
    )


if __name__ == "__main__":
    import uvicorn
    print("🚀 KTU Result Processor API")
    print("📍 http://localhost:8000")
    print("📄 Single PDF → Simple Excel")
    print("📄📄 Two PDFs → Beautiful Excel")
    print("🔓 NO AUTHENTICATION REQUIRED")
    uvicorn.run("main:app", reload=True, port=8000)
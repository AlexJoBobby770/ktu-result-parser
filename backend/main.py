# backend/main.py
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil

from pdf_parser import parse_ktu_results
from excel_generator import generate_excel_report
from database import save_session, get_recent_sessions, get_session  # ← ADD THIS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/upload")
async def upload_result(pdf_file: UploadFile = File(...)):
    session_id = uuid.uuid4().hex[:8]

    # Save PDF
    pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    
    # Parse PDF
    results = parse_ktu_results(pdf_path)
    
    # Generate Excel
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    generate_excel_report(results, excel_path)

    # Calculate summary
    summary = {}
    for student in results:
        dept = student["department"]
        if dept not in summary:
            summary[dept] = {"total_students": 0, "with_arrears": 0}
        summary[dept]["total_students"] += 1
        if student["status"] == "Fail":
            summary[dept]["with_arrears"] += 1
    
    
    save_session(
        session_id=session_id,
        filename=pdf_file.filename,
        total_students=len(results),
        total_departments=len(summary)
    )
    
    return {
        "message": f"Successfully parsed {len(results)} students",
        "session_id": session_id,
        "total_students": len(results),
        "departments": summary,
        "excel_ready": True
    }


@app.get("/download/{session_id}")
def download_excel(session_id: str):
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    
    if not os.path.exists(excel_path):
        return {"error": "File not found"}
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx"
    )


@app.get("/sessions")
def get_sessions():
    """Get list of recent uploads"""
    sessions = get_recent_sessions(limit=10)
    return {"sessions": sessions}


@app.get("/sessions/{session_id}")
def get_session_details(session_id: str):
    """Get details of a specific session"""
    session = get_session(session_id)
    
    if not session:
        return {"error": "Session not found"}
    
    # Check if Excel file still exists
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    session["excel_available"] = os.path.exists(excel_path)
    
    return session


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
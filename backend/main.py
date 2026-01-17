from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil

from pdf_parser import parse_ktu_results
from excel_generator import generate_excel_report

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
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
async def upload_result(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):
    # Save PDF
    session_id = uuid.uuid4().hex[:8]
    pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    
    # Save master file (not used yet, but saved for future)
    master_path = os.path.join(UPLOAD_DIR, f"{session_id}_master.xlsx")
    with open(master_path, "wb") as f:
        shutil.copyfileobj(master_file.file, f)
    
    # Parse PDF
    results = parse_ktu_results(pdf_path)
    
    # Generate Excel
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    generate_excel_report(results, excel_path)
    
    # Summary stats
    summary = {}
    for r in results:
        dept = r["department"]
        if dept not in summary:
            summary[dept] = {"total": 0, "pass": 0, "fail": 0}
        summary[dept]["total"] += 1
        if r["status"] == "Pass":
            summary[dept]["pass"] += 1
        else:
            summary[dept]["fail"] += 1
    
    return {
        "message": f"Successfully parsed {len(results)} records",
        "session_id": session_id,
        "total_records": len(results),
        "departments": summary,
        "sample_data": results[:5],
        "excel_ready": True
    }


@app.get("/download/{session_id}")
def download_excel(session_id: str):
    """Download generated Excel file"""
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    
    if not os.path.exists(excel_path):
        return {"error": "File not found"}
    
    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
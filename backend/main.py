from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os
import uuid
import shutil
from pdf_parser import parse_ktu_results

app = FastAPI(title="KTU Result Processor API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UPLOAD_DIR = os.path.join(BASE_DIR, "data")

os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/upload")
async def upload_files(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):
    """Upload PDF and master file, then parse the PDF"""
    
    # Save PDF
    pdf_filename = f"{uuid.uuid4().hex}_result.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    
    # Save master file
    master_ext = os.path.splitext(master_file.filename)[1]
    master_filename = f"{uuid.uuid4().hex}_master{master_ext}"
    master_path = os.path.join(UPLOAD_DIR, master_filename)
    with open(master_path, "wb") as f:
        shutil.copyfileobj(master_file.file, f)
    
    # Parse the PDF
    results = parse_ktu_results(pdf_path)
    print(f"Parsed {len(results)} records from {pdf_file.filename}")

    # Get department summary
    dept_summary = {}
    for r in results:
        dept = r['department']
        if dept not in dept_summary:
            dept_summary[dept] = {'total': 0, 'pass': 0, 'fail': 0}
        dept_summary[dept]['total'] += 1
        if r['status'] == 'Pass':
            dept_summary[dept]['pass'] += 1
        else:
            dept_summary[dept]['fail'] += 1
    
    return {
        "status": "success",
        "message": f"Parsed {len(results)} records",
        "total_records": len(results),
        "departments": dept_summary,
        "sample_data": results[:5]
    }


@app.get("/static/styles.css")
def get_styles():
    css_path = os.path.join(FRONTEND_DIR, "styles.css")
    return FileResponse(css_path, media_type="text/css")


@app.get("/static/script.js")
def get_script():
    js_path = os.path.join(FRONTEND_DIR, "script.js")
    return FileResponse(js_path, media_type="application/javascript")


@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server at http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os, uuid, shutil

from pdf_parser import extract_text_from_pdf, parse_ktu_results

app = FastAPI(title="KTU Result Processor API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UPLOAD_DIR = os.path.join(BASE_DIR, "data")

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


@app.post("/upload")
async def upload_files(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):
    """
    Accept PDF and master file from frontend.
    Save them to disk for processing.
    """
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save PDF
    pdf_filename = f"{uuid.uuid4().hex}_result.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    
    try:
        with open(pdf_path, "wb") as f:
            shutil.copyfileobj(pdf_file.file, f)
    finally:
        await pdf_file.close()

    # Save master file
    master_filename = f"{uuid.uuid4().hex}_master{os.path.splitext(master_file.filename)[1]}"
    master_path = os.path.join(UPLOAD_DIR, master_filename)
    
    try:
        with open(master_path, "wb") as f:
            shutil.copyfileobj(master_file.file, f)
    finally:
        await master_file.close()

    return {
        "status": "success",
        "message": "Files uploaded successfully",
        "pdf_saved": pdf_filename,
        "master_saved": master_filename
    }

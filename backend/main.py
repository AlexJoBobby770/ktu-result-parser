from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import shutil

from pdf_parser import parse_pdf  

app = FastAPI(title="KTU Result Processor API")

FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")

os.makedirs(UPLOAD_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/")
async def serve_homepage():
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)


@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/upload")
async def upload_files(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):

    if not pdf_file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    if not master_file.filename.lower().endswith((".xlsx", ".xls", ".csv")):
        raise HTTPException(status_code=400, detail="Invalid master file")

    pdf_path = os.path.join(UPLOAD_DIR, pdf_file.filename)
    master_path = os.path.join(UPLOAD_DIR, master_file.filename)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    with open(master_path, "wb") as f:
        shutil.copyfileobj(master_file.file, f)

    try:
        result = parse_pdf(pdf_path, master_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {
        "message": "Files uploaded and processed successfully",
        "result": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

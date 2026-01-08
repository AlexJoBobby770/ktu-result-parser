from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pdf_parser import extract_text_from_pdf, parse_ktu_results
import os
import uuid
import shutil

app = FastAPI(title="KTU Result Processor API")


FRONTEND_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

@app.get("/")
async def serve_homepage():
    """
    Serve the main HTML page when user visits the root URL.
    This is the entry point of our web application.
    """
    index_path = os.path.join(FRONTEND_DIR, "index.html")
    return FileResponse(index_path)

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint to verify backend is running.
    Returns JSON with status message.
    """
    return {"status": "ok", "message": "Backend is running"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Preserve original name, but prefix with uuid to avoid collisions
    safe_name = os.path.basename(file.filename) or "upload"
    filename = f"{uuid.uuid4().hex}_{safe_name}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    text = extract_text_from_pdf("results.pdf")
    results = parse_ktu_results(text)


    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to save uploaded file")
    finally:
        await file.close()

    return {"status": "ok", "filename": filename, "saved_to": str(file_path)}

if __name__ == "__main__":
    import uvicorn
    print('localhost:8000')
    uvicorn.run("main:app", port=8000, reload=True)
    
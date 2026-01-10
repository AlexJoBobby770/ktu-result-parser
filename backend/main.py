from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
import os, uuid, shutil

app = FastAPI(title="KTU Result Processor API")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "..", "frontend")
UPLOAD_DIR = os.path.join(BASE_DIR, "data")


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/upload")
async def upload_files(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # Save PDF
    pdf_filename = f"{uuid.uuid4().hex}_result.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    await pdf_file.close()

    # Save master file
    master_ext = os.path.splitext(master_file.filename)[1]
    master_filename = f"{uuid.uuid4().hex}_master{master_ext}"
    master_path = os.path.join(UPLOAD_DIR, master_filename)
    with open(master_path, "wb") as f:
        shutil.copyfileobj(master_file.file, f)
    await master_file.close()

    return {
        "status": "success",
        "message": "Files uploaded successfully",
        "pdf_saved": pdf_filename,
        "master_saved": master_filename
    }


@app.get("/styles.css")
def get_styles():
    return FileResponse(os.path.join(FRONTEND_DIR, "styles.css"), media_type="text/css")


@app.get("/script.js")
def get_script():
    return FileResponse(os.path.join(FRONTEND_DIR, "script.js"), media_type="application/javascript")


@app.get("/")
def home():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server at http://localhost:8000")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
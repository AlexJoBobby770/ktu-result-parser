from fastapi import FastAPI, UploadFile, File
import os
import uuid
import shutil

from pdf_parser import parse_ktu_results

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# Folder where uploaded files will be stored
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/upload")
async def upload_result(
    pdf_file: UploadFile = File(...),
    master_file: UploadFile = File(...)
):
   
    pdf_name = f"{uuid.uuid4().hex}.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_name)

    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    master_name = f"{uuid.uuid4().hex}_{master_file.filename}"
    master_path = os.path.join(UPLOAD_DIR, master_name)

    with open(master_path, "wb") as f:
        shutil.copyfileobj(master_file.file, f)

    results = parse_ktu_results(pdf_path)


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
        "total_students": len(results),
        "department_summary": summary,
        "sample": results[:5]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True)

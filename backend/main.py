# backend/main.py
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
from datetime import timedelta
from typing import Optional

from pdf_parser import parse_ktu_results
from excel_generator import generate_excel_report
from excel_generator_v2 import generate_merged_excel
from internal_parser import parse_internal_marks
from data_merger import merge_results
from models import ExternalRecord, grade_to_marks

from auth import (
    UserLogin, UserRegister, Token,
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from database.database import create_user, get_user_by_username

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


# ==================== AUTH ROUTES ====================

@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    if get_user_by_username(user.username):
        raise HTTPException(status_code=400, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    if not create_user(user.username, user.email, hashed_password):
        raise HTTPException(status_code=500, detail="Could not create user")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = get_user_by_username(user.username)
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    user = get_user_by_username(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": user["username"], "email": user["email"]}


# ==================== PUBLIC ROUTES ====================

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


# ==================== FILE PROCESSING ====================

@app.post("/upload")
async def upload_result(
    pdf_file: UploadFile = File(...),
    internal_file: Optional[UploadFile] = File(None),
    current_user: str = Depends(get_current_user)
):
    """Process KTU result PDF with optional internal marks"""
    
    session_id = uuid.uuid4().hex[:8]
    external_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_external.pdf")
    
    # Save external PDF
    with open(external_pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    await pdf_file.close()

    try:
        print(f"📄 Parsing external PDF: {pdf_file.filename}")
        external_students = parse_ktu_results(external_pdf_path)
        
        excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
        
        # CASE 1: External only (simple format)
        if internal_file is None:
            print("📊 Generating simple Excel...")
            generate_excel_report(external_students, excel_path)
            
            return {
                "message": f"Processed {len(external_students)} students",
                "session_id": session_id,
                "total_students": len(external_students),
                "passed_students": sum(1 for s in external_students if s.get("status") == "Pass"),
                "has_internal_marks": False
            }
        
        # CASE 2: Both PDFs (beautiful format)
        else:
            print(f"📄 Parsing internal PDF: {internal_file.filename}")
            internal_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_internal.pdf")
            
            with open(internal_pdf_path, "wb") as f:
                shutil.copyfileobj(internal_file.file, f)
            await internal_file.close()
            
            # Parse and merge
            internal_records, name_mapping = parse_internal_marks(internal_pdf_path)
            
            external_records = []
            for student in external_students:
                for subject_code, grade in student["subjects"].items():
                    external_records.append(ExternalRecord(
                        register_no=student["register_no"],
                        subject_code=subject_code,
                        grade=grade,
                        external_mark=grade_to_marks(grade)
                    ))
            
            print("🔄 Merging data...")
            merged_records, merge_stats = merge_results(
                internal_records, external_records, name_mapping
            )
            
            print("✨ Generating beautiful Excel...")
            generate_merged_excel(merged_records, excel_path)
            
            return {
                "message": f"Processed {merge_stats['unique_students']} students with internal marks",
                "session_id": session_id,
                "total_students": merge_stats['unique_students'],
                "passed_students": sum(1 for r in merged_records if r.result == "Pass"),
                "has_internal_marks": True,
                "merge_stats": merge_stats
            }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.get("/download/{session_id}")
def download_excel(session_id: str, current_user: str = Depends(get_current_user)):
    """Download processed Excel file"""
    
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
    uvicorn.run("main:app", reload=True, port=8000)
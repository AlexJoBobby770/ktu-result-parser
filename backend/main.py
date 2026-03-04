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
    internal_file: UploadFile = File(None),
    current_user: dict = Depends(get_current_user)
):
    """
    Upload and process result files
    - pdf_file: External KTU results (required)
    - internal_file: Internal marks PDF (optional)
    """
    session_id = str(uuid.uuid4())[:8]
    
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
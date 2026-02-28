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
from excel_generator import generate_excel_report  # Keep old generator as fallback
from excel_generator_v2 import generate_merged_excel  # New beautiful generator
from internal_parser import parse_internal_marks
from data_merger import merge_results
from models import ExternalRecord

from auth import (
    UserLogin, UserRegister, Token,
    get_password_hash, verify_password, create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
)
from database.database import (
    save_session, get_recent_sessions, get_session,
    create_user, get_user_by_username
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
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
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    hashed_password = get_password_hash(user.password)
    success = create_user(user.username, user.email, hashed_password)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = get_user_by_username(user.username)

    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    user = get_user_by_username(current_user)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"]
    }


# ==================== PUBLIC ROUTES ====================

@app.get("/health")
def health():
    return {"status": "ok", "message": "Backend is running"}


# ==================== PROTECTED ROUTES ====================

@app.post("/upload")
async def upload_result(
    pdf_file: UploadFile = File(..., description="KTU External Results PDF"),
    internal_file: Optional[UploadFile] = File(None, description="Internal Marks PDF (optional)"),
    current_user: str = Depends(get_current_user)
):
    """
    Upload external results PDF (required) and optionally internal marks PDF.
    
    - If only external PDF: Uses old excel_generator (simple format)
    - If both PDFs: Uses excel_generator_v2 (beautiful 5-sheet format)
    """
    session_id = uuid.uuid4().hex[:8]

    # Save external results PDF
    external_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_external.pdf")
    with open(external_pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    await pdf_file.close()

    try:
        # Parse external results (always required)
        print(f"📄 Parsing external PDF: {pdf_file.filename}")
        external_students = parse_ktu_results(external_pdf_path)
        
        total_students = len(external_students)
        total_departments = len(set(s.get("department", "OTHER") for s in external_students))
        
        excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
        
        # CASE 1: Only external PDF (use old simple generator)
        if internal_file is None:
            print("📊 Generating simple Excel (external only)...")
            
            # Use old generator
            generate_excel_report(external_students, excel_path)
            
            passed_students = sum(1 for s in external_students if s.get("status") == "Pass")
            
            # Save session
            save_session(
                session_id=session_id,
                filename=pdf_file.filename,
                total_students=total_students,
                total_departments=total_departments,
                username=current_user
            )
            
            return {
                "message": f"Successfully processed {total_students} students (external only)",
                "session_id": session_id,
                "total_students": total_students,
                "passed_students": passed_students,
                "has_internal_marks": False,
                "excel_ready": True
            }
        
        # CASE 2: Both PDFs provided (use new beautiful generator)
        else:
            print(f"📄 Parsing internal PDF: {internal_file.filename}")
            
            # Save internal PDF
            internal_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_internal.pdf")
            with open(internal_pdf_path, "wb") as f:
                shutil.copyfileobj(internal_file.file, f)
            await internal_file.close()
            
            # Parse internal marks
            internal_records, name_mapping = parse_internal_marks(internal_pdf_path)
            
            # Convert external students to ExternalRecord objects
            external_records = []
            for student in external_students:
                for subject_code, grade in student["subjects"].items():
                    from models import grade_to_marks
                    external_records.append(ExternalRecord(
                        register_no=student["register_no"],
                        subject_code=subject_code,
                        grade=grade,
                        external_mark=grade_to_marks(grade)
                    ))
            
            # Merge data
            print("🔄 Merging internal + external data...")
            merged_records, merge_stats = merge_results(
                internal_records,
                external_records,
                name_mapping
            )
            
            # Generate beautiful Excel
            print("✨ Generating beautiful Excel report...")
            generate_merged_excel(merged_records, excel_path)
            
            # Calculate summary
            unique_students = merge_stats['unique_students']
            passed_records = sum(1 for r in merged_records if r.result == "Pass")
            
            # Save session
            save_session(
                session_id=session_id,
                filename=f"{pdf_file.filename} + {internal_file.filename}",
                total_students=unique_students,
                total_departments=len(set(r.department for r in merged_records)),
                username=current_user
            )
            
            return {
                "message": f"Successfully processed {unique_students} students with internal marks",
                "session_id": session_id,
                "total_students": unique_students,
                "passed_students": passed_records,
                "merge_stats": merge_stats,
                "has_internal_marks": True,
                "excel_ready": True
            }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@app.get("/download/{session_id}")
def download_excel(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    session = get_session(session_id, username=current_user)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found or you don't have permission"
        )

    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")

    if not os.path.exists(excel_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Excel file not found"
        )

    return FileResponse(
        excel_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=f"KTU_Results_{session_id}.xlsx"
    )


@app.get("/sessions")
def get_sessions(current_user: str = Depends(get_current_user)):
    sessions = get_recent_sessions(limit=10, username=current_user)
    return {"sessions": sessions}


@app.get("/sessions/{session_id}")
def get_session_details(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    session = get_session(session_id, username=current_user)

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )

    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    session["excel_available"] = os.path.exists(excel_path)

    return session


if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting server at http://localhost:8000")
    print("📝 Frontend compatible mode:")
    print("   - Single PDF upload: Simple Excel format")
    print("   - Two PDF upload (future): Beautiful 5-sheet format")
    uvicorn.run("main:app", reload=True, port=8000)
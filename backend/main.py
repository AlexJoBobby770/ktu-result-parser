# backend/main.py
import sys
import os

# Fix path so Python can find database/ folder (one level up from backend/)
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uuid
import shutil
from datetime import timedelta
from internal_parser import parse_internal_marks
from data_merger import merge_results

# Relative imports removed — now plain imports since we cd into backend/
from pdf_parser import parse_ktu_results
from excel_generator import generate_excel_report
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
        "https://your-app.vercel.app",   # ← replace with your actual Vercel URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Use absolute paths so files save correctly regardless of where uvicorn runs from
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
    internal_file: UploadFile = File(..., description="Internal Marks PDF"),
    current_user: str = Depends(get_current_user)
):
    """
    Upload both external results PDF and internal marks PDF,
    merge them, and generate comprehensive Excel report
    """
    session_id = uuid.uuid4().hex[:8]

    # Save external results PDF
    external_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_external.pdf")
    with open(external_pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    # Save internal marks PDF
    internal_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_internal.pdf")
    with open(internal_pdf_path, "wb") as f:
        shutil.copyfileobj(internal_file.file, f)

    try:
        # Parse external results
        external_records = parse_ktu_results(external_pdf_path)
        
        # Parse internal marks
        internal_records, name_mapping = parse_internal_marks(internal_pdf_path)
        
        # Merge data
        merged_records, merge_stats = merge_results(
            internal_records,
            external_records,
            name_mapping
        )
        
        # Generate Excel
        excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
        generate_excel_report(merged_records, excel_path)
        
        # Calculate summary
        total_students = merge_stats['unique_students']
        passed_students = sum(1 for r in merged_records if r.result == "Pass")
        
        # Save session
        save_session(
            session_id=session_id,
            filename=f"{pdf_file.filename} + {internal_file.filename}",
            total_students=total_students,
            total_departments=len(set(r.department for r in merged_records)),
            username=current_user
        )
        
        return {
            "message": f"Successfully processed {total_students} students",
            "session_id": session_id,
            "total_students": total_students,
            "passed_students": passed_students,
            "merge_stats": merge_stats,
            "excel_ready": True
        }
        
    except Exception as e:
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
    uvicorn.run("main:app", reload=True, port=8000)
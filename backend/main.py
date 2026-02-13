# backend/main.py
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import shutil
from datetime import timedelta

from .pdf_parser import parse_ktu_results
from .excel_generator import generate_excel_report
from .auth import (
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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "data"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)


# ==================== AUTH ROUTES ====================

@app.post("/register", response_model=Token)
async def register(user: UserRegister):
    """Register a new user"""
    # Check if user already exists
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Hash password and create user
    hashed_password = get_password_hash(user.password)
    success = create_user(user.username, user.email, hashed_password)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not create user"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    """Login and get access token"""
    # Get user from database
    db_user = get_user_by_username(user.username)
    
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
async def get_me(current_user: str = Depends(get_current_user)):
    """Get current user info"""
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
    pdf_file: UploadFile = File(...),
    current_user: str = Depends(get_current_user)
):
    """Upload and process PDF (requires authentication)"""
    session_id = uuid.uuid4().hex[:8]

    # Save PDF
    pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}.pdf")
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)
    
    # Parse PDF
    results = parse_ktu_results(pdf_path)
    
    # Generate Excel
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    generate_excel_report(results, excel_path)

    # Calculate summary
    summary = {}
    for student in results:
        dept = student["department"]
        if dept not in summary:
            summary[dept] = {"total_students": 0, "with_arrears": 0}
        summary[dept]["total_students"] += 1
        if student["status"] == "Fail":
            summary[dept]["with_arrears"] += 1
    
    # Save session with username
    save_session(
        session_id=session_id,
        filename=pdf_file.filename,
        total_students=len(results),
        total_departments=len(summary),
        username=current_user
    )
    
    return {
        "message": f"Successfully parsed {len(results)} students",
        "session_id": session_id,
        "total_students": len(results),
        "departments": summary,
        "excel_ready": True
    }


@app.get("/download/{session_id}")
def download_excel(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Download Excel file (requires authentication and ownership)"""
    # Check if session exists and belongs to user
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
    """Get user's recent uploads (requires authentication)"""
    sessions = get_recent_sessions(limit=10, username=current_user)
    return {"sessions": sessions}


@app.get("/sessions/{session_id}")
def get_session_details(
    session_id: str,
    current_user: str = Depends(get_current_user)
):
    """Get session details (requires authentication and ownership)"""
    session = get_session(session_id, username=current_user)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if Excel file still exists
    excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
    session["excel_available"] = os.path.exists(excel_path)
    
    return session


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", reload=True, port=8000)
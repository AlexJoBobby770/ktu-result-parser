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

# Import new modules
from internal_parser import parse_internal_marks
from data_merger import merge_results
from pdf_parser import parse_ktu_results
from excel_generator_v2 import generate_merged_excel  # NEW!

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
    internal_file: UploadFile = File(None, description="Internal Marks PDF (optional)"),
    current_user: str = Depends(get_current_user)
):
    """
    Upload external results PDF (required) and internal marks PDF (optional).
    If internal marks provided, generates merged report with names.
    If not, generates basic report with just external marks.
    """
    session_id = uuid.uuid4().hex[:8]

    # Save external results PDF
    external_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_external.pdf")
    with open(external_pdf_path, "wb") as f:
        shutil.copyfileobj(pdf_file.file, f)

    try:
        # Parse external results
        external_records = parse_ktu_results(external_pdf_path)
        
        if internal_file:
            # Save internal marks PDF
            internal_pdf_path = os.path.join(UPLOAD_DIR, f"{session_id}_internal.pdf")
            with open(internal_pdf_path, "wb") as f:
                shutil.copyfileobj(internal_file.file, f)
            
            # Parse internal marks
            internal_records, name_mapping = parse_internal_marks(internal_pdf_path)
            
            # Merge data
            merged_records, merge_stats = merge_results(
                internal_records,
                external_records,
                name_mapping
            )
            
            # Generate enhanced Excel
            excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
            generate_merged_excel(merged_records, excel_path)
            
            total_students = merge_stats['unique_students']
            passed_records = sum(1 for r in merged_records if r.result == "Pass")
            
            save_session(
                session_id=session_id,
                filename=f"{pdf_file.filename} + {internal_file.filename}",
                total_students=total_students,
                total_departments=len(set(r.department for r in merged_records)),
                username=current_user
            )
            
            return {
                "message": f"Successfully processed {total_students} students with merged data",
                "session_id": session_id,
                "total_students": total_students,
                "total_records": len(merged_records),
                "passed_records": passed_records,
                "merge_stats": merge_stats,
                "excel_ready": True,
                "has_internal_marks": True
            }
        
        else:
            # No internal marks - just external results
            # Convert ExternalRecord to simple dict for old excel generator
            from excel_generator import generate_excel_report
            
            students = {}
            for record in external_records:
                if record.register_no not in students:
                    students[record.register_no] = {
                        "register_no": record.register_no,
                        "name": "",
                        "department": get_department_from_regno(record.register_no),
                        "subjects": {},
                        "status": "Pass"
                    }
                students[record.register_no]["subjects"][record.subject_code] = record.grade
                if record.grade in ["F", "FE", "AB", "Absent", "Withheld"]:
                    students[record.register_no]["status"] = "Fail"
            
            excel_path = os.path.join(OUTPUT_DIR, f"{session_id}_results.xlsx")
            generate_excel_report(list(students.values()), excel_path)
            
            total_students = len(students)
            
            save_session(
                session_id=session_id,
                filename=pdf_file.filename,
                total_students=total_students,
                total_departments=len(set(s["department"] for s in students.values())),
                username=current_user
            )
            
            return {
                "message": f"Successfully processed {total_students} students (external marks only)",
                "session_id": session_id,
                "total_students": total_students,
                "excel_ready": True,
                "has_internal_marks": False
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


def get_department_from_regno(regno: str) -> str:
    """Extract department from register number"""
    regno = regno.upper()
    if "EE" in regno and "EEE" not in regno:
        return "EEE"
    if "EC" in regno:
        return "ECE"
    if "CS" in regno:
        return "CSE"
    if "ME" in regno:
        return "ME"
    if "CE" in regno and "ECE" not in regno:
        return "CE"
    return "OTHER"


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
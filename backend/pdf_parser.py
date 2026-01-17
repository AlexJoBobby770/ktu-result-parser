import re
from typing import List, Dict
import PyPDF2


# ---------- PDF TEXT EXTRACTION ----------

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


# ---------- MAIN PARSER ----------

def parse_ktu_results(pdf_path: str):
    text = extract_text_from_pdf(pdf_path)
    students = []

    current_department = None
    current_usn = None
    current_subjects = {}

    for line in text.splitlines():
        line = line.strip()

        # 1. Detect department
        if "ENGINEERING" in line and "[FULL TIME]" in line.upper():
            current_department = line.split("[")[0].strip()
            continue

        # 2. Detect USN at line start
        usn_match = re.match(r"\b[A-Z]{3}\d{2}[A-Z]{2}\d{3}\b", line)

        if usn_match:
            # 🔑 SAVE PREVIOUS STUDENT FIRST
            if current_usn and current_subjects:
                has_fail = any(
                    g in ["F", "FE", "AB", "Absent", "Withheld"]
                    for g in current_subjects.values()
                )
                students.append({
                    "register_no": current_usn,
                    "department": current_department,
                    "subjects": current_subjects,
                    "status": "Fail" if has_fail else "Pass"
                })

            # 🔄 START NEW STUDENT
            current_usn = usn_match.group()
            current_subjects = {}

        # 3. Extract subjects (same or next line)
        subject_matches = re.findall(
            r"([A-Z]{2,6}\d{3})\(([^)]+)\)",
            line
        )

        for code, grade in subject_matches:
            current_subjects[code] = grade

    # ✅ SAVE LAST STUDENT (VERY IMPORTANT)
    if current_usn and current_subjects:
        has_fail = any(
            g in ["F", "FE", "AB", "Absent", "Withheld"]
            for g in current_subjects.values()
        )
        students.append({
            "register_no": current_usn,
            "department": current_department,
            "subjects": current_subjects,
            "status": "Fail" if has_fail else "Pass"
        })

    return students



# ---------- QUICK CLI TEST (OPTIONAL) ----------

if __name__ == "__main__":
    import sys

    pdf = sys.argv[1]
    results = parse_ktu_results(pdf)

    print(f"Total students parsed: {len(results)}\n")
    print("First 3 students:\n")

    for s in results[:300]:
        print(s)

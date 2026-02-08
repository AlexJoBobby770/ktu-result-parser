import re
from typing import List, Dict
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def parse_ktu_results(pdf_path: str):

    text = extract_text_from_pdf(pdf_path)
    students = []

    current_department = None
    current_usn = None
    current_subjects = {}

    for line in text.splitlines():
        line = line.strip()

     
        if "ENGINEERING" in line and "[FULL TIME]" in line.upper():
            current_department = line.split("[")[0].strip()
            continue

        
        usn_match = re.match(r"\b[A-Z]{3}\d{2}[A-Z]{2}\d{3}\b", line)

        if usn_match:
     
            if current_usn and current_subjects:
                has_fail = any(
                    g in ["F", "FE", "AB", "Absent", "Withheld"]
                    for g in current_subjects.values()
                )
                students.append({
                    "register_no": current_usn,
                    "name": "",  
                    "department": current_department,
                    "subjects": current_subjects,
                    "status": "Fail" if has_fail else "Pass"
                })

            current_usn = usn_match.group()
            current_subjects = {}

        subject_matches = re.findall(r"([A-Z]{2,6}\d{3})\(([^)]+)\)", line)
        for code, grade in subject_matches:
            current_subjects[code] = grade

    if current_usn and current_subjects:
        has_fail = any(
            g in ["F", "FE", "AB", "Absent", "Withheld"]
            for g in current_subjects.values()
        )
        students.append({
            "register_no": current_usn,
            "name": "",
            "department": current_department,
            "subjects": current_subjects,
            "status": "Fail" if has_fail else "Pass"
        })

    return students


if __name__ == "__main__":
    import sys
    pdf = sys.argv[1] if len(sys.argv) > 1 else "../master .pdf"
    
    results = parse_ktu_results(pdf)
    print(f"✅ Parsed {len(results)} students\n")
    
    for s in results[:3]:
        print(s)
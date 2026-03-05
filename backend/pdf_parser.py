# backend/pdf_parser.py
import re
from typing import List
import PyPDF2
from models import ExternalRecord


def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def parse_ktu_results(pdf_path: str) -> List[ExternalRecord]:
    """
    Parse KTU result PDF and return list of ExternalRecord objects
    containing register_no, subject_code and grade
    """

    text = extract_text_from_pdf(pdf_path)
    records = []

    current_usn = None
    current_subjects = {}

    for line in text.splitlines():
        line = line.strip()

        # Detect register number
        usn_match = re.match(r"\b[A-Z]{3}\d{2}[A-Z]{2}\d{3}\b", line)

        if usn_match:
            # Save previous student
            if current_usn and current_subjects:
                for subj_code, grade in current_subjects.items():
                    records.append(
                        ExternalRecord(
                            register_no=current_usn,
                            subject_code=subj_code,
                            grade=grade
                        )
                    )

            current_usn = usn_match.group()
            current_subjects = {}

        # Extract subject grades
        subject_matches = re.findall(r"([A-Z]{2,6}\d{3})\(([^)]+)\)", line)

        for code, grade in subject_matches:
            current_subjects[code] = grade

    # Save last student
    if current_usn and current_subjects:
        for subj_code, grade in current_subjects.items():
            records.append(
                ExternalRecord(
                    register_no=current_usn,
                    subject_code=subj_code,
                    grade=grade
                )
            )

    return records


def get_department_from_regno(regno: str) -> str:
    """Extract department from register number"""
    regno = regno.upper()

    if "CS" in regno:
        return "CSE"
    if "EC" in regno:
        return "ECE"
    if "EE" in regno and "EEE" not in regno:
        return "EEE"
    if "ME" in regno:
        return "ME"
    if "CE" in regno and "ECE" not in regno:
        return "CE"

    return "OTHER"


if __name__ == "__main__":
    import sys

    pdf = sys.argv[1] if len(sys.argv) > 1 else "master_.pdf"

    results = parse_ktu_results(pdf)

    print(f"✅ Parsed {len(results)} records\n")

    for r in results[:5]:
        print(f"{r.register_no} - {r.subject_code}: {r.grade}")
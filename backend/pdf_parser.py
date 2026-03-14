# backend/pdf_parser.py
import re
import pdfplumber
from backend.models import ExternalRecord, get_department


# Regex: matches USN at start of a line
# Covers AIK, LAIK, SGI, SPT, GWE, MZW prefixes seen in real PDFs
USN_PATTERN   = re.compile(r'^([A-Z]+\d{2}[A-Z]{2}\d{3})', re.MULTILINE)
GRADE_PATTERN = re.compile(r'([A-Z]{2,4}\d{3})\(([^)]+)\)')

DEPARTMENT_MAP = {
    "CIVIL ENGINEERING":              "CE",
    "MECHANICAL ENGINEERING":         "ME",
    "ELECTRICAL AND ELECTRONICS":     "EEE",
    "ELECTRONICS & COMMUNICATION":    "ECE",
    "COMPUTER SCIENCE":               "CSE",
}

DEPT_HEADER = re.compile(
    r'(CIVIL ENGINEERING|MECHANICAL ENGINEERING|'
    r'ELECTRICAL AND ELECTRONICS ENGINEERING|'
    r'ELECTRONICS & COMMUNICATION ENGG|'
    r'COMPUTER SCIENCE & ENGINEERING)'
    r'\[Full Time\]',
    re.IGNORECASE
)


def extract_text(pdf_path: str) -> str:
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"
    return full_text


def split_by_department(text: str) -> dict:
    matches = list(DEPT_HEADER.finditer(text))
    departments = {}

    for i, match in enumerate(matches):
        keyword = match.group(1).upper()
        dept = None
        for key, short in DEPARTMENT_MAP.items():
            if key in keyword:
                dept = short
                break
        if not dept:
            continue

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        departments[dept] = text[start:end]

    return departments


def parse_department_block(dept: str, block: str) -> list:
    records = []
    usn_matches = list(USN_PATTERN.finditer(block))

    for i, usn_match in enumerate(usn_matches):
        usn = usn_match.group(1)
        start = usn_match.start()
        end = usn_matches[i + 1].start() if i + 1 < len(usn_matches) else len(block)
        student_line = block[start:end]

        for course_code, grade in GRADE_PATTERN.findall(student_line):
            records.append(ExternalRecord(
                usn=usn,
                department=dept,
                course_code=course_code,
                grade=grade.strip(),
            ))

    return records


def parse_ktu_pdf(pdf_path: str) -> list:
    """
    Main entry point.
    Returns flat list of ExternalRecord — one per (student, subject).
    """
    text = extract_text(pdf_path)
    departments = split_by_department(text)
    all_records = []

    for dept, block in departments.items():
        records = parse_department_block(dept, block)
        all_records.extend(records)
        print(f"  {dept}: {len(records)} records")

    print(f"  TOTAL: {len(all_records)} records across {len(departments)} departments")
    return all_records
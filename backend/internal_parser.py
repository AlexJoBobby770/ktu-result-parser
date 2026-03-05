import re
import pdfplumber
from typing import List, Dict, Tuple
from models import InternalRecord


# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    return text


# -----------------------------
# SUBJECT METADATA PARSER
# -----------------------------
def parse_subject_mapping(text: str) -> Dict[str, Tuple[str, str]]:
    """
    Extract subject code, subject name, and faculty name
    from the footer section of the PDF.
    """

    subject_map = {}

    # Example line:
    # 1 MCN401 INDUSTRIAL SAFETY ENGINEERING Ms. Shruthi Chandran
    pattern = re.compile(
        r"^\d+\s+([A-Z]{2,4}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+.+)$"
    )

    for line in text.split("\n"):
        line = line.strip()

        m = pattern.match(line)
        if m:
            code = m.group(1).strip()
            subject_name = m.group(2).strip()
            faculty_name = m.group(3).strip()

            if code not in subject_map:
                subject_map[code] = (subject_name, faculty_name)
            else:
                existing_subject, existing_faculty = subject_map[code]
                subject_map[code] = (
                    existing_subject,
                    f"{existing_faculty}, {faculty_name}",
                )

    return subject_map


# -----------------------------
# MAIN INTERNAL MARK PARSER
# -----------------------------
def parse_internal_marks(pdf_path: str) -> Tuple[List[InternalRecord], Dict[str, str]]:

    text = extract_text_from_pdf(pdf_path)

    # DEBUG: show end of PDF text
    print("=== LAST 500 CHARS ===")
    print(repr(text[-500:]))
    print("=== END ===")

    subject_map = parse_subject_mapping(text)

    if not subject_map:
        raise ValueError("Could not extract subject metadata from footer")

    subject_codes = list(subject_map.keys())
    subject_count = len(subject_codes)

    # Cut before footer to avoid garbage parsing
    cutoff = text.find("Class Average")
    if cutoff > 0:
        text = text[:cutoff]

    tokens = text.split()

    records: List[InternalRecord] = []
    name_mapping: Dict[str, str] = {}

    reg_pattern = re.compile(r"^(AIK|LAIK|SGI)\d{2}[A-Z]{2}\d{3}$")

    i = 0
    total_tokens = len(tokens)

    while i < total_tokens:

        token = tokens[i]

        if reg_pattern.match(token):

            regno = token
            i += 1

            # -----------------------------
            # Student Name Extraction
            # -----------------------------
            name_parts = []

            while i < total_tokens and not re.match(r"^\d+(\.\d+)?$", tokens[i]):
                name_parts.append(tokens[i])
                i += 1

            student_name = " ".join(name_parts).strip()

            name_mapping[regno] = student_name

            # -----------------------------
            # Extract subject marks
            # -----------------------------
            marks = []

            for _ in range(subject_count):

                # Skip elective marker "*"
                # Handle elective "* 0"
                if i < total_tokens and tokens[i] == "*":
                    i += 2
                    marks.append(0)
                    continue

                # Read mark (marks are integers, attendance has decimals)
                if i < total_tokens and re.match(r"^\d+$", tokens[i]):
                    marks.append(int(tokens[i]))
                    i += 1
                else:
                    marks.append(0)

                # Skip attendance %
                if i < total_tokens and re.match(r"^\d+(\.\d+)?$", tokens[i]):
                    i += 1

            # Skip "Total" column
            if i < total_tokens and re.match(r"^\d+(\.\d+)?$", tokens[i]):
                i += 1

            # -----------------------------
            # Build records
            # -----------------------------
            for idx, subject_code in enumerate(subject_codes):

                subject_name, faculty_name = subject_map.get(
                    subject_code, (subject_code, "N/A")
                )

                records.append(
                    InternalRecord(
                        register_no=regno,
                        student_name=student_name,
                        subject_code=subject_code,
                        subject_name=subject_name,
                        faculty_name=faculty_name,
                        internal_mark=marks[idx] if idx < len(marks) else 0,
                    )
                )

        else:
            i += 1

    return records, name_mapping


# -----------------------------
# DATA VALIDATION
# -----------------------------
def validate_internal_data(records: List[InternalRecord]) -> Dict:

    if not records:
        return {"valid": False, "error": "No records found"}

    invalid_marks = [r for r in records if r.internal_mark < 0 or r.internal_mark > 50]

    unique_students = set(r.register_no for r in records)
    unique_subjects = set(r.subject_code for r in records)
    unique_faculty = set(r.faculty_name for r in records)

    subject_stats = {}

    for record in records:

        if record.subject_code not in subject_stats:
            subject_stats[record.subject_code] = {
                "name": record.subject_name,
                "faculty": record.faculty_name,
                "count": 0,
                "total": 0,
                "max": 0,
                "min": 50,
            }

        stats = subject_stats[record.subject_code]

        stats["count"] += 1
        stats["total"] += record.internal_mark
        stats["max"] = max(stats["max"], record.internal_mark)
        stats["min"] = min(stats["min"], record.internal_mark)

    for code in subject_stats:
        stats = subject_stats[code]
        stats["average"] = round(stats["total"] / stats["count"], 2)

    return {
        "valid": len(invalid_marks) == 0,
        "total_records": len(records),
        "unique_students": len(unique_students),
        "unique_subjects": len(unique_subjects),
        "unique_faculty": len(unique_faculty),
        "invalid_marks_count": len(invalid_marks),
        "students": sorted(list(unique_students))[:5],
        "subjects": {code: stats["name"] for code, stats in subject_stats.items()},
        "subject_stats": subject_stats,
    }


# -----------------------------
# CLI TEST
# -----------------------------
if __name__ == "__main__":

    import sys

    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "Sessionals_S7_CSE.pdf"

    print(f"📄 Parsing: {pdf_path}\n")

    records, name_map = parse_internal_marks(pdf_path)

    print(f"✅ Found {len(records)} internal mark records")
    print(f"✅ Found {len(name_map)} students\n")

    stats = validate_internal_data(records)

    print("📊 Validation Stats:")
    print(f"  - Total Records: {stats['total_records']}")
    print(f"  - Unique Students: {stats['unique_students']}")
    print(f"  - Unique Subjects: {stats['unique_subjects']}")

    for code, name in stats["subjects"].items():
        s = stats["subject_stats"][code]
        print(f"  - {code}: {name} | Avg: {s['average']}, Max: {s['max']}, Min: {s['min']}")

    for regno in stats["students"]:
        print(f"  - {regno}: {name_map[regno]}")
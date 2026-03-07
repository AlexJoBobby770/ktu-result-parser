# backend/internal_parser.py
import re
import pdfplumber
from models import InternalRecord


# Matches the footer course table lines like:
# 1 MCN401 INDUSTRIAL SAFETY ENGINEERING Ms. Shruthi Chandran
FOOTER_PATTERN = re.compile(
    r'^\d+\s+([A-Z]{2,4}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+\S.+)$'
)

# USN pattern - same prefixes as KTU PDF
USN_PATTERN = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW)\d{2}[A-Z]{2}\d{3})$')


def extract_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def parse_subject_footer(text: str) -> dict:
    """
    Parse the footer table at the bottom of the sessional PDF.
    Returns { "CST401": ("ARTIFICIAL INTELLIGENCE", "Ms. NISY JOHN PANICKER"), ... }
    One entry per unique subject code (multiple faculty lines are merged).
    """
    subject_map = {}

    for line in text.split("\n"):
        m = FOOTER_PATTERN.match(line.strip())
        if not m:
            continue

        code = m.group(1).strip()
        name = m.group(2).strip()
        faculty = m.group(3).strip()

        if code not in subject_map:
            subject_map[code] = (name, faculty)
        else:
            # Multiple faculty for same subject — append name
            existing_name, existing_faculty = subject_map[code]
            subject_map[code] = (existing_name, f"{existing_faculty}, {faculty}")

    return subject_map


def parse_sessional_pdf(pdf_path: str) -> tuple:
    """
    Parse the college sessional marks PDF.

    Returns:
        records     : list of InternalRecord
        name_mapping: { usn: student_name }

    How electives work in the PDF:
        Subjects are listed left-to-right in the header row.
        Each subject has TWO columns: Mark and Att%.
        For a skipped elective the Mark column contains '*'
        and the Att% column contains a number (0 or 100).
        We use elected=False for those records and internal_mark=0.
    """
    text = extract_text(pdf_path)

    # Cut text before footer stats so "Class Average" etc. don't confuse parsing
    cutoff = text.find("Class Average")
    body = text[:cutoff] if cutoff > 0 else text

    # Parse footer AFTER cutoff to get subject metadata
    subject_map = parse_subject_footer(text)

    if not subject_map:
        raise ValueError(
            "Could not find subject footer table in sessional PDF. "
            "Check that the PDF has the '# Course Code ...' section."
        )

    subject_codes = list(subject_map.keys())
    subject_count = len(subject_codes)

    records = []
    name_mapping = {}

    tokens = body.split()
    i = 0
    total = len(tokens)

    while i < total:
        token = tokens[i]

        # Skip roll number (pure integer)
        if re.match(r'^\d{1,3}$', token):
            i += 1
            continue

        # Detect USN
        if not USN_PATTERN.match(token):
            i += 1
            continue

        usn = token
        i += 1

        # --- Extract student name ---
        # Name tokens are uppercase alphabetic words (may include spaces)
        # Stop when we hit a number (first mark value)
        name_parts = []
        while i < total and not re.match(r'^\d+(\.\d+)?$', tokens[i]):
            name_parts.append(tokens[i])
            i += 1
        student_name = " ".join(name_parts).strip()
        name_mapping[usn] = student_name

        # --- Extract marks for each subject in order ---
        marks = []    # list of (mark_int, elected_bool)

        for _ in range(subject_count):
            if i >= total:
                marks.append((0, False))
                continue

            if tokens[i] == "*":
                # Elective NOT chosen by student
                i += 1  # skip '*'
                if i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    i += 1  # skip the attendance number that follows *
                marks.append((0, False))
            else:
                # Normal subject: mark then att%
                mark_val = 0
                if re.match(r'^\d+$', tokens[i]):
                    mark_val = int(tokens[i])
                    i += 1
                # Skip attendance %
                if i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    i += 1
                marks.append((mark_val, True))

        # Skip Total column (one final integer)
        if i < total and re.match(r'^\d+$', tokens[i]):
            i += 1

        # Build InternalRecord for each subject
        for idx, code in enumerate(subject_codes):
            subject_name, faculty_name = subject_map[code]
            mark, elected = marks[idx] if idx < len(marks) else (0, False)

            records.append(InternalRecord(
                usn=usn,
                student_name=student_name,
                course_code=code,
                subject_name=subject_name,
                faculty_name=faculty_name,
                internal_mark=mark,
                elected=elected,
            ))

    return records, name_mapping
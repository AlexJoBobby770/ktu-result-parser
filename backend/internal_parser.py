# backend/internal_parser.py
import re
import pdfplumber

try:
    from backend.models import InternalRecord
except ModuleNotFoundError:
    from models import InternalRecord

# Matches a KTU-style course code standing alone (used as a guard)
SUBJECT_CODE = re.compile(r'^[A-Z]{2,8}\d{3}$')

# Primary footer pattern — requires Ms./Mr./Dr. honorific
FOOTER_PATTERN = re.compile(
    r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+\S.+)$'
)

# Fallback footer pattern — for lab entries where faculty have no honorific
FOOTER_FALLBACK = re.compile(
    r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+([A-Z][A-Za-z\s\.]+)$'
)

# FIX: Added MET prefix to USN pattern
USN_PATTERN = re.compile(
    r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2}\d{3})$'
)


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

    Tries FOOTER_PATTERN first (requires Ms./Mr./Dr. honorific).
    Falls back to FOOTER_FALLBACK for lab entries where faculty have no honorific.
    """
    subject_map = {}

    for line in text.split("\n"):
        stripped = line.strip()
        m = FOOTER_PATTERN.match(stripped)
        if not m:
            m = FOOTER_FALLBACK.match(stripped)
        if not m:
            continue
        # Guard: group(1) must actually look like a subject code
        if not SUBJECT_CODE.match(m.group(1).strip()):
            continue

        code    = m.group(1).strip()
        name    = m.group(2).strip()
        faculty = m.group(3).strip()

        if code not in subject_map:
            subject_map[code] = (name, faculty)
        else:
            existing_name, existing_faculty = subject_map[code]
            subject_map[code] = (existing_name, f"{existing_faculty}, {faculty}")

    return subject_map


def _find_header_codes(text: str) -> list:
    """
    Fallback: scan the header row for course codes when no footer table exists.
    Looks for lines that contain only course codes (e.g. 'CST401 MCN401 CSL411').
    Returns ordered list of codes, or empty list if nothing found.
    """
    header_line_pattern = re.compile(
        r'^((?:[A-Z]{2,8}\d{3})\s+)+(?:[A-Z]{2,8}\d{3})\s*$'
    )
    for line in text.split("\n"):
        stripped = line.strip()
        if header_line_pattern.match(stripped):
            return re.findall(r'[A-Z]{2,8}\d{3}', stripped)
    return []


def _stitch_split_names(body: str) -> str:
    """
    Fix student names that are split across two PDF lines.
    Example raw text:
        AIK24CS036 AUGUSTINE NESTAC PAUL
        BHAKYADAS 45 78 ...
    After stitch:
        AIK24CS036 AUGUSTINE NESTAC PAUL BHAKYADAS 45 78 ...
    """
    lines = body.split("\n")
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            is_continuation = (
                re.match(r'^[A-Z][A-Z\s]+\d', next_line) is not None
                and not USN_PATTERN.match(next_line.split()[0] if next_line.split() else "")
                and not re.match(r'^\d', next_line)
            )
            if is_continuation:
                line = line.rstrip() + " " + next_line
                i += 1
        result.append(line)
        i += 1
    return "\n".join(result)


def _load_name_overrides() -> dict:
    """Load manual name corrections from backend/data/name_overrides.csv."""
    import os
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "name_overrides.csv"
    )
    overrides = {}
    if not os.path.exists(csv_path):
        return overrides
    import csv
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            usn  = row.get("USN", "").strip().upper()
            name = row.get("Name", "").strip()
            if usn and name:
                overrides[usn] = name
    if overrides:
        print(f"[internal_parser] Loaded {len(overrides)} name overrides from CSV")
    return overrides


def detect_batch_year(text: str) -> str:
    """Extract 2-digit batch year from sessional PDF header."""
    m = re.search(r'Batch.*?:(\d{4})-\d{4}', text)
    if m:
        return m.group(1)[2:]
    return ''


def _detect_row_format(tokens: list, start: int, subject_count: int) -> bool:
    """
    Look ahead from `start` to decide whether this student row uses
    two columns per subject (mark + att%) or one column (mark only).

    Returns True if att% columns are present (2-col format).

    Strategy: count consecutive digit-or-star tokens. If the count equals
    subject_count * 2 + 1 (all marks + all att% + total), it's 2-col.
    If it equals subject_count + 1 (all marks + total), it's 1-col.
    If neither matches exactly, use a ratio heuristic.
    """
    j = start
    total_tokens = len(tokens)
    count = 0
    while j < total_tokens:
        t = tokens[j]
        if re.match(r'^\d+(\.\d+)?$', t) or t == "*":
            count += 1
            j += 1
        else:
            break

    if count == subject_count * 2 + 1:
        return True   # clear 2-col signal
    if count == subject_count + 1:
        return False  # clear 1-col signal

    # Ambiguous: guess by whether count is closer to 2-col or 1-col expectation
    return abs(count - (subject_count * 2 + 1)) < abs(count - (subject_count + 1))


def parse_sessional_pdf(pdf_path: str) -> tuple:
    """
    Parse the college sessional marks PDF.

    Returns:
        records     : list of InternalRecord
        name_mapping: { usn: student_name }
        batch_year  : 2-digit string e.g. '23'
    """
    text = extract_text(pdf_path)

    cutoff = text.find("Class Average")
    body   = text[:cutoff] if cutoff > 0 else text
    body   = _stitch_split_names(body)

    subject_map = parse_subject_footer(text)

    if not subject_map:
        header_codes = _find_header_codes(body)
        if header_codes:
            subject_map = {code: (code, "N/A") for code in header_codes}

    if not subject_map:
        raise ValueError(
            "Could not find subject footer table in sessional PDF. "
            "Check that the PDF has the '# Course Code ...' section."
        )

    subject_codes = list(subject_map.keys())
    subject_count = len(subject_codes)
    name_overrides = _load_name_overrides()

    records      = []
    name_mapping = {}
    tokens = body.split()
    i      = 0
    total  = len(tokens)

    while i < total:
        token = tokens[i]

        if re.match(r'^\d{1,3}$', token):
            i += 1
            continue

        if not USN_PATTERN.match(token):
            i += 1
            continue

        usn = token
        i += 1

        # Extract student name — stop at first digit token
        name_parts = []
        while i < total and not re.match(r'^\d+(\.\d+)?$', tokens[i]):
            name_parts.append(tokens[i])
            i += 1
        student_name = " ".join(name_parts).strip()

        if usn in name_overrides:
            student_name = name_overrides[usn]
        name_mapping[usn] = student_name

        # ── KEY FIX: detect per-student whether att% columns are present ──
        has_att_col = _detect_row_format(tokens, i, subject_count)

        marks = []
        for _ in range(subject_count):
            if i >= total:
                marks.append((0, False))
                continue

            if tokens[i] == "*":
                i += 1  # skip '*'
                if has_att_col and i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    i += 1  # skip att%
                marks.append((0, False))
            else:
                mark_val = 0
                if i < total and re.match(r'^\d+$', tokens[i]):
                    mark_val = int(tokens[i])
                    i += 1
                if has_att_col and i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    i += 1  # skip att%
                marks.append((mark_val, True))

        # Skip trailing total column
        if i < total and re.match(r'^\d+$', tokens[i]):
            i += 1

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

    batch_year = detect_batch_year(text)
    return records, name_mapping, batch_year
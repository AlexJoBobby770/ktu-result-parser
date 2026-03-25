# backend/internal_parser.py
import re
import os
import pandas as pd
import pdfplumber

try:
    from backend.models import InternalRecord
except ModuleNotFoundError:
    from models import InternalRecord

USN_PATTERN    = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2,3}\d{3})$')
SUBJECT_CODE   = re.compile(r'^[A-Z]{2,8}\d{3}$')
FOOTER_PATTERN = re.compile(
    r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+\S.+)$'
)

# Allow fallback footer lines without honorifics to support different PDF formatting.
FOOTER_FALLBACK = re.compile(r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+(.+)$')


# FIX: Changed [A-Z]{2,4} → [A-Z]{2,8} to match long 2024-scheme course codes
# like GAMAT301, PCCST302, UCHUT346
FOOTER_PATTERN = re.compile(
    r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+\S.+)$'
)

# FIX: Added MET prefix to USN pattern (seen in some college PDFs)
USN_PATTERN = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2}\d{3})$')


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
            m = FOOTER_FALLBACK.match(line.strip())
        if not m:
            continue

        code    = m.group(1).strip()
        name    = m.group(2).strip()
        faculty = m.group(3).strip()

        if code not in subject_map:
            subject_map[code] = (name, faculty)
        else:
            # Multiple faculty for same subject — append name
            existing_name, existing_faculty = subject_map[code]
            subject_map[code] = (existing_name, f"{existing_faculty}, {faculty}")

    return subject_map


def _find_data_sheet(excel_path: str) -> str:
    """Find sheet with student records by USN detection."""
    xl = pd.ExcelFile(excel_path)
    best_sheet = xl.sheet_names[0]
    max_count = 0

    for sheet in xl.sheet_names:
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet, header=None, nrows=15)
            count = sum(1 for _, row in df.iterrows()
                        if len(row) > 1 and isinstance(row.iloc[1], str) and USN_PATTERN.match(row.iloc[1].strip()))
            if count > max_count:
                max_count = count
                best_sheet = sheet
        except Exception:
            continue

    return best_sheet


def parse_sessional_excel(excel_path: str) -> tuple:
    """Parse sessional Excel file into internal records."""
    sheet = _find_data_sheet(excel_path)
    df = pd.read_excel(excel_path, sheet_name=sheet, header=None)

    # Find header row: contains 'Reg no'/'Roll No' and subject codes
    header_row_idx = None
    for i in range(min(len(df), 10)):
        row = df.iloc[i].astype(str).str.strip().tolist()
        if any('Reg no' in str(v) or 'Roll No' in str(v) for v in row):
            header_row_idx = i
            break

    if header_row_idx is None:
        raise ValueError('Could not find sessional Excel header row')

    # Read subject codes from header row (skip first 3 columns: roll, usn, name)
    top = df.iloc[header_row_idx].astype(str).tolist()
    subject_codes = [re.sub(r'\s+', '', str(x).strip()) for x in top[3:] if x and 'Total' not in str(x)]
    subject_codes = [c for c in subject_codes if SUBJECT_CODE.match(c)]

    if not subject_codes:
        raise ValueError('No subject codes found in sessional Excel header row')

    # Subject metadata block may be in the same sheet after data
    # Parse using the same footer parsing logic used for PDFs (FOOTER_PATTERN / FOOTER_FALLBACK)
    subject_map = {}
    footer_lines = []
    for i in range(max(0, len(df)-15), len(df)):
        row = df.iloc[i].dropna().astype(str).str.strip()
        if row.empty:
            continue
        footer_lines.append(" ".join(row.tolist()))

    if footer_lines:
        subject_map = parse_subject_footer("\n".join(footer_lines))

    # Ensure subject_map includes all detected codes with safe defaults
    if not subject_map:
        subject_map = {c: (c, 'N/A') for c in subject_codes}
    else:
        # keep only relevant codes and fill missing ones
        subject_map = {c: (n, f) for c, (n, f) in subject_map.items() if c in subject_codes}
        for c in subject_codes:
            if c not in subject_map:
                subject_map[c] = (c, 'N/A')

    # student rows begin after the header row and mark row
    records = []
    name_mapping = {}
    for i in range(header_row_idx + 2, len(df)):
        row = df.iloc[i]
        if pd.isna(row.iloc[0]) or pd.isna(row.iloc[1]):
            continue
        usn = str(row.iloc[1]).strip().upper()
        if not USN_PATTERN.match(usn):
            continue
        name = str(row.iloc[2]).strip()
        name_mapping[usn] = name

        for j, code in enumerate(subject_codes):
            col = 3 + j
            if col >= len(row):
                val = ''
            else:
                val = row.iloc[col]
            if pd.isna(val) or str(val).strip() == '*':
                mark = 0
                elected = False
            else:
                try:
                    mark = int(float(val))
                    elected = True
                except Exception:
                    mark = 0
                    elected = False
            subj_name, faculty = subject_map.get(code, (code, 'N/A'))
            records.append(InternalRecord(usn=usn, student_name=name,
                                          course_code=code, subject_name=subj_name,
                                          faculty_name=faculty, internal_mark=mark,
                                          elected=elected))

    batch_year = detect_batch_year(str(df.iloc[0].astype(str).str.cat(sep=' ')))
    return records, name_mapping, batch_year


def _find_header_codes(text: str) -> list:
    """
    Fallback: scan the header row for course codes when no footer table exists.
    Looks for the line containing 'Reg no' or 'Roll No', then extracts course codes
    from that line and subsequent lines until codes are found.
    Handles cases where codes are split across tokens (e.g. 'CST30 1' -> 'CST301').
    Returns ordered list of codes, or empty list if nothing found.
    """
    codes = []
    header_found = False
    for line in text.split("\n"):
        stripped = line.strip()
        if not header_found and ("Reg no" in stripped or "Roll No" in stripped):
            header_found = True
        if header_found:
            tokens = stripped.split()
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if SUBJECT_CODE.match(token):
                    codes.append(token)
                    i += 1
                elif i+1 < len(tokens) and SUBJECT_CODE.match(token + tokens[i+1]):
                    codes.append(token + tokens[i+1])
                    i += 2
                else:
                    i += 1
            if codes:  # stop after finding codes in this or subsequent lines
                break
    return codes


def _stitch_split_names(body: str) -> str:
    """
    Fix student names that are split across two PDF lines.
    Pattern: a line ending mid-name (all caps words, no digits)
    followed by a line that continues with more caps words before a digit.

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
        # If the next line starts with uppercase words (no digits) before numbers,
        # it is a continuation of the current line's name.
        if i + 1 < len(lines):
            next_line = lines[i + 1].strip()
            # Next line is a name continuation if:
            # - starts with uppercase letters (not a USN, not a digit)
            # - does NOT match a USN pattern
            # - contains digits somewhere (meaning name ends and marks begin)
            is_continuation = (
                re.match(r'^[A-Z][A-Z\s]+\d', next_line) is not None
                and not USN_PATTERN.match(next_line.split()[0] if next_line.split() else "")
                and not re.match(r'^\d', next_line)
            )
            if is_continuation:
                line = line.rstrip() + " " + next_line
                i += 1  # skip the continuation line
        result.append(line)
        i += 1
    return "\n".join(result)


def _load_name_overrides() -> dict:
    """
    Load manual name corrections from backend/data/name_overrides.csv.
    Format: USN,Name
    No code change needed — just edit the CSV and restart.
    """
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
    """
    Extract 2-digit batch year from sessional PDF header.
    e.g. 'Batch & Semester :2022-2026 S7'  →  '22'
    Returns '' if not found.
    """
    m = re.search(r'Batch.*?:(\d{4})-\d{4}', text)
    if m:
        return m.group(1)[2:]   # '2022' → '22'
    return ''


def parse_sessional_pdf(pdf_path: str) -> tuple:
    """
    Parse the college sessional marks PDF.

    Returns:
        records     : list of InternalRecord
        name_mapping: { usn: student_name }
        batch_year  : 2-digit string e.g. '23'

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
    body   = text[:cutoff] if cutoff > 0 else text

    # FIX: stitch names that got split across PDF lines before tokenising
    body = _stitch_split_names(body)

    # Get subject codes from header (more reliable order)
    header_codes = _find_header_codes(body)

    # Parse footer AFTER cutoff to get subject metadata
    subject_map = parse_subject_footer(text)

    if header_codes:
        subject_codes = header_codes
        # Merge with footer metadata if available
        for code in subject_codes:
            if code not in subject_map:
                subject_map[code] = (code, "N/A")
    else:
        if not subject_map:
            raise ValueError(
                "Could not find subject footer table or header codes in sessional PDF. "
                "Check that the PDF has the '# Course Code ...' section or header with subject codes."
            )
        subject_codes = list(subject_map.keys())
    subject_count = len(subject_codes)

    # FIX: load manual name overrides from CSV
    name_overrides = _load_name_overrides()

    records      = []
    name_mapping = {}

    tokens = body.split()
    i      = 0
    total  = len(tokens)

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

        # Apply manual override if present
        if usn in name_overrides:
            student_name = name_overrides[usn]

        name_mapping[usn] = student_name

        # --- Extract marks for each subject in order ---
        # First, count consecutive digit tokens to detect format
        digit_count = 0
        j = i
        while j < total and re.match(r'^\d+(\.\d+)?$', tokens[j]):
            digit_count += 1
            j += 1

        marks = []    # list of (mark_int, elected_bool)

        if digit_count == subject_count * 2 + 1:
            # Format: mark att% ... total
            for _ in range(subject_count):
                if tokens[i] == "*":
                    # Elective NOT chosen
                    i += 1
                    if i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                        i += 1  # skip att%
                    marks.append((0, False))
                else:
                    # Normal subject
                    mark_val = 0
                    if re.match(r'^\d+$', tokens[i]):
                        mark_val = int(tokens[i])
                        i += 1
                    if i < total and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                        i += 1  # skip att%
                    marks.append((mark_val, True))
            # Skip total
            if i < total and re.match(r'^\d+$', tokens[i]):
                i += 1
        elif digit_count == subject_count + 1:
            # Format: mark ... total
            for _ in range(subject_count):
                mark_val = 0
                if i < total and re.match(r'^\d+$', tokens[i]):
                    mark_val = int(tokens[i])
                    i += 1
                marks.append((mark_val, True))
            # Skip total
            if i < total and re.match(r'^\d+$', tokens[i]):
                i += 1
        else:
            # Fallback: assume marks only
            for _ in range(subject_count):
                mark_val = 0
                if i < total and re.match(r'^\d+$', tokens[i]):
                    mark_val = int(tokens[i])
                    i += 1
                marks.append((mark_val, True))

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

    batch_year = detect_batch_year(text)
    return records, name_mapping, batch_year
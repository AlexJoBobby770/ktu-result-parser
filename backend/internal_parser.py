# backend/internal_parser.py
import re
import pdfplumber

try:
    from backend.models import InternalRecord
except ModuleNotFoundError:
    from models import InternalRecord


USN_PATTERN    = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2}\d{3})$')
SUBJECT_CODE   = re.compile(r'^[A-Z]{2,8}\d{3}$')
FOOTER_PATTERN = re.compile(
    r'^\d+\s+([A-Z]{2,8}\d{3})\s+(.+?)\s+((?:Ms\.|Mr\.|Dr\.)\s+\S.+)$'
)


def _clean(val) -> str:
    if val is None:
        return ""
    return str(val).replace("\n", " ").strip()


def _is_usn(val) -> bool:
    return bool(USN_PATTERN.match(_clean(val)))


def _is_number(val) -> bool:
    s = _clean(val)
    try:
        float(s)
        return True
    except ValueError:
        return False


def _parse_subject_footer(text: str) -> dict:
    subject_map = {}
    for line in text.split("\n"):
        m = FOOTER_PATTERN.match(line.strip())
        if not m:
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


def _detect_batch_year(text: str) -> str:
    m = re.search(r'Batch.*?:(\d{4})-\d{4}', text)
    return m.group(1)[2:] if m else ""


def _load_name_overrides() -> dict:
    import os, csv
    csv_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "data", "name_overrides.csv"
    )
    overrides = {}
    if not os.path.exists(csv_path):
        return overrides
    with open(csv_path, newline="") as f:
        for row in csv.DictReader(f):
            usn  = row.get("USN", "").strip().upper()
            name = row.get("Name", "").strip()
            if usn and name:
                overrides[usn] = name
    if overrides:
        print(f"[internal_parser] Loaded {len(overrides)} name overrides")
    return overrides


def _parse_table(table: list, subject_codes: list) -> list:
    """
    Parse one pdfplumber-extracted table from a sessional PDF page.
    Returns list of (usn, name, marks_list) where marks_list is
    [(mark_int, elected_bool), ...] aligned to subject_codes order.
    """
    if not table:
        return []

    # Find the header row — contains 'Reg no'
    header_row_idx = None
    header_row     = None
    for i, row in enumerate(table):
        if row and any(_clean(c) == "Reg no" for c in row):
            header_row_idx = i
            header_row     = row
            break

    if header_row is None:
        return []

    # Locate USN and Name columns from header
    usn_col  = None
    name_col = None
    for i, c in enumerate(header_row):
        cleaned = _clean(c)
        if cleaned == "Reg no":
            usn_col = i
        if cleaned == "Name of student":
            name_col = i

    if usn_col is None:
        return []

    # Locate subject mark columns — header cell matches subject code pattern
    subject_col_map = {}
    for i, c in enumerate(header_row):
        cleaned = _clean(c)
        if SUBJECT_CODE.match(cleaned):
            subject_col_map[cleaned] = i

    # Parse data rows
    results = []
    for row in table[header_row_idx + 1:]:
        if not row:
            continue

        # Find USN in this row
        usn = None
        for cell in row:
            if _is_usn(cell):
                usn = _clean(cell)
                break
        if not usn:
            continue

        # Extract name from name column; fallback to first non-numeric cell after USN
        name = ""
        if name_col is not None and name_col < len(row):
            name = _clean(row[name_col])
        if not name:
            for cell in row[usn_col + 1:]:
                s = _clean(cell)
                if s and not _is_number(s) and not SUBJECT_CODE.match(s):
                    name = s
                    break

        # Extract marks in subject_codes order
        marks = []
        for code in subject_codes:
            mark_col = subject_col_map.get(code)
            if mark_col is None or mark_col >= len(row):
                marks.append((0, True))
                continue
            cell_val = _clean(row[mark_col])
            if cell_val == "*" or cell_val == "":
                marks.append((0, False))   # elective not taken
            else:
                try:
                    marks.append((int(cell_val), True))
                except ValueError:
                    marks.append((0, True))

        results.append((usn, name, marks))

    return results


def parse_sessional_pdf(pdf_path: str) -> tuple:
    """
    Parse the college sessional marks PDF using pdfplumber table extraction.
    Returns: (records, name_mapping, batch_year)
    """
    # Full text needed for footer table and batch year detection
    full_text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                full_text += t + "\n"

    batch_year  = _detect_batch_year(full_text)
    subject_map = _parse_subject_footer(full_text)

    if not subject_map:
        raise ValueError(
            "Could not find subject footer table in sessional PDF. "
            "Check that the PDF has the '# Course Code ...' section."
        )

    subject_codes  = list(subject_map.keys())
    name_overrides = _load_name_overrides()

    # Parse tables from each page
    all_student_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            if not tables:
                continue
            rows = _parse_table(tables[0], subject_codes)
            all_student_rows.extend(rows)

    # Deduplicate — keep first occurrence of each USN
    seen = set()
    unique_rows = []
    for row in all_student_rows:
        if row[0] not in seen:
            seen.add(row[0])
            unique_rows.append(row)

    records      = []
    name_mapping = {}

    for usn, name, marks in unique_rows:
        if usn in name_overrides:
            name = name_overrides[usn]
        name_mapping[usn] = name

        for idx, code in enumerate(subject_codes):
            subject_name, faculty_name = subject_map[code]
            mark, elected = marks[idx] if idx < len(marks) else (0, True)
            records.append(InternalRecord(
                usn=usn,
                student_name=name,
                course_code=code,
                subject_name=subject_name,
                faculty_name=faculty_name,
                internal_mark=mark,
                elected=elected,
            ))

    print(f"[internal_parser] {len(unique_rows)} students, "
          f"{len(subject_codes)} subjects, batch={batch_year!r}")

    return records, name_mapping, batch_year
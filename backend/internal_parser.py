# backend/internal_parser.py
import re
import pdfplumber
from backend.models import InternalRecord

COURSE_CODE_RE = re.compile(r'^([A-Z]{2,8}\d{3})$')
USN_RE_SEARCH  = re.compile(r'(?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2}\d{3}')
USN_RE_EXACT   = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2}\d{3})$')
NUMBER_RE      = re.compile(r'^\d+(\.\d+)?$')
INT_RE         = re.compile(r'^\d+$')


def extract_text(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def detect_batch_year(text: str) -> str:
    m = re.search(r'Batch.*?:(\d{4})-\d{4}', text)
    if m:
        return m.group(1)[2:]
    return ''


def parse_subject_footer(text: str) -> dict:
    """
    Parse '# Course Code Course Name Faculty' footer table.
    Handles multi-line subject names (name wraps to the line before the code).
    Returns {code: (subject_name, faculty_name)}
    """
    subject_map  = {}
    FOOTER_LINE  = re.compile(
        r'^\d{1,2}\s+([A-Z]{2,8}\d{3})\s*(.*?)\s*((?:Ms\.|Mr\.|Dr\.)\s+\S.*)$'
    )
    pending_name = ""

    for line in text.split('\n'):
        stripped = line.strip()
        m = FOOTER_LINE.match(stripped)
        if m:
            code    = m.group(1).strip()
            inline  = m.group(2).strip()
            faculty = m.group(3).strip()
            name    = inline if inline else pending_name
            if code not in subject_map:
                subject_map[code] = (name, faculty)
            else:
                n, f = subject_map[code]
                subject_map[code] = (n, f"{f}, {faculty}")
            pending_name = ""
            continue

        if (stripped
                and not stripped.startswith('#')
                and not stripped.startswith('Signature')
                and not stripped.startswith('Date')
                and not stripped.startswith('Disclaimer')
                and not re.match(r'^\d', stripped)
                and not re.search(r'(?:Ms\.|Mr\.|Dr\.)', stripped)):
            pending_name = stripped
        else:
            pending_name = ""

    return subject_map


def detect_format(text: str) -> str:
    """
    Detect which PDF format this is:
      'excel'    — converted from Excel: no attendance columns, marks only
      'original' — original AISAT PDF: has attendance % columns
    """
    # Excel-converted PDFs have a two-line header like:
    #   "Roll UCHUT GAMAT PCCST ..."
    #   "no 346 301 302 ..."
    # Original PDFs have "Mark Att %" columns
    if re.search(r'\bMark\b.*\bAtt\s*%\b', text) or re.search(r'\bAtt\s*%\b.*\bMark\b', text):
        return 'original'
    return 'excel'


def parse_excel_format(text: str, subject_map: dict) -> tuple:
    """
    Parse Excel-converted PDF.
    Row format: roll_no USN name mark1 mark2 ... markN total
    No attendance columns.
    """
    codes         = list(subject_map.keys())
    subject_count = len(codes)
    records       = []
    name_mapping  = {}

    # Cut stats footer
    cutoff = text.find("Class Average")
    body   = text[:cutoff] if cutoff > 0 else text

    tokens = body.split()
    i, total = 0, len(tokens)

    while i < total:
        # Skip roll number
        if INT_RE.match(tokens[i]) and len(tokens[i]) <= 3:
            i += 1
            continue

        if not USN_RE_EXACT.match(tokens[i]):
            i += 1
            continue

        usn = tokens[i]; i += 1

        # Student name — uppercase words until first number
        name_parts = []
        while i < total and not NUMBER_RE.match(tokens[i]):
            name_parts.append(tokens[i])
            i += 1
        name = " ".join(name_parts).strip()
        name_mapping[usn] = name

        # Marks — just integers, one per subject, then Total
        marks = []
        for _ in range(subject_count):
            if i < total and INT_RE.match(tokens[i]):
                marks.append(int(tokens[i])); i += 1
            else:
                marks.append(0)

        # Skip Total
        if i < total and INT_RE.match(tokens[i]):
            i += 1

        for idx, code in enumerate(codes):
            sname, faculty = subject_map[code]
            mark = marks[idx] if idx < len(marks) else 0
            records.append(InternalRecord(
                usn=usn, student_name=name,
                course_code=code, subject_name=sname,
                faculty_name=faculty, internal_mark=mark, elected=True,
            ))

    return records, name_mapping


def parse_original_format(text: str, subject_map: dict) -> tuple:
    """
    Parse original AISAT sessional PDF.
    Row format: roll_no USN name (mark att%)* total
    Has attendance % columns interleaved with marks.
    Electives marked with * instead of mark.
    """
    codes         = list(subject_map.keys())
    subject_count = len(codes)
    records       = []
    name_mapping  = {}

    cutoff = text.find("Class Average")
    body   = text[:cutoff] if cutoff > 0 else text

    tokens = body.split()
    i, total = 0, len(tokens)

    while i < total:
        if INT_RE.match(tokens[i]) and len(tokens[i]) <= 3:
            i += 1; continue

        if not USN_RE_EXACT.match(tokens[i]):
            i += 1; continue

        usn = tokens[i]; i += 1

        name_parts = []
        while i < total and not NUMBER_RE.match(tokens[i]):
            name_parts.append(tokens[i]); i += 1
        name = " ".join(name_parts).strip()
        name_mapping[usn] = name

        marks = []
        for _ in range(subject_count):
            if i >= total:
                marks.append((0, False)); continue
            if tokens[i] == "*":
                i += 1
                if i < total and NUMBER_RE.match(tokens[i]):
                    i += 1   # skip att% after *
                marks.append((0, False))
            else:
                mark_val = 0
                if INT_RE.match(tokens[i]):
                    mark_val = int(tokens[i]); i += 1
                if i < total and NUMBER_RE.match(tokens[i]):
                    i += 1   # skip att%
                marks.append((mark_val, True))

        if i < total and INT_RE.match(tokens[i]):
            i += 1   # skip Total

        for idx, code in enumerate(codes):
            sname, faculty = subject_map[code]
            mark, elected = marks[idx] if idx < len(marks) else (0, False)
            records.append(InternalRecord(
                usn=usn, student_name=name,
                course_code=code, subject_name=sname,
                faculty_name=faculty, internal_mark=mark, elected=elected,
            ))

    return records, name_mapping


def parse_sessional_pdf(pdf_path: str) -> tuple:
    """
    Parse sessional marks PDF.

    Handles two formats:
      'excel'    — converted from Excel (no attendance columns)
      'original' — original AISAT PDF (has attendance % columns + elective * markers)

    Both formats must have the '# Course Code' footer table.
    If footer is missing, raises a clear error telling the teacher.

    Returns: (records, name_mapping, batch_year)
    """
    text       = extract_text(pdf_path)
    batch_year = detect_batch_year(text)

    # Parse footer — required in both formats
    if '# Course Code' not in text:
        raise ValueError(
            "Could not find the subject table in the sessional PDF.\n\n"
            "The PDF must contain the '# Course Code / Course Name / Faculty' "
            "table at the bottom. This table is required to identify subject names "
            "and assign marks correctly.\n\n"
            "If you converted an Excel file to PDF, make sure all pages/sheets "
            "were included in the export, including the last page with the subject table."
        )

    subject_map = parse_subject_footer(text)
    if not subject_map:
        raise ValueError(
            "Found the subject table header but could not parse any subject rows. "
            "Please check the PDF is not corrupted or password-protected."
        )

    fmt = detect_format(text)

    if fmt == 'excel':
        records, name_mapping = parse_excel_format(text, subject_map)
    else:
        records, name_mapping = parse_original_format(text, subject_map)

    return records, name_mapping, batch_year
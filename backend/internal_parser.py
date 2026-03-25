# backend/internal_parser.py
import re
import pandas as pd

try:
    from backend.models import InternalRecord
except ModuleNotFoundError:
    from models import InternalRecord

USN_PATTERN    = re.compile(r'^((?:AIK|LAIK|SGI|SPT|GWE|MZW|MET)\d{2}[A-Z]{2,3}\d{3})$')
SUBJECT_CODE   = re.compile(r'^[A-Z]{2,8}\d{3}$')


def parse_subject_metadata(excel_path: str) -> dict:
    """
    Parse the subject metadata from the bottom of the Excel sheet.
    Expected format: rows like "1 CST301 Formal Languages and Automata Theory Ms. A. Thilakavathi"
    Returns { "CST301": ("Formal Languages and Automata Theory", "Ms. A. Thilakavathi"), ... }
    """
    sheet_name = _find_data_sheet(excel_path)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    
    subject_map = {}
    # Look for rows that start with numbers (subject numbering)
    for _, row in df.iterrows():
        first_cell = str(row.iloc[0]).strip()
        if first_cell.isdigit():
            # Check if it looks like subject metadata
            row_str = ' '.join(str(x) for x in row if pd.notna(x))
            # Pattern: number CODE Subject Name Faculty
            parts = row_str.split()
            if len(parts) >= 4 and re.match(r'^[A-Z]{2,8}\d{3}$', parts[1]):
                code = parts[1]
                # Find where faculty starts (usually "Ms." or "Mr." or "Dr.")
                faculty_start = -1
                for i, part in enumerate(parts[2:], 2):
                    if re.match(r'^(Ms\.|Mr\.|Dr\.)', part):
                        faculty_start = i
                        break
                if faculty_start > 0:
                    subject_name = ' '.join(parts[2:faculty_start])
                    faculty = ' '.join(parts[faculty_start:])
                    subject_map[code] = (subject_name, faculty)
    
    return subject_map


def _find_data_sheet(excel_path: str) -> str:
    """
    Find the sheet containing student data by looking for patterns.
    Returns the sheet name with the most student records.
    """
    xl = pd.ExcelFile(excel_path)
    best_sheet = xl.sheet_names[0]
    max_students = 0
    
    for sheet_name in xl.sheet_names:
        try:
            df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None, nrows=10)
            # Look for rows that look like student data (USN pattern in column 1)
            student_count = 0
            for _, row in df.iterrows():
                if len(row) > 1:
                    cell_val = str(row.iloc[1]).strip()
                    if USN_PATTERN.match(cell_val):
                        student_count += 1
            if student_count > max_students:
                max_students = student_count
                best_sheet = sheet_name
        except:
            continue
    
    return best_sheet


def _find_subject_codes(excel_path: str) -> list:
    """
    Find subject codes from the header row in the Excel.
    Looks for row 4 (index 4) which contains subject codes after "Name of student"
    Handles split codes like 'CST30 1' -> 'CST301'
    """
    sheet_name = _find_data_sheet(excel_path)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)
    
    # Row 4 (index 4) should contain the headers
    if len(df) > 4:
        header_row = df.iloc[4]
        subject_codes = []
        # Columns 3-10: subject codes
        for cell in header_row.iloc[3:11]:  # Up to but not including column 11 (Total)
            if pd.notna(cell):
                cell_str = str(cell).strip().replace(' ', '')  # Remove spaces
                # Extract subject code if it matches pattern
                match = re.search(r'^([A-Z]{2,8}\d{3})', cell_str)
                if match:
                    subject_codes.append(match.group(1))
        return subject_codes
    return []


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


def detect_batch_year(excel_path: str) -> str:
    """
    Extract 2-digit batch year from Excel.
    Try to find in a cell containing 'Batch' or from filename.
    Returns '' if not found.
    """
    try:
        xl = pd.ExcelFile(excel_path)
        for sheet in xl.sheet_names:
            df = pd.read_excel(excel_path, sheet_name=sheet, nrows=10)  # Read first 10 rows
            for _, row in df.iterrows():
                for cell in row:
                    cell_str = str(cell)
                    m = re.search(r'Batch.*?:(\d{4})-\d{4}', cell_str)
                    if m:
                        return m.group(1)[2:]   # '2022' → '22'
    except:
        pass
    # Fallback: try filename
    filename = os.path.basename(excel_path)
    m = re.search(r'(\d{2})', filename)
    if m:
        return m.group(1)
    return ''


def parse_sessional_excel(excel_path: str) -> tuple:
    """
    Parse the college sessional marks Excel.

    Expected format (based on sample):
    - Sheet 'Table 1': 
      - Row 2: Batch info like "Branch :CSE  B Batch & Semester :2023-2027  S5"
      - Row 4: Headers: Roll No, Reg no, Name of student, CST301, CST303, ..., Total
      - Rows 5+: Student data: roll, USN, name, marks for each subject
      - Bottom rows: Subject metadata like "1 CST301 Formal Languages and Automata Theory Ms. A. Thilakavathi"

    Returns:
        records     : list of InternalRecord
        name_mapping: { usn: student_name }
        batch_year  : 2-digit string e.g. '23'
    """
    # Get subject codes from headers
    subject_codes = _find_subject_codes(excel_path)
    subject_count = len(subject_codes)

    # Get subject metadata
    subject_map = parse_subject_metadata(excel_path)

    # Merge with metadata
    for code in subject_codes:
        if code not in subject_map:
            subject_map[code] = (code, "N/A")

    # Load name overrides
    name_overrides = _load_name_overrides()

    # Read the full data
    sheet_name = _find_data_sheet(excel_path)
    df = pd.read_excel(excel_path, sheet_name=sheet_name, header=None)

    records = []
    name_mapping = {}

    # Data starts from row 5 (index 5)
    for idx in range(5, len(df)):
        row = df.iloc[idx]
        
        # Skip if first cell is not a number (roll number)
        roll_cell = str(row.iloc[0]).strip()
        if not roll_cell.isdigit():
            continue
            
        usn = str(row.iloc[1]).strip().upper()
        if not USN_PATTERN.match(usn):
            continue  # Skip invalid rows

        student_name = str(row.iloc[2]).strip()
        # Apply override
        if usn in name_overrides:
            student_name = name_overrides[usn]
        name_mapping[usn] = student_name

        # Marks start from column 3, up to subject_count
        for subj_idx, code in enumerate(subject_codes):
            col_idx = 3 + subj_idx
            if col_idx >= len(row):
                mark = 0
                elected = False
            else:
                mark_val = row.iloc[col_idx]
                if pd.isna(mark_val) or str(mark_val).strip() in ('*', ''):
                    mark = 0
                    elected = False
                else:
                    try:
                        mark = int(float(mark_val))
                        elected = True
                    except:
                        mark = 0
                        elected = False

            subject_name, faculty_name = subject_map[code]
            records.append(InternalRecord(
                usn=usn,
                student_name=student_name,
                course_code=code,
                subject_name=subject_name,
                faculty_name=faculty_name,
                internal_mark=mark,
                elected=elected,
            ))

    batch_year = detect_batch_year(excel_path)
    return records, name_mapping, batch_year
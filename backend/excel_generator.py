# backend/excel_generator.py
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict
from datetime import datetime
from models import (
    PASSING_GRADES, FAIL_GRADES, GRADE_POINTS,
    compute_sgpa, get_credits, get_status
)

COLLEGE_NAME     = "ALBERTIAN INSTITUTE OF SCIENCE AND TECHNOLOGY (AISAT)"
COLLEGE_LOCATION = "Kalamassery, Ernakulam, Kerala"

# ── colour palette ────────────────────────────────────────────────────────────
C = {
    "dark_blue":  "1E3A8A",
    "mid_blue":   "3B82F6",
    "pass_bg":    "D1FAE5",
    "pass_fg":    "065F46",
    "fail_bg":    "FEE2E2",
    "fail_fg":    "991B1B",
    "white":      "FFFFFF",
    "light_gray": "F3F4F6",
    "dark_text":  "1F2937",
    "skip_bg":    "F3F4F6",   # greyed out = elective not chosen
    "skip_fg":    "9CA3AF",
}

THIN = Border(
    left=Side(style="thin", color="D1D5DB"),
    right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin", color="D1D5DB"),
    bottom=Side(style="thin", color="D1D5DB"),
)


# ── helpers ───────────────────────────────────────────────────────────────────

def _fill(hex_color):
    return PatternFill(start_color=hex_color, end_color=hex_color, fill_type="solid")

def _font(color=C["dark_text"], bold=False, size=10, italic=False):
    return Font(name="Calibri", size=size, bold=bold, color=color, italic=italic)


def _write_sheet_header(ws, title: str, num_cols: int):
    """Write the 5-row college header block at the top of every sheet."""
    col_letter = get_column_letter(num_cols)

    rows = [
        (COLLEGE_NAME,    16, True,  C["dark_blue"],  C["white"]),
        (COLLEGE_LOCATION, 11, False, C["dark_text"],  None),
        (title,           12, True,  C["dark_text"],  C["mid_blue"]),
        (f"Generated: {datetime.now().strftime('%d %B %Y  %I:%M %p')}", 9, False, "6B7280", None),
    ]

    for row_idx, (text, size, bold, fg, bg) in enumerate(rows, start=1):
        ws.merge_cells(f"A{row_idx}:{col_letter}{row_idx}")
        cell = ws[f"A{row_idx}"]
        cell.value = text
        cell.font = Font(name="Calibri", size=size, bold=bold, color=fg)
        cell.alignment = Alignment(horizontal="center", vertical="center")
        if bg:
            cell.fill = _fill(bg)
        ws.row_dimensions[row_idx].height = 22 if row_idx < 4 else 16

    ws.row_dimensions[5].height = 6   # blank spacer row


def _format_header_row(ws, row=6):
    """Style the column header row (row 6)."""
    ws.row_dimensions[row].height = 32
    for col in range(1, ws.max_column + 1):
        cell = ws.cell(row=row, column=col)
        if cell.value is not None:
            cell.font = Font(name="Calibri", size=10, bold=True, color=C["white"])
            cell.fill = _fill(C["dark_blue"])
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            cell.border = THIN


def _format_data_rows(ws, start_row=7):
    """Apply alternating rows and grade-based colouring to data."""
    for row_idx in range(start_row, ws.max_row + 1):
        alt_fill = _fill(C["light_gray"] if row_idx % 2 == 0 else C["white"])

        for col_idx in range(1, ws.max_column + 1):
            cell = ws.cell(row=row_idx, column=col_idx)
            if cell.value is None:
                continue

            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = THIN

            v = str(cell.value).strip()

            if v == "—":
                cell.font = _font(C["skip_fg"])
                cell.fill = _fill(C["skip_bg"])
            elif "✓" in v:
                cell.font = _font(C["pass_fg"], bold=True)
                cell.fill = _fill(C["pass_bg"])
            elif "✗" in v:
                cell.font = _font(C["fail_fg"], bold=True)
                cell.fill = _fill(C["fail_bg"])
            elif v in {"F", "FE", "Absent", "Withheld"}:
                cell.font = _font(C["fail_fg"], bold=True)
                cell.fill = _fill(C["fail_bg"])
            elif v in PASSING_GRADES:
                cell.font = _font(C["pass_fg"])
                cell.fill = _fill(C["pass_bg"])
            else:
                cell.font = _font()
                cell.fill = alt_fill

    ws.freeze_panes = "A7"


# ── MODE 1: external PDF only ─────────────────────────────────────────────────

def generate_external_excel(external_records: list, output_path: str):
    """
    One sheet per department.
    Columns: USN | subject grades... | SGPA | Status
    """
    # Group records by department
    dept_map = defaultdict(list)
    for r in external_records:
        dept_map[r.department].append(r)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for dept in sorted(dept_map):
            recs = dept_map[dept]

            # Build { usn: { course_code: grade } }
            student_grades = defaultdict(dict)
            for r in recs:
                student_grades[r.usn][r.course_code] = r.grade

            # All subjects that appear in this dept, sorted
            all_subjects = sorted({r.course_code for r in recs})

            rows = []
            for usn in sorted(student_grades):
                grades = student_grades[usn]
                row = {"Register No": usn}

                arrears = []
                for sub in all_subjects:
                    grade = grades.get(sub, "")
                    row[sub] = grade
                    if grade and grade not in PASSING_GRADES and grade != "":
                        arrears.append(sub)

                row["SGPA"] = compute_sgpa(grades)
                row["Status"] = "✓ PASS" if not arrears else f"✗ {len(arrears)} ARREAR(S)"
                rows.append(row)

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=dept, index=False, startrow=5)

    _apply_formatting_pass(output_path)
    print(f"✅ External-only Excel saved: {output_path}")


# ── MODE 2: external + internal (CSE focused) ─────────────────────────────────

def generate_merged_excel(
    external_records: list,
    internal_records: list,
    name_mapping: dict,
    output_path: str,
):
    """
    For CSE (or any dept that uploads sessional marks):
    One sheet per department found in external records.
    For depts that also have internal records, columns are:
      USN | Name | [SubjectName - Internal | SubjectName - Grade]... | SGPA | Status
    For depts without internal data, same as external-only mode.
    """
    # Build external lookup: { usn: { course_code: grade } }
    ext_lookup = defaultdict(dict)
    ext_dept   = {}
    for r in external_records:
        ext_lookup[r.usn][r.course_code] = r.grade
        ext_dept[r.usn] = r.department

    # Build internal lookup: { usn: { course_code: InternalRecord } }
    int_lookup = defaultdict(dict)
    for r in internal_records:
        int_lookup[r.usn][r.course_code] = r

    # Departments from external PDF
    dept_usns = defaultdict(set)
    for usn, dept in ext_dept.items():
        dept_usns[dept].add(usn)

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for dept in sorted(dept_usns):
            usns = sorted(dept_usns[dept])
            all_ext_subjects = sorted({
                code for usn in usns
                for code in ext_lookup[usn]
            })

            # Check if we have internal data for this dept
            has_internal = any(usn in int_lookup for usn in usns)

            rows = []
            for usn in usns:
                ext_grades = ext_lookup[usn]
                int_data   = int_lookup.get(usn, {})
                name       = name_mapping.get(usn, "")

                row = {"Register No": usn, "Name": name}

                arrears = []
                sgpa_grades = {}   # only elected subjects go into SGPA

                for code in all_ext_subjects:
                    grade = ext_grades.get(code, "")

                    if has_internal:
                        irec = int_data.get(code)

                        if irec and not irec.elected:
                            # Elective not chosen — show dash
                            row[f"{code} Internal"] = "—"
                            row[f"{code} Grade"]    = "—"
                            continue

                        internal_val = irec.internal_mark if irec else ""
                        row[f"{code} Internal"] = internal_val
                        row[f"{code} Grade"]    = grade
                    else:
                        row[code] = grade

                    # Track arrears and SGPA
                    if grade:
                        sgpa_grades[code] = grade
                        if grade not in PASSING_GRADES:
                            arrears.append(code)

                row["SGPA"]   = compute_sgpa(sgpa_grades)
                row["Status"] = "✓ PASS" if not arrears else f"✗ {len(arrears)} ARREAR(S)"
                rows.append(row)

            df = pd.DataFrame(rows)
            df.to_excel(writer, sheet_name=dept, index=False, startrow=5)

    _apply_formatting_pass(output_path)
    print(f"✅ Merged Excel saved: {output_path}")


# ── formatting post-pass ──────────────────────────────────────────────────────

def _apply_formatting_pass(path: str):
    wb = load_workbook(path)
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        max_col = ws.max_column

        # Determine sheet title
        title = f"{sheet_name} Department — University Examination Results"

        _write_sheet_header(ws, title, max_col)
        _format_header_row(ws, row=6)
        _format_data_rows(ws, start_row=7)

        # Column widths
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 24
        for i in range(3, max_col + 1):
            ws.column_dimensions[get_column_letter(i)].width = 14

    wb.save(path)
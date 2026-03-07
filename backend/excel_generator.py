# backend/excel_generator.py
import re
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from collections import defaultdict
from datetime import datetime
from models import PASSING_GRADES, compute_sgpa

COLLEGE_NAME     = "ALBERTIAN INSTITUTE OF SCIENCE AND TECHNOLOGY (AISAT)"
COLLEGE_LOCATION = "Kalamassery, Ernakulam, Kerala"

C = {
    "dark_blue":  "1E3A8A", "mid_blue":  "3B82F6",
    "pass_bg":    "D1FAE5", "pass_fg":   "065F46",
    "fail_bg":    "FEE2E2", "fail_fg":   "991B1B",
    "white":      "FFFFFF", "light_gray":"F3F4F6",
    "dark_text":  "1F2937", "skip_bg":   "F3F4F6",
    "skip_fg":    "9CA3AF",
}
THIN = Border(
    left=Side(style="thin", color="D1D5DB"), right=Side(style="thin", color="D1D5DB"),
    top=Side(style="thin",  color="D1D5DB"), bottom=Side(style="thin",color="D1D5DB"),
)
PERF_COLORS = {
    "Excellent":         ("D1FAE5", "065F46"),
    "Good":              ("DBEAFE", "1E40AF"),
    "Average":           ("FEF3C7", "92400E"),
    "Needs Improvement": ("FEE2E2", "991B1B"),
}


# ── micro helpers ─────────────────────────────────────────────────────────────

def _fill(h):
    return PatternFill(start_color=h, end_color=h, fill_type="solid")

def _font(color=C["dark_text"], bold=False, size=10):
    return Font(name="Calibri", size=size, bold=bold, color=color)

def _batch_year(usn: str) -> str:
    m = re.match(r'[A-Z]+(\d{2})', usn)
    return m.group(1) if m else ""

def _filter_batch(records, batch_year: str, field="usn"):
    if not batch_year:
        return records
    return [r for r in records if _batch_year(getattr(r, field)) == batch_year]


# ── sheet header & formatting helpers ────────────────────────────────────────

def _write_header(ws, title: str, ncols: int):
    cl = get_column_letter(ncols)
    meta = [
        (COLLEGE_NAME,     16, True,  C["white"],    C["dark_blue"]),
        (COLLEGE_LOCATION, 11, False, C["dark_text"],None),
        (title,            12, True,  C["dark_text"],C["mid_blue"]),
        (f"Generated: {datetime.now().strftime('%d %B %Y  %I:%M %p')}",
                            9, False, "6B7280",      None),
    ]
    for i, (txt, sz, bold, fg, bg) in enumerate(meta, 1):
        ws.merge_cells(f"A{i}:{cl}{i}")
        c = ws[f"A{i}"]
        c.value = txt
        c.font  = Font(name="Calibri", size=sz, bold=bold, color=fg)
        c.alignment = Alignment(horizontal="center", vertical="center")
        if bg: c.fill = _fill(bg)
        ws.row_dimensions[i].height = 22 if i < 4 else 16
    ws.row_dimensions[5].height = 6


def _fmt_col_headers(ws, row=6):
    ws.row_dimensions[row].height = 34
    for col in range(1, ws.max_column + 1):
        c = ws.cell(row=row, column=col)
        if c.value is not None:
            c.font      = Font(name="Calibri", size=10, bold=True, color=C["white"])
            c.fill      = _fill(C["dark_blue"])
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border    = THIN


def _fmt_result_data(ws, start=7):
    for r in range(start, ws.max_row + 1):
        alt = _fill(C["light_gray"] if r % 2 == 0 else C["white"])
        for col in range(1, ws.max_column + 1):
            c = ws.cell(row=r, column=col)
            if c.value is None: continue
            c.alignment = Alignment(horizontal="center", vertical="center")
            c.border    = THIN
            v = str(c.value).strip()
            if   v == "—":                     c.font, c.fill = _font(C["skip_fg"]),       _fill(C["skip_bg"])
            elif "✓" in v:                     c.font, c.fill = _font(C["pass_fg"],True),  _fill(C["pass_bg"])
            elif "✗" in v:                     c.font, c.fill = _font(C["fail_fg"],True),  _fill(C["fail_bg"])
            elif v in {"F","FE","Absent","Withheld"}: c.font, c.fill = _font(C["fail_fg"],True), _fill(C["fail_bg"])
            elif v in PASSING_GRADES:          c.font, c.fill = _font(C["pass_fg"]),       _fill(C["pass_bg"])
            else:                              c.font, c.fill = _font(),                   alt
    ws.freeze_panes = "A7"


def _fmt_analysis_data(ws, start=7):
    """Colour rows based on Performance column (last column)."""
    perf_col = ws.max_column
    for r in range(start, ws.max_row + 1):
        alt      = _fill(C["light_gray"] if r % 2 == 0 else C["white"])
        perf_val = str(ws.cell(row=r, column=perf_col).value or "").strip()
        bg_hex, fg_hex = PERF_COLORS.get(perf_val, (None, C["dark_text"]))
        for col in range(1, ws.max_column + 1):
            c = ws.cell(row=r, column=col)
            if c.value is None: continue
            c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
            c.border    = THIN
            c.font      = _font(fg_hex if (col == perf_col and bg_hex) else C["dark_text"],
                                bold=(col == perf_col and bool(bg_hex)))
            c.fill      = _fill(bg_hex) if (col == perf_col and bg_hex) else alt
        ws.row_dimensions[r].height = 18
    ws.freeze_panes = "A7"


# ── subject analysis builder ──────────────────────────────────────────────────

def _subject_analysis(ext_records, int_records, batch_year) -> pd.DataFrame:
    """
    Returns one row per subject with: code, name, faculty,
    appeared, passed, failed, pass%, performance.
    Only current-batch students, elective skips excluded.
    """
    # Subject metadata from sessional PDF
    meta = {}   # code → (name, faculty)
    for r in int_records:
        if r.course_code not in meta:
            meta[r.course_code] = (r.subject_name, r.faculty_name)

    # Which (usn, code) pairs were NOT elected
    not_elected = {(r.usn, r.course_code) for r in int_records if not r.elected}

    # Only analyse subjects that appear in the sessional PDF
    # and only for students in the same dept as the sessional PDF
    known_codes = set(meta.keys())
    sessional_usns = {r.usn for r in int_records}

    # Accumulate grades per subject (current batch, elected only, known codes only)
    code_grades = defaultdict(list)
    for r in _filter_batch(ext_records, batch_year):
        if (r.course_code in known_codes
                and r.usn in sessional_usns
                and (r.usn, r.course_code) not in not_elected):
            code_grades[r.course_code].append(r.grade)

    rows = []
    for code in sorted(code_grades):
        grades   = code_grades[code]
        appeared = len(grades)
        if appeared == 0: continue

        passed   = sum(1 for g in grades if g in PASSING_GRADES)
        failed   = appeared - passed
        pct      = round(passed / appeared * 100, 1)
        name, faculty = meta.get(code, (code, "N/A"))

        if pct >= 90:   perf = "Excellent"
        elif pct >= 75: perf = "Good"
        elif pct >= 60: perf = "Average"
        else:           perf = "Needs Improvement"

        rows.append({
            "Subject Code": code,
            "Subject Name": name,
            "Faculty":      faculty,
            "Appeared":     appeared,
            "Passed":       passed,
            "Failed":       failed,
            "Pass %":       f"{pct}%",
            "Performance":  perf,
        })
    return pd.DataFrame(rows)


# ── MODE 1 ────────────────────────────────────────────────────────────────────

def generate_external_excel(ext_records: list, output_path: str, batch_year: str = ""):
    dept_map = defaultdict(list)
    for r in _filter_batch(ext_records, batch_year) if batch_year else ext_records:
        dept_map[r.department].append(r)

    titles = {}
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        for dept in sorted(dept_map):
            recs = dept_map[dept]
            sg   = defaultdict(dict)
            for r in recs: sg[r.usn][r.course_code] = r.grade
            subs = sorted({r.course_code for r in recs})

            rows = []
            for usn in sorted(sg):
                g   = sg[usn]
                row = {"Register No": usn}
                arr = []
                for s in subs:
                    grade = g.get(s, "")
                    row[s] = grade
                    if grade and grade not in PASSING_GRADES: arr.append(s)
                row["SGPA"]   = compute_sgpa(g)
                row["Status"] = "✓ PASS" if not arr else f"✗ {len(arr)} ARREAR(S)"
                rows.append(row)

            pd.DataFrame(rows).to_excel(writer, sheet_name=dept, index=False, startrow=5)
            lbl = f" — Batch 20{batch_year}" if batch_year else ""
            titles[dept] = f"{dept} — University Examination Results{lbl}"

    _post_format(output_path, titles, analysis_sheets=set())
    print(f"✅ External-only Excel: {output_path}")


# ── MODE 2 ────────────────────────────────────────────────────────────────────

def generate_merged_excel(
    ext_records:  list,
    int_records:  list,
    name_mapping: dict,
    output_path:  str,
    batch_year:   str = "",
):
    if batch_year:
        ext_records  = _filter_batch(ext_records, batch_year)
        int_records  = _filter_batch(int_records, batch_year)
        name_mapping = {u: n for u, n in name_mapping.items()
                        if _batch_year(u) == batch_year}

    ext_lu  = defaultdict(dict)
    ext_dep = {}
    for r in ext_records:
        ext_lu[r.usn][r.course_code] = r.grade
        ext_dep[r.usn] = r.department

    int_lu = defaultdict(dict)
    for r in int_records:
        int_lu[r.usn][r.course_code] = r

    dept_usns = defaultdict(set)
    for usn, dept in ext_dep.items():
        dept_usns[dept].add(usn)

    titles = {}
    analysis_sheets = set()

    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        for dept in sorted(dept_usns):
            usns     = sorted(dept_usns[dept])
            subs     = sorted({c for u in usns for c in ext_lu[u]})
            has_int  = any(u in int_lu for u in usns)

            rows = []
            for usn in usns:
                eg  = ext_lu[usn]
                id_ = int_lu.get(usn, {})
                row = {"Register No": usn, "Name": name_mapping.get(usn, "")}
                arr, sgpa_g = [], {}

                for code in subs:
                    grade = eg.get(code, "")
                    if has_int:
                        irec = id_.get(code)
                        if irec and not irec.elected:
                            row[f"{code} Internal"] = "—"
                            row[f"{code} Grade"]    = "—"
                            continue
                        row[f"{code} Internal"] = irec.internal_mark if irec else ""
                        row[f"{code} Grade"]    = grade
                    else:
                        row[code] = grade
                    if grade:
                        sgpa_g[code] = grade
                        if grade not in PASSING_GRADES: arr.append(code)

                row["SGPA"]   = compute_sgpa(sgpa_g)
                row["Status"] = "✓ PASS" if not arr else f"✗ {len(arr)} ARREAR(S)"
                rows.append(row)

            pd.DataFrame(rows).to_excel(writer, sheet_name=dept, index=False, startrow=5)
            lbl = f" — Batch 20{batch_year}" if batch_year else ""
            titles[dept] = (
                f"{dept} — Internal + University Results{lbl}" if has_int
                else f"{dept} — University Examination Results{lbl}"
            )

        # Subject Analysis sheet
        if int_records:
            df_analysis = _subject_analysis(ext_records, int_records, batch_year)
            if not df_analysis.empty:
                df_analysis.to_excel(
                    writer, sheet_name="Subject Analysis", index=False, startrow=5
                )
                lbl = f" — Batch 20{batch_year}" if batch_year else ""
                titles["Subject Analysis"] = f"Subject-wise Pass/Fail Analysis{lbl}"
                analysis_sheets.add("Subject Analysis")

    _post_format(output_path, titles, analysis_sheets)
    print(f"✅ Merged Excel: {output_path}")


# ── post-format pass ──────────────────────────────────────────────────────────

def _post_format(path: str, titles: dict, analysis_sheets: set):
    wb = load_workbook(path)
    for sname in wb.sheetnames:
        ws    = wb[sname]
        title = titles.get(sname, sname)
        _write_header(ws, title, ws.max_column)
        _fmt_col_headers(ws, row=6)

        if sname in analysis_sheets:
            _fmt_analysis_data(ws, start=7)
            # Custom column widths for analysis
            for col, w in zip("ABCDEFGH", [13, 36, 30, 11, 10, 10, 10, 20]):
                ws.column_dimensions[get_column_letter(ord(col)-64)].width = w
        else:
            _fmt_result_data(ws, start=7)
            ws.column_dimensions["A"].width = 18
            ws.column_dimensions["B"].width = 26
    wb.save(path)
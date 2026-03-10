# backend/models.py
"""
Single source of truth for:
  - Grade points and passing grades
  - Credit registry (KTU 2019 scheme, all 5 depts, S1-S8)
  - CSV override fallback
  - SGPA computation
  - Department detection
  - Data classes
"""

import os
import csv
from dataclasses import dataclass

# ---------------------------------------------------------------------------
# GRADE SYSTEM
# ---------------------------------------------------------------------------

GRADE_POINTS = {
    "S":  10, "A+": 9, "A": 8.5, "B+": 8, "B": 7,
    "C+": 6,  "C":  5.5, "D": 5, "P": 4,
    "F": 0, "FE": 0, "Absent": 0, "Withheld": 0, "": 0,
}

PASSING_GRADES = {"S", "A+", "A", "B+", "B", "C+", "C", "D", "P"}
FAIL_GRADES    = {"F", "FE", "Absent", "Withheld"}


# ---------------------------------------------------------------------------
# CREDIT REGISTRY  (KTU 2019 Scheme, AISAT — CE, ME, EEE, ECE, CSE)
#
# 0  = mandatory non-credit course (MCN, HUN, EST200 Design in some depts)
# Credits confirmed from official KTU 2019 scheme curriculum document.
# ---------------------------------------------------------------------------

CREDIT_REGISTRY = {

    # ── S1 / S2  (common to all branches) ───────────────────────────────────
    "MAT101": 4,   "MAT102": 4,
    "PHT100": 4,   "PHT110": 4,
    "CYT100": 4,
    "EST100": 3,   "EST110": 3,
    "EST120": 4,   "EST130": 4,
    "EST102": 4,
    "HUN101": 0,   "HUN102": 0,   # Life Skills, Prof. Communication — non-credit
    "PHL120": 1,   "CYL120": 1,
    "ESL120": 1,   "ESL130": 1,

    # ── S3/S4  (common codes) ────────────────────────────────────────────────
    "EST200": 2,   # Design & Engineering
    "HUT200": 2,   # Professional Ethics
    "MCN201": 0,   # Sustainable Engineering
    "MCN202": 0,   # Constitution of India

    # ── S5/S6  (common codes) ────────────────────────────────────────────────
    "MCN301": 0,   "MCN302": 0,   # Disaster Management
    "HUT300": 3,   # Industrial Economics & Foreign Trade

    # ── S7/S8  (common codes) ────────────────────────────────────────────────
    "MCN401": 0,   # Industrial Safety Engineering

    # ════════════════════════════════════════════════════════════════════════
    # CIVIL ENGINEERING  (CET / CEL / CED / CEQ / CEN)
    # ════════════════════════════════════════════════════════════════════════
    # S3
    "MAT201": 4, "CET201": 4, "CET203": 4, "CET205": 4,
    "CEL201": 2, "CEL203": 2,
    # S4
    "MAT202": 4, "CET202": 4, "CET204": 4, "CET206": 4,
    "CEL202": 2, "CEL204": 2,
    # S5
    "CET301": 4, "CET303": 4, "CET305": 4, "CET307": 4, "CET309": 3,
    "CEL331": 2, "CEL333": 2,
    # S6
    "CET302": 4, "CET304": 4, "CET306": 4, "CET308": 1,
    "CEL332": 2, "CEL334": 2,
    "CET312": 3, "CET322": 3, "CET332": 3, "CET342": 3,   # S6 Elec I
    "CET352": 3, "CET362": 3, "CET372": 3,
    # S7
    "CET401": 3, "CEL411": 2, "CEQ413": 2, "CED415": 2,
    "CET413": 3, "CET423": 3, "CET433": 3, "CET443": 3,   # S7 Elec II
    "CET453": 3, "CET463": 3, "CET473": 3,
    "CET415": 3, "CET425": 3, "CET435": 3, "CET445": 3,   # Open electives
    "CET455": 3, "CET465": 3,
    # S8
    "CET402": 3, "CET404": 1, "CED416": 4,
    "CET414": 3, "CET424": 3, "CET434": 3, "CET444": 3,
    "CET454": 3, "CET464": 3, "CET474": 3,
    "CET416": 3, "CET426": 3, "CET436": 3, "CET446": 3,
    "CET456": 3, "CET466": 3, "CET476": 3,
    "CET418": 3, "CET428": 3, "CET438": 3, "CET448": 3,
    "CET458": 3, "CET468": 3, "CET478": 3,

    # ════════════════════════════════════════════════════════════════════════
    # MECHANICAL ENGINEERING  (MET / MEL / MED / MEQ)
    # ════════════════════════════════════════════════════════════════════════
    # S3
    "MET201": 4, "MET203": 4, "MET205": 4, "MET207": 4,
    "MEL201": 2, "MEL203": 2,
    # S4
    "MET202": 3, "MET204": 3, "MET206": 3,
    "MEL202": 1, "MEL204": 1,
    # S5
    "MET301": 4, "MET303": 4, "MET305": 4, "MET307": 4, "MET309": 3,
    "MEL331": 2, "MEL333": 2,
    # S6
    "MET302": 4, "MET304": 4, "MET306": 4, "MET308": 1,
    "MEL332": 2, "MEL334": 2,
    "MET312": 3, "MET322": 3, "MET332": 3, "MET342": 3,
    "MET352": 3, "MET362": 3,
    # S7
    "MET401": 3, "MEL411": 2, "MEQ413": 2, "MED415": 2,
    "MET413": 3, "MET423": 3, "MET433": 3, "MET443": 3,
    "MET453": 3, "MET463": 3, "MET473": 3,
    "MET445": 3,   # open elective taken by other depts
    # S8
    "MET402": 3, "MET404": 1, "MED416": 4,
    "MET414": 3, "MET424": 3, "MET434": 3, "MET444": 3,
    "MET454": 3, "MET464": 3, "MET474": 3,
    "MET416": 3, "MET426": 3, "MET436": 3, "MET446": 3,
    "MET456": 3, "MET466": 3, "MET476": 3,
    "MET418": 3, "MET428": 3, "MET438": 3, "MET448": 3,
    "MET458": 3, "MET468": 3, "MET478": 3,

    # ════════════════════════════════════════════════════════════════════════
    # ELECTRICAL & ELECTRONICS ENGINEERING  (EET / EEL / EED / EEQ)
    # ════════════════════════════════════════════════════════════════════════
    # S3
    "EET201": 4, "EET203": 4, "EET205": 4,
    "EEL201": 2, "EEL203": 2,
    # S4
    "MAT204": 4, "EET202": 3, "EET204": 3, "EET206": 3,
    "EEL202": 1, "EEL204": 1,
    # S5
    "EET301": 4, "EET303": 4, "EET305": 4, "EET307": 4, "EET309": 3,
    "EEL331": 2, "EEL333": 2,
    # S6
    "EET302": 4, "EET304": 4, "EET306": 4, "EET308": 1,
    "EEL332": 2, "EEL334": 2,
    "EET312": 3, "EET322": 3, "EET332": 3, "EET342": 3,
    "EET352": 3, "EET362": 3,
    # S7
    "EET401": 3, "EET413": 3, "EET463": 3,
    "EEL411": 2, "EEQ413": 2, "EED415": 2,
    "EET403": 3, "EET423": 3, "EET433": 3, "EET443": 3, "EET453": 3,
    "EET435": 3,   # open elective
    # S8
    "EET402": 3, "EET404": 1, "EED416": 4,
    "EET414": 3, "EET424": 3, "EET434": 3, "EET444": 3,
    "EET454": 3, "EET464": 3, "EET474": 3,
    "EET416": 3, "EET426": 3, "EET436": 3, "EET446": 3,
    "EET456": 3, "EET466": 3, "EET476": 3,
    "EET418": 3, "EET428": 3, "EET438": 3, "EET448": 3,
    "EET458": 3, "EET468": 3, "EET478": 3,

    # ════════════════════════════════════════════════════════════════════════
    # ELECTRONICS & COMMUNICATION ENGINEERING  (ECT / ECL / ECD / ECQ)
    # ════════════════════════════════════════════════════════════════════════
    # S3
    "ECT201": 4, "ECT203": 4, "ECT205": 4,
    "ECL201": 2, "ECL203": 2,
    # S4
    "ECT202": 3, "ECT204": 3, "ECT206": 3,
    "ECL202": 1, "ECL204": 1,
    # S5
    "ECT301": 4, "ECT303": 4, "ECT305": 4, "ECT307": 4, "ECT309": 3,
    "ECL331": 2, "ECL333": 2,
    # S6
    "ECT302": 4, "ECT304": 4, "ECT306": 4, "ECT308": 1,
    "ECL332": 2, "ECL334": 2,
    "ECT312": 3, "ECT322": 3, "ECT332": 3, "ECT342": 3,
    "ECT352": 3, "ECT362": 3,
    # S7
    "ECT401": 3, "ECT413": 3, "ECT443": 3, "ECT463": 3,
    "ECL411": 2, "ECQ413": 2, "ECD415": 2,
    "ECT403": 3, "ECT423": 3, "ECT433": 3, "ECT453": 3, "ECT473": 3,
    "CST435": 3,   # open elective from CS
    # S8
    "ECT402": 3, "ECT404": 1, "ECD416": 4,
    "ECT414": 3, "ECT424": 3, "ECT434": 3, "ECT444": 3,
    "ECT454": 3, "ECT464": 3, "ECT474": 3,
    "ECT416": 3, "ECT426": 3, "ECT436": 3, "ECT446": 3,
    "ECT456": 3, "ECT466": 3, "ECT476": 3,
    "ECT418": 3, "ECT428": 3, "ECT438": 3, "ECT448": 3,
    "ECT458": 3, "ECT468": 3, "ECT478": 3,

    # ════════════════════════════════════════════════════════════════════════
    # COMPUTER SCIENCE & ENGINEERING  (CST / CSL / CSD / CSQ)
    # ════════════════════════════════════════════════════════════════════════
    # S3
    "MAT203": 4,
    "CST201": 4, "CST203": 4, "CST205": 4,
    "CSL201": 2, "CSL203": 2,
    # S4
    "MAT206": 4, "CST202": 3, "CST204": 3, "CST206": 3,
    "CSL202": 1, "CSL204": 1,
    # S5
    "CST301": 4, "CST303": 4, "CST305": 4, "CST307": 4, "CST309": 3,
    "CSL331": 2, "CSL333": 2,
    # S6
    "CST302": 4, "CST304": 4, "CST306": 4, "CST308": 1,
    "CSL332": 2, "CSL334": 2,
    "CST312": 3, "CST322": 3, "CST332": 3, "CST342": 3,
    "CST352": 3, "CST362": 3,
    # S7
    "CST401": 3,
    "CST423": 3, "CST433": 3,   # mutually exclusive electives
    "ECT435": 3,                 # open elective from ECE
    "CSL411": 2, "CSQ413": 2, "CSD415": 2,
    "CST403": 3, "CST413": 3, "CST443": 3, "CST453": 3,
    "CST463": 3, "CST473": 3,
    # S8
    "CST402": 3, "CST404": 1, "CSD416": 4,
    "CST414": 3, "CST424": 3, "CST434": 3, "CST444": 3,
    "CST454": 3, "CST464": 3, "CST474": 3,
    "CST416": 3, "CST426": 3, "CST436": 3, "CST446": 3,
    "CST456": 3, "CST466": 3, "CST476": 3,
    "CST418": 3, "CST428": 3, "CST438": 3, "CST448": 3,
    "CST458": 3, "CST468": 3, "CST478": 3,
}


# ---------------------------------------------------------------------------
# CSV OVERRIDE  (backend/data/credits_override.csv)
#
# Faculty can fix or add credits without touching code.
# Format — header row required:  course_code,credits
# Example row:                   CST999,3
#
# Restart the server after editing the CSV for changes to take effect.
# ---------------------------------------------------------------------------

_CSV_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "data", "credits_override.csv"
)

def _load_csv_overrides() -> dict:
    overrides = {}
    if not os.path.exists(_CSV_PATH):
        return overrides
    with open(_CSV_PATH, newline="") as f:
        for row in csv.DictReader(f):
            code = row.get("course_code", "").strip().upper()
            try:
                overrides[code] = int(row.get("credits", "").strip())
            except ValueError:
                pass
    if overrides:
        print(f"[models] Loaded {len(overrides)} credit overrides from CSV")
    return overrides

_CSV_OVERRIDES = _load_csv_overrides()   # loaded once at import


def get_credits(course_code: str) -> int:
    """
    Lookup order:
      1. CSV override  (faculty-editable, no code change required)
      2. Hardcoded registry  (KTU 2019 scheme)
      3. Smart default from course-code structure:
           third letter N  → 0  (non-credit)
           third letter L/Q/D → 2  (lab / seminar / project)
           anything else  → 3  (theory)
    """
    code = course_code.strip().upper()
    if code in _CSV_OVERRIDES:  return _CSV_OVERRIDES[code]
    if code in CREDIT_REGISTRY: return CREDIT_REGISTRY[code]
    if len(code) >= 3:
        n = code[2]
        if n == "N":              return 0
        if n in ("L", "Q", "D"): return 2
    return 3


# ---------------------------------------------------------------------------
# HELPER FUNCTIONS
# ---------------------------------------------------------------------------

def get_status(grade: str) -> str:
    g = grade.strip()
    if g in PASSING_GRADES:  return "Pass"
    if g == "Absent":        return "Absent"
    if g == "Withheld":      return "Withheld"
    if g == "FE":            return "FE"
    return "Fail"


def compute_sgpa(subject_grades: dict) -> float:
    """
    subject_grades = { "CST401": "A", "MCN401": "P", ... }
    Zero-credit subjects are skipped.
    Returns 0.0 if no creditable subjects.
    """
    weighted, total = 0.0, 0
    for code, grade in subject_grades.items():
        cr = get_credits(code)
        if cr == 0: continue
        weighted += GRADE_POINTS.get(grade, 0) * cr
        total    += cr
    return round(weighted / total, 2) if total > 0 else 0.0


def get_department(usn: str) -> str:
    u = usn.upper()
    if "CS" in u: return "CSE"
    if "EC" in u: return "ECE"
    if "EE" in u: return "EEE"
    if "ME" in u: return "ME"
    if "CE" in u: return "CE"
    return "OTHER"


# ---------------------------------------------------------------------------
# DATA CLASSES
# ---------------------------------------------------------------------------

@dataclass
class ExternalRecord:
    usn:         str
    department:  str
    course_code: str
    grade:       str

@dataclass
class InternalRecord:
    usn:           str
    student_name:  str
    course_code:   str
    subject_name:  str
    faculty_name:  str
    internal_mark: int
    elected:       bool
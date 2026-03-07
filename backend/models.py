# backend/models.py
from dataclasses import dataclass


# ---------------------------------------------------------------------------
# GRADE CONSTANTS — single source of truth, used everywhere
# ---------------------------------------------------------------------------

PASSING_GRADES = {"S", "A+", "A", "B+", "B", "C+", "C", "D", "P"}
FAIL_GRADES    = {"F", "FE", "Absent", "Withheld"}

GRADE_POINTS = {
    "S":  10,  "A+": 9,  "A":  8.5, "B+": 8,
    "B":  7,   "C+": 6.5,"C":  6,   "D":  5.5, "P": 5,
    "F":  0,   "FE": 0,  "Absent": 0, "Withheld": 0,
}


# ---------------------------------------------------------------------------
# CREDIT REGISTRY — hardcoded per semester/scheme
# Add new semesters here when needed
# ---------------------------------------------------------------------------

CREDIT_REGISTRY = {
    # S7 CSE (2019 scheme)
    "MCN401": 0,   # non-credit
    "CST401": 3,
    "CST423": 3,   # elective
    "CST433": 3,   # elective (mutually exclusive with CST423)
    "ECT435": 3,
    "CSL411": 2,
    "CSQ413": 2,
    "CSD415": 2,

    # S7 Civil
    "CET423": 3,
    "CET401": 3,
    "MET445": 3,
    "CEL411": 2,
    "CEQ413": 2,
    "CED415": 2,
    "CET453": 3,

    # S7 Mechanical
    "MET463": 3,
    "EET435": 3,
    "MET401": 3,
    "MEL411": 2,
    "MEQ413": 2,
    "MED415": 2,
    "MET473": 3,

    # S7 EEE
    "EET401": 3,
    "EET413": 3,
    "EET463": 3,
    "CET415": 3,
    "EEL411": 2,
    "EEQ413": 2,
    "EED415": 2,

    # S7 ECE
    "ECT401": 3,
    "ECT413": 3,
    "ECT443": 3,
    "CST435": 3,
    "ECT463": 3,
    "ECL411": 2,
    "ECQ413": 2,
    "ECD415": 2,

    # S4 subjects (from previous semester support)
    "MAT202": 4, "MAT204": 4, "MAT206": 4,
    "CET202": 3, "CET204": 3, "CET206": 3,
    "CEL202": 1, "CEL204": 1,
    "EST200": 0, "MCN202": 0,
    "MET202": 3, "MET204": 3, "MET206": 3,
    "MEL202": 1, "MEL204": 1,
    "HUT200": 3,
    "EET202": 3, "EET204": 3, "EET206": 3,
    "EEL202": 1, "EEL204": 1,
    "ECT202": 3, "ECT204": 3, "ECT206": 3,
    "ECL202": 1, "ECL204": 1,
    "CST202": 3, "CST204": 3, "CST206": 3,
    "CSL202": 1, "CSL204": 1,
}


def get_credits(course_code: str) -> int:
    return CREDIT_REGISTRY.get(course_code, 3)  # default 3 if unknown


def get_status(grade: str) -> str:
    g = grade.strip()
    if g in PASSING_GRADES:
        return "Pass"
    if g == "Absent":
        return "Absent"
    if g == "Withheld":
        return "Withheld"
    if g == "FE":
        return "FE"
    return "Fail"


def compute_sgpa(subject_grades: dict) -> float:
    """
    subject_grades = { "CST401": "A", "CST423": "B+", ... }
    Skips zero-credit subjects (MCN401 etc).
    Returns 0.0 if no creditable subjects.
    """
    weighted = 0.0
    total_credits = 0

    for code, grade in subject_grades.items():
        credits = get_credits(code)
        if credits == 0:
            continue
        gp = GRADE_POINTS.get(grade, 0)
        weighted += gp * credits
        total_credits += credits

    return round(weighted / total_credits, 2) if total_credits > 0 else 0.0


def get_department(usn: str) -> str:
    """Extract department short name from USN. Single definition, used everywhere."""
    u = usn.upper()
    # Order matters: check EC before EE to avoid false match
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
    """One subject-grade entry from the KTU result PDF."""
    usn:         str
    department:  str
    course_code: str
    grade:       str


@dataclass
class InternalRecord:
    """One subject-mark entry from the college sessional PDF."""
    usn:          str
    student_name: str
    course_code:  str
    subject_name: str
    faculty_name: str
    internal_mark: int
    elected:      bool   # False = student did NOT choose this elective slot
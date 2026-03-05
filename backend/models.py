# backend/models.py
from dataclasses import dataclass
from typing import Dict, Optional

@dataclass
class InternalRecord:
    """Represents internal marks from college master file"""
    register_no: str
    student_name: str
    subject_code: str
    subject_name: str
    faculty_name: str
    internal_mark: int  # Out of 50

@dataclass
@dataclass
class ExternalRecord:
    register_no: str
    subject_code: str
    grade: str

from dataclasses import dataclass

@dataclass
class MergedRecord:
    register_no: str
    student_name: str
    subject_code: str
    subject_name: str
    faculty_name: str
    internal_mark: int
    grade: str
    department: str

    def to_dict(self):
        return {
            "Register No": self.register_no,
            "Student Name": self.student_name,
            "Subject Code": self.subject_code,
            "Subject Name": self.subject_name,
            "Faculty Name": self.faculty_name,
            "Internal Mark": self.internal_mark,
            "Grade": self.grade,
            "Department": self.department
        }

GRADE_POINTS = {
    'S': 10, 'A+': 9, 'A': 8.5, 'B+': 8, 'B': 7,
    'C+': 6.5, 'C': 6, 'D': 5.5, 'P': 5,
    'F': 0, 'FE': 0, 'Absent': 0,
}

DEFAULT_CREDITS = {
    'MCN401': 0,   # Industrial Safety Engineering (non-credit)
    'CST401': 3,   # Artificial Intelligence
    'CST423': 3,   # Cloud Computing
    'CST433': 3,   # Security in Computing
    'ECT435': 3,   # Electronic Hardware for Engineers
    'CSL411': 2,   # Compiler Lab
    'CSQ413': 2,   # Seminar
    'CSD415': 2,   # Project Phase I
}

ELECTIVES = {
    "CST423",   # Cloud Computing
}

def compute_sgpa(subject_grades: dict, internal_marks: dict) -> float:
    FAIL = {'F', 'FE', 'Absent', 'AB'}

    weighted = 0.0
    credits = 0

    for code, grade in subject_grades.items():

        internal = internal_marks.get(code, 0)

        # Skip elective not chosen (* 0)
        if internal == 0 and grade in FAIL:
            continue

        # Real failure still counts as 0 GP
        gp = GRADE_POINTS.get(grade, 0)
        cr = DEFAULT_CREDITS.get(code, 3)

        weighted += gp * cr
        credits += cr

    return round(weighted / credits, 2) if credits > 0 else 0.0

def is_skipped_elective(internal_mark: int, grade: str) -> bool:
    grade = grade.upper().strip()

    FAIL_GRADES = {"F", "FE", "AB", "ABSENT"}

    return internal_mark == 0 and grade in FAIL_GRADES
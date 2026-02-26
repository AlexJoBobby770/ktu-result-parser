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
class ExternalRecord:
    """Represents external marks from KTU PDF"""
    register_no: str
    subject_code: str
    grade: str
    external_mark: int  # Derived from grade, out of 50

@dataclass
class MergedRecord:
    """Final merged record with complete information"""
    register_no: str
    student_name: str
    subject_code: str
    subject_name: str
    faculty_name: str
    internal_mark: int
    external_mark: int
    total_mark: int
    grade: str
    result: str  # Pass/Fail
    department: str
    
    def to_dict(self):
        return {
            'Register No': self.register_no,
            'Student Name': self.student_name,
            'Subject Code': self.subject_code,
            'Subject Name': self.subject_name,
            'Faculty Name': self.faculty_name,
            'Internal Mark': self.internal_mark,
            'External Mark': self.external_mark,
            'Total Mark': self.total_mark,
            'Grade': self.grade,
            'Result': self.result,
            'Department': self.department
        }


def grade_to_marks(grade: str) -> int:
    """
    Convert KTU grade to approximate external marks (out of 50)
    
    KTU Grading:
    S = 90-100 (45-50 external)
    A+ = 85-89 (42-44)
    A = 80-84 (40-41)
    B+ = 75-79 (37-39)
    B = 70-74 (35-36)
    C+ = 65-69 (32-34)
    C = 60-64 (30-31)
    D = 55-59 (27-29)
    P = 50-54 (25-26)
    F = <50 (0-24)
    """
    grade = grade.upper().strip()
    
    grade_map = {
        'S': 47,
        'A+': 43,
        'A': 40,
        'B+': 38,
        'B': 35,
        'C+': 33,
        'C': 30,
        'D': 28,
        'P': 25,
        'F': 20,
        'FE': 0,
        'AB': 0,
        'ABSENT': 0,
        'WITHHELD': 0
    }
    
    return grade_map.get(grade, 0)
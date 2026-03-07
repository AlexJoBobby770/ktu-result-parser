# backend/data_merger.py
from typing import List, Dict, Tuple
from collections import defaultdict


FAIL_GRADES = {"F", "FE", "AB", "ABSENT"}


def is_skipped_elective(internal_mark: int, grade: str) -> bool:
    """
    Detect electives that were not chosen.
    Pattern from AISAT sessional sheet:
        * 0  → internal_mark = 0
        grade = Absent
    """
    grade = grade.upper().strip()
    return internal_mark == 0 and grade in FAIL_GRADES


def merge_results(internal_records, external_records, name_mapping):

    merged = []

    internal_students = set(r.register_no for r in internal_records)

    # {regno: {subject_code: grade}}
    external_lookup = defaultdict(dict)

    for r in external_records:
        if r.register_no in internal_students:
            external_lookup[r.register_no][r.subject_code] = r.grade

    for rec in internal_records:

        regno = rec.register_no

        grade = external_lookup.get(regno, {}).get(rec.subject_code, "Absent")

       

        merged.append(
            MergedRecord(
                register_no=regno,
                student_name=name_mapping.get(regno, rec.student_name),
                subject_code=rec.subject_code,
                subject_name=rec.subject_name,
                faculty_name=rec.faculty_name,
                internal_mark=rec.internal_mark,
                grade=grade,
                department=get_department_from_regno(regno),
            )
        )

    return merged, {"total_merged": len(merged)}


def get_department_from_regno(regno: str) -> str:
    """Extract department from register number"""

    regno = regno.upper()

    if "CS" in regno:
        return "CSE"

    if "EE" in regno and "EEE" not in regno:
        return "EEE"

    if "EC" in regno:
        return "ECE"

    if "ME" in regno:
        return "ME"

    if "CE" in regno and "ECE" not in regno:
        return "CE"

    return "OTHER"
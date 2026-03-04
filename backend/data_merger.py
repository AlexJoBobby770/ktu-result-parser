# backend/data_merger.py
from typing import List, Dict, Tuple
from models import InternalRecord, ExternalRecord, MergedRecord, grade_to_marks
from collections import defaultdict


def merge_results(
    internal_records: List[InternalRecord],
    external_records: List[ExternalRecord],
    name_mapping: Dict[str, str]
) -> Tuple[List[MergedRecord], Dict]:
    """
    Merge internal and external records.
    ONLY processes students who appear in internal records (same department).
    """
    
    merged = []
    
    # Get all register numbers from internal records (CSE students)
    internal_students = set(r.register_no for r in internal_records)
    
    print(f"   🎯 Filtering for {len(internal_students)} students from internal marks")
    
    # Filter external records to ONLY include students from internal
    external_records_filtered = [
        r for r in external_records 
        if r.register_no in internal_students
    ]
    
    print(f"   ✂️  Filtered external records: {len(external_records)} → {len(external_records_filtered)}")
    
    # Create lookup dictionaries
    internal_lookup = {
        (r.register_no, r.subject_code): r 
        for r in internal_records
    }
    
    external_lookup = {
        (r.register_no, r.subject_code): r 
        for r in external_records_filtered  # Use filtered records
    }
    
    # Get all unique combinations
    all_keys = set(internal_lookup.keys()) | set(external_lookup.keys())
    
    # Statistics
    stats = {
        'total_merged': 0,
        'internal_only': 0,
        'external_only': 0,
        'both': 0,
        'missing_names': 0,
        'students_processed': set(),
        'subjects_processed': set()
    }
    
    for (regno, subj_code) in all_keys:
        internal_rec = internal_lookup.get((regno, subj_code))
        external_rec = external_lookup.get((regno, subj_code))
        
        # Get student name
        student_name = name_mapping.get(regno, "")
        if not student_name and internal_rec:
            student_name = internal_rec.student_name
        
        if not student_name:
            stats['missing_names'] += 1
        
        # Get department
        dept = get_department_from_regno(regno)
        
        # Case 1: Both internal and external exist (ideal)
        if internal_rec and external_rec:
            internal_mark = internal_rec.internal_mark
            external_mark = external_rec.external_mark
            grade = external_rec.grade
            stats['both'] += 1
            
        # Case 2: Only internal exists (student didn't appear for exam)
        elif internal_rec and not external_rec:
            internal_mark = internal_rec.internal_mark
            external_mark = 0
            grade = "Absent"
            stats['internal_only'] += 1
            
        # Case 3: Only external exists (shouldn't happen after filtering)
        elif external_rec and not internal_rec:
            internal_mark = 0
            external_mark = external_rec.external_mark
            grade = external_rec.grade
            stats['external_only'] += 1
            
        else:
            continue
        
        # Calculate total and result
        total_mark = internal_mark + external_mark
        
        # Pass/Fail logic: Need 40+ total AND 17.5+ external
        external_pass = external_mark >= 17.5
        total_pass = total_mark >= 40
        result = "Pass" if (external_pass and total_pass and grade not in ["F", "FE", "Absent"]) else "Fail"
        
        # Get subject and faculty info from internal record
        subject_name = internal_rec.subject_name if internal_rec else subj_code
        faculty_name = internal_rec.faculty_name if internal_rec else "N/A"
        
        # Create merged record
        merged_record = MergedRecord(
            register_no=regno,
            student_name=student_name,
            subject_code=subj_code,
            subject_name=subject_name,
            faculty_name=faculty_name,
            internal_mark=internal_mark,
            external_mark=external_mark,
            total_mark=total_mark,
            grade=grade,
            result=result,
            department=dept
        )
        
        merged.append(merged_record)
        
        stats['students_processed'].add(regno)
        stats['subjects_processed'].add(subj_code)
    
    stats['total_merged'] = len(merged)
    stats['unique_students'] = len(stats['students_processed'])
    stats['unique_subjects'] = len(stats['subjects_processed'])
    
    # Convert sets to lists for JSON
    stats['students_processed'] = sorted(list(stats['students_processed']))[:10]
    stats['subjects_processed'] = sorted(list(stats['subjects_processed']))
    
    return merged, stats


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
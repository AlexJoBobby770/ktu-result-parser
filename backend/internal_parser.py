# backend/internal_parser.py
from email.mime import text
import re
import PyPDF2
from typing import List, Dict, Tuple
from models import InternalRecord


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF"""
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text


def parse_subject_mapping(text: str) -> Dict[str, Tuple[str, str]]:
    """
    Parse the subject code to subject name and faculty mapping from the footer table.
    
    Returns:
        Dict mapping subject_code -> (subject_name, faculty_name)
    """
    subject_map = {}
    
    # Look for lines that start with a number followed by subject code
    # Example: "1 MCN401 INDUSTRIAL SAFETY ENGINEERING Ms. Shruthi Chandran"
    pattern = r'\d+\s+([A-Z]{3}\d{3})\s+([A-Z\s]+(?:[A-Z\s]+)?)\s+(?:Ms\.|Mr\.|Dr\.)\s+([A-Za-z\s.]+)'
    
    matches = re.findall(pattern, text)
    
    for match in matches:
        code = match[0].strip()
        subject_name = match[1].strip()
        faculty_name = match[2].strip()
        
        # Store or update mapping (some subjects may have multiple faculty)
        if code not in subject_map:
            subject_map[code] = (subject_name, faculty_name)
        else:
            # If subject already exists, append faculty name
            existing_subject, existing_faculty = subject_map[code]
            subject_map[code] = (existing_subject, f"{existing_faculty}, {faculty_name}")
    
    return subject_map


def parse_internal_marks(pdf_path: str) -> Tuple[List[InternalRecord], Dict[str, str]]:
    """
    Fully dynamic internal marks parser.
    Works for any semester, any subject count.
    """

    text = extract_text_from_pdf(pdf_path)

    # ---------------------------------------------------
    # 1️⃣ Extract subject metadata from footer
    # ---------------------------------------------------
    subject_map = parse_subject_mapping(text)

    if not subject_map:
        raise ValueError("Could not extract subject metadata from footer")

    subject_codes = list(subject_map.keys())
    subject_count = len(subject_codes)

    # ---------------------------------------------------
    # 2️⃣ Convert entire text into token stream
    # ---------------------------------------------------
    tokens = text.split()

    records = []
    name_mapping = {}

    i = 0
    total_tokens = len(tokens)

    reg_pattern = re.compile(r'^(AIK|LAIK|SGI)\d{2}[A-Z]{2}\d{3}$')

    while i < total_tokens:

        token = tokens[i]

        # Detect register number
        if reg_pattern.match(token):

            regno = token
            i += 1

            # ---------------------------------------------------
            # Extract student name (until first numeric mark)
            # ---------------------------------------------------
            name_parts = []
            while i < total_tokens and not re.match(r'^\d+(\.\d+)?$', tokens[i]):
                name_parts.append(tokens[i])
                i += 1

            student_name = " ".join(name_parts).strip()
            name_mapping[regno] = student_name

            # ---------------------------------------------------
            # Extract marks dynamically
            # For each subject: mark + attendance
            # ---------------------------------------------------
            marks = []

            for _ in range(subject_count):

                # Skip "*" if present
                if i < total_tokens and tokens[i] == "*":
                    i += 1

                # Internal mark
                if i < total_tokens and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    mark = int(float(tokens[i]))
                    marks.append(mark)
                    i += 1
                else:
                    marks.append(0)

                # Skip attendance %
                if i < total_tokens and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                    i += 1

            # Skip total column if present
            if i < total_tokens and re.match(r'^\d+(\.\d+)?$', tokens[i]):
                i += 1

            # ---------------------------------------------------
            # Create records
            # ---------------------------------------------------
            for idx, subject_code in enumerate(subject_codes):

                subject_name, faculty_name = subject_map.get(
                    subject_code,
                    (subject_code, "N/A")
                )

                record = InternalRecord(
                    register_no=regno,
                    student_name=student_name,
                    subject_code=subject_code,
                    subject_name=subject_name,
                    faculty_name=faculty_name,
                    internal_mark=marks[idx] if idx < len(marks) else 0
                )

                records.append(record)

        else:
            i += 1

    return records, name_mapping

def validate_internal_data(records: List[InternalRecord]) -> Dict:
    """Validate and provide statistics about internal marks"""
    
    if not records:
        return {
            "valid": False,
            "error": "No records found"
        }
    
    # Check for invalid marks
    invalid_marks = [r for r in records if r.internal_mark < 0 or r.internal_mark > 50]
    
    # Get unique counts
    unique_students = set(r.register_no for r in records)
    unique_subjects = set(r.subject_code for r in records)
    unique_faculty = set(r.faculty_name for r in records)
    
    # Get subject statistics
    subject_stats = {}
    for record in records:
        if record.subject_code not in subject_stats:
            subject_stats[record.subject_code] = {
                'name': record.subject_name,
                'faculty': record.faculty_name,
                'count': 0,
                'total': 0,
                'max': 0,
                'min': 50
            }
        
        stats = subject_stats[record.subject_code]
        stats['count'] += 1
        stats['total'] += record.internal_mark
        stats['max'] = max(stats['max'], record.internal_mark)
        stats['min'] = min(stats['min'], record.internal_mark)
    
    # Calculate averages
    for code in subject_stats:
        stats = subject_stats[code]
        stats['average'] = round(stats['total'] / stats['count'], 2)
    
    return {
        "valid": len(invalid_marks) == 0,
        "total_records": len(records),
        "unique_students": len(unique_students),
        "unique_subjects": len(unique_subjects),
        "unique_faculty": len(unique_faculty),
        "invalid_marks_count": len(invalid_marks),
        "students": sorted(list(unique_students))[:5],  # Sample
        "subjects": {code: stats['name'] for code, stats in subject_stats.items()},
        "subject_stats": subject_stats
    }


if __name__ == "__main__":
    # Test the parser
    import sys
    
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "Sessionals_S7_CSE.pdf"
    
    print(f"📄 Parsing: {pdf_path}\n")
    
    records, name_map = parse_internal_marks(pdf_path)
    
    print(f"✅ Found {len(records)} internal mark records")
    print(f"✅ Found {len(name_map)} students\n")
    
    # Show validation stats
    stats = validate_internal_data(records)
    print("📊 Validation Stats:")
    print(f"  - Total Records: {stats['total_records']}")
    print(f"  - Unique Students: {stats['unique_students']}")
    print(f"  - Unique Subjects: {stats['unique_subjects']}")
    print(f"  - Unique Faculty: {stats['unique_faculty']}")
    print(f"\n📚 Subjects Found:")
    for code, name in stats['subjects'].items():
        subject_stats = stats['subject_stats'][code]
        print(f"  - {code}: {name}")
        print(f"    Faculty: {subject_stats['faculty']}")
        print(f"    Avg: {subject_stats['average']}, Max: {subject_stats['max']}, Min: {subject_stats['min']}")
    
    print(f"\n👥 Sample Students:")
    for regno in stats['students']:
        print(f"  - {regno}: {name_map[regno]}")
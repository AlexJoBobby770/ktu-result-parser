import re
from typing import List, Dict, Optional
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")


def parse_ktu_results(pdf_text: str) -> List[Dict]:
    results = []

    student_blocks = re.split(r'(?=Register No:)', pdf_text)
    
    for block in student_blocks:
        if not block.strip():
            continue

        reg_match = re.search(r'Register No[:\s]+(\d+)', block, re.IGNORECASE)
        if not reg_match:
            continue
        
        register_no = reg_match.group(1)

        name_match = re.search(r'Name[:\s]+([A-Z\s]+)', block, re.IGNORECASE)
        student_name = name_match.group(1).strip() if name_match else "Unknown"

        subject_pattern = r'Subject Code[:\s]+([A-Z0-9]+).*?Subject Name[:\s]+([^|]+).*?Grade[:\s]+([A-Z+\-]+).*?Credits[:\s]+(\d+)'
        
        subjects = re.finditer(subject_pattern, block, re.IGNORECASE | re.DOTALL)
        
        for subject in subjects:
            result_entry = {
                'register_no': register_no,
                'student_name': student_name,
                'subject_code': subject.group(1).strip(),
                'subject_name': subject.group(2).strip(),
                'grade': subject.group(3).strip(),
                'credits': int(subject.group(4))
            }

            result_entry['status'] = get_pass_status(result_entry['grade'])
            
            results.append(result_entry)
    
    return results


def get_pass_status(grade: str) -> str:
 
    passing_grades = ['A+', 'A', 'B+', 'B', 'C']
    
    if grade.upper() in passing_grades:
        return "Pass"
    else:
        return "Fail"


def validate_parsed_results(results: List[Dict]) -> bool:

    if not results:
        return False
    
    required_fields = ['register_no', 'student_name', 'subject_code', 
                       'subject_name', 'grade', 'credits', 'status']
    
    for result in results:
        if not all(field in result for field in required_fields):
            return False
    
    return True
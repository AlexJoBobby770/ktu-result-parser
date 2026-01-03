"""
PDF Parser for KTU Result Files
Extracts student results using regex patterns
"""

import re
from typing import List, Dict, Optional
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text as a single string
        
    Raises:
        Exception: If PDF cannot be read
    """
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            
            # Extract text from all pages
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")


def parse_ktu_results(pdf_text: str) -> List[Dict]:
    """
    Parse KTU result data from extracted PDF text.
    
    This is a SAMPLE parser - you'll need to adjust regex patterns
    based on your actual KTU result PDF format.
    
    Expected PDF format (example):
    Register No: 123456789
    Name: JOHN DOE
    Subject Code: CS101 | Subject Name: Programming | Grade: A+ | Credits: 4
    Subject Code: CS102 | Subject Name: Data Structures | Grade: B | Credits: 3
    
    Args:
        pdf_text: Text extracted from PDF
        
    Returns:
        List of dictionaries containing student results
    """
    results = []
    
    # Pattern to find student blocks (adjust based on your PDF format)
    # This pattern looks for "Register No:" followed by content until next "Register No:" or end
    student_blocks = re.split(r'(?=Register No:)', pdf_text)
    
    for block in student_blocks:
        if not block.strip():
            continue
            
        # Extract Register Number
        reg_match = re.search(r'Register No[:\s]+(\d+)', block, re.IGNORECASE)
        if not reg_match:
            continue
        
        register_no = reg_match.group(1)
        
        # Extract Name
        name_match = re.search(r'Name[:\s]+([A-Z\s]+)', block, re.IGNORECASE)
        student_name = name_match.group(1).strip() if name_match else "Unknown"
        
        # Extract subject results
        # Pattern: Subject Code: XXX | Subject Name: YYY | Grade: Z | Credits: N
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
            
            # Add pass/fail status based on grade
            result_entry['status'] = get_pass_status(result_entry['grade'])
            
            results.append(result_entry)
    
    return results


def get_pass_status(grade: str) -> str:
    """
    Determine pass/fail status from grade.
    
    KTU Grading: A+, A, B+, B, C are passing grades
    D, E, F are failing grades
    
    Args:
        grade: Letter grade (e.g., "A+", "B", "F")
        
    Returns:
        "Pass" or "Fail"
    """
    passing_grades = ['A+', 'A', 'B+', 'B', 'C']
    
    if grade.upper() in passing_grades:
        return "Pass"
    else:
        return "Fail"


def validate_parsed_results(results: List[Dict]) -> bool:
    """
    Validate that parsed results have required fields.
    
    Args:
        results: List of parsed result dictionaries
        
    Returns:
        True if valid, False otherwise
    """
    if not results:
        return False
    
    required_fields = ['register_no', 'student_name', 'subject_code', 
                       'subject_name', 'grade', 'credits', 'status']
    
    for result in results:
        if not all(field in result for field in required_fields):
            return False
    
    return True
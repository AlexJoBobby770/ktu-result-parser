import re
from typing import List, Dict
import PyPDF2


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract raw text from PDF"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            return text
    except Exception as e:
        raise Exception(f"Failed to read PDF: {str(e)}")


def parse_ktu_results(pdf_path: str) -> List[Dict]:
    """
    Parse KTU results from PDF
    Returns list of dicts with student results
    """
    # Extract text first
    full_text = extract_text_from_pdf(pdf_path)
    
    results = []
    
    # Split by department headers (all caps with ENGINEERING)
    dept_sections = re.split(r'\n([A-Z\s&]+ENGINEERING.*?)\n', full_text)
    
    # Process each department
    for i in range(1, len(dept_sections), 2):
        dept_name = dept_sections[i].strip()
        dept_data = dept_sections[i+1] if i+1 < len(dept_sections) else ""
        
        # Find all register numbers (AIKxxXXxxx pattern)
        student_blocks = re.split(r'(AIK\d{2}[A-Z]{2}\d{3})', dept_data)
        
        # Process each student
        for j in range(1, len(student_blocks), 2):
            regno = student_blocks[j]
            data_block = student_blocks[j+1] if j+1 < len(student_blocks) else ""
            
            # Extract CourseCode(Grade) patterns
            # Matches: MAT202(F), CET204(P), CET206(Absent), etc.
            subjects = re.findall(
                r'([A-Z]{3}\d{3})\(([A-Z+]+|Absent|Withheld|FE)\)', 
                data_block
            )
            
            # Create one record per subject
            for course_code, grade in subjects:
                status = get_pass_status(grade)
                
                results.append({
                    'department': dept_name,
                    'register_no': regno,
                    'course_code': course_code,
                    'grade': grade,
                    'status': status
                })
    
    return results


def get_pass_status(grade: str) -> str:
    """Determine if grade is passing or failing"""
    passing_grades = ['S', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'P']
    
    if grade in passing_grades:
        return "Pass"
    else:
        return "Fail"


def validate_parsed_results(results: List[Dict]) -> bool:
    """Check if parsing was successful"""
    if not results:
        return False
    
    required_fields = ['department', 'register_no', 'course_code', 
                       'grade', 'status']
    
    for result in results:
        if not all(field in result for field in required_fields):
            return False
    
    return True


# Test function
if __name__ == "__main__":
    import sys
    
    # Use command line arg or default
    if len(sys.argv) > 1:
        pdf_file = sys.argv[1]
    else:
        pdf_file = "../master .pdf"  # Your actual PDF
    
    print(f"📄 Parsing: {pdf_file}")
    
    try:
        results = parse_ktu_results(pdf_file)
        
        print(f"\n✅ Extracted {len(results)} records")
        
        if results:
            print("\n📊 First 5 records:")
            for r in results[:5]:
                print(r)
            
            # Department summary
            depts = {}
            for r in results:
                dept = r['department']
                depts[dept] = depts.get(dept, 0) + 1
            
            print("\n📈 Department-wise count:")
            for dept, count in depts.items():
                print(f"  {dept}: {count} records")
        else:
            print("⚠️ No records extracted. PDF format might be different.")
            
    except Exception as e:
        print(f"❌ Error: {e}")
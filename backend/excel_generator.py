import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict


def generate_excel_report(students: List[Dict], output_path: str):
    """
    Generate Excel report from parsed student data
    
    Input format:
    [
        {
            "register_no": "AIK23CE035",
            "department": "CIVIL ENGINEERING[Full Time]",
            "subjects": {"MAT202": "AB", "EST200": "F"},
            "status": "Fail"
        }
    ]
    """
    
    # Convert nested structure to flat rows
    flat_data = []
    for student in students:
        regno = student['register_no']
        dept = student['department']
        status = student['status']
        
        for subject_code, grade in student['subjects'].items():
            flat_data.append({
                'Register No': regno,
                'Department': dept,
                'Subject Code': subject_code,
                'Grade': grade,
                'Status': 'Pass' if grade not in ['F', 'FE', 'AB', 'Absent', 'Withheld'] else 'Fail'
            })
    
    # Create DataFrame
    df = pd.DataFrame(flat_data)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: MASTER (all data)
        df.to_excel(writer, sheet_name='MASTER', index=False)
        
        # Sheet 2+: Department-wise sheets
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            # Truncate sheet name to 31 chars (Excel limit)
            sheet_name = dept[:31]
            dept_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Last Sheet: SUMMARY
        summary_data = []
        for dept in df['Department'].unique():
            dept_df = df[df['Department'] == dept]
            
            total_records = len(dept_df)
            passed = len(dept_df[dept_df['Status'] == 'Pass'])
            failed = total_records - passed
            
            # Count unique students
            unique_students = dept_df['Register No'].nunique()
            
            summary_data.append({
                'Department': dept,
                'Total Students': unique_students,
                'Total Subject Records': total_records,
                'Passed Subjects': passed,
                'Failed Subjects': failed,
                'Pass Rate %': round((passed / total_records) * 100, 2) if total_records > 0 else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='SUMMARY', index=False)
    
    # Apply styling
    wb = load_workbook(output_path)
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Header styling
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = min(max_length + 2, 50)
    
    wb.save(output_path)
    print(f"✅ Excel generated: {output_path}")
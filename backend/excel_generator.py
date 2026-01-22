import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from typing import List, Dict


def generate_excel_report(students: List[Dict], output_path: str):
    """
    Generate Excel report with ONE SHEET PER DEPARTMENT
    
    Each sheet contains:
    - All students from that department
    - All their subjects
    - Pass/Fail analysis
    """
    
    # Convert nested structure to flat rows
    flat_data = []
    for student in students:
        regno = student['register_no']
        dept = student['department']
        
        for subject_code, grade in student['subjects'].items():
            flat_data.append({
                'Register No': regno,
                'Department': dept,
                'Subject Code': subject_code,
                'Grade': grade,
                'Status': 'Pass' if grade not in ['F', 'FE', 'AB', 'Absent', 'Withheld'] else 'Fail'
            })
    
    df = pd.DataFrame(flat_data)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Create ONE SHEET PER DEPARTMENT
        for dept in sorted(df['Department'].unique()):
            dept_df = df[df['Department'] == dept].copy()
            
            # Clean department name for sheet (Excel limit: 31 chars)
            sheet_name = dept.replace('[Full Time]', '').strip()[:31]
            
            # Sort by register number then subject
            dept_df = dept_df.sort_values(['Register No', 'Subject Code'])
            
            # Write to sheet
            dept_df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Add summary statistics at the bottom
            worksheet = writer.sheets[sheet_name]
            last_row = len(dept_df) + 2  # +2 for header and gap
            
            # Calculate stats
            total_students = dept_df['Register No'].nunique()
            total_records = len(dept_df)
            passed_records = len(dept_df[dept_df['Status'] == 'Pass'])
            failed_records = total_records - passed_records
            
            # Students with any failure
            failed_students = dept_df[dept_df['Status'] == 'Fail']['Register No'].nunique()
            
            # Write summary
            summary_row = last_row + 1
            worksheet[f'A{summary_row}'] = 'SUMMARY'
            worksheet[f'A{summary_row}'].font = Font(bold=True, size=12)
            
            worksheet[f'A{summary_row + 1}'] = 'Total Students:'
            worksheet[f'B{summary_row + 1}'] = total_students
            
            worksheet[f'A{summary_row + 2}'] = 'Students with Arrears:'
            worksheet[f'B{summary_row + 2}'] = failed_students
            
            worksheet[f'A{summary_row + 3}'] = 'Total Subject Records:'
            worksheet[f'B{summary_row + 3}'] = total_records
            
            worksheet[f'A{summary_row + 4}'] = 'Passed Subjects:'
            worksheet[f'B{summary_row + 4}'] = passed_records
            
            worksheet[f'A{summary_row + 5}'] = 'Failed Subjects:'
            worksheet[f'B{summary_row + 5}'] = failed_records
            
            worksheet[f'A{summary_row + 6}'] = 'Pass Rate:'
            worksheet[f'B{summary_row + 6}'] = f"{round((passed_records / total_records) * 100, 2)}%"
    
    # Apply styling
    wb = load_workbook(output_path)
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Header styling
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF", size=11)
            cell.fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
            cell.alignment = Alignment(horizontal="center", vertical="center")
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = min(max_length + 3, 50)
        
        # Highlight failed subjects in red
        for row in ws.iter_rows(min_row=2, max_col=5):
            if row[4].value == 'Fail':  # Status column
                row[3].font = Font(color="FF0000", bold=True)  # Grade column in red
    
    wb.save(output_path)
    print(f"✅ Excel generated: {output_path}")



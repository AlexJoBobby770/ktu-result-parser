import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from typing import List, Dict


def generate_excel_report(results: List[Dict], output_path: str):
    """
    Generate Excel report with multiple sheets:
    - MASTER: All results
    - Department-wise sheets
    - SUMMARY: Statistics
    """
    
    # Convert to DataFrame
    df = pd.DataFrame(results)
    
    # Create Excel writer
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # Sheet 1: MASTER (all data)
        df.to_excel(writer, sheet_name='MASTER', index=False)
        
        # Sheet 2+: Each department
        for dept in df['department'].unique():
            dept_df = df[df['department'] == dept]
            sheet_name = dept[:31]  # Excel limit
            dept_df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Last Sheet: SUMMARY
        summary_data = []
        for dept in df['department'].unique():
            dept_df = df[df['department'] == dept]
            
            total = len(dept_df)
            passed = len(dept_df[dept_df['status'] == 'Pass'])
            failed = total - passed
            
            # Count students (not records)
            unique_students = dept_df['register_no'].nunique()
            
            summary_data.append({
                'Department': dept,
                'Total Students': unique_students,
                'Total Records': total,
                'Pass Count': passed,
                'Fail Count': failed,
                'Pass %': round((passed / total) * 100, 2) if total > 0 else 0
            })
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='SUMMARY', index=False)
    
    # Format Excel (optional styling)
    wb = load_workbook(output_path)
    
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        
        # Header styling
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="667eea", end_color="667eea", fill_type="solid")
            cell.alignment = Alignment(horizontal="center")
        
        # Auto-width columns
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            ws.column_dimensions[column_letter].width = max_length + 2
    
    wb.save(output_path)
    print(f"✅ Excel generated: {output_path}")


if __name__ == "__main__":
    # Test with dummy data
    test_data = [
        {'department': 'CIVIL', 'register_no': 'AIK23CE001', 'course_code': 'MAT202', 'grade': 'A', 'status': 'Pass'},
        {'department': 'CIVIL', 'register_no': 'AIK23CE001', 'course_code': 'CET202', 'grade': 'F', 'status': 'Fail'},
        {'department': 'MECH', 'register_no': 'AIK23ME001', 'course_code': 'MAT202', 'grade': 'B', 'status': 'Pass'},
    ]
    
    generate_excel_report(test_data, "test_output.xlsx")
# backend/excel_generator.py (BEAUTIFUL VERSION)
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List
from collections import defaultdict
from datetime import datetime


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


def generate_excel_report(external_records, output_path):
    """
    Generate beautiful Excel report from ExternalRecord objects
    (Used when only external PDF is uploaded, no internal marks)
    """
    
    COLLEGE_NAME = "ALBERTIAN INSTITUTE OF SCIENCE AND TECHNOLOGY (AISAT)"
    COLLEGE_LOCATION = "Kalamassery, Kerala"
    
    # Convert ExternalRecord objects to student dictionary format
    students_dict = {}
    
    for record in external_records:
        regno = record.register_no
        
        if regno not in students_dict:
            students_dict[regno] = {
                "register_no": regno,
                "subjects": {},
                "department": get_department_from_regno(regno)
            }
        
        students_dict[regno]["subjects"][record.subject_code] = record.grade
    
    # Convert to list
    students = list(students_dict.values())
    
    # Group by department
    dept_students = defaultdict(list)
    for student in students:
        dept = student["department"]
        dept_students[dept].append(student)
    
    # Generate Excel with proper structure
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        
        for dept, dept_list in dept_students.items():
            
            # Get all subjects for this department
            dept_subjects = set()
            for s in dept_list:
                dept_subjects.update(s["subjects"].keys())
            dept_subjects = sorted(dept_subjects)
            
            # Build rows with Status column
            rows = []
            for s in dept_list:
                row = {
                    "Register No": s["register_no"]
                }
                
                arrears = []
                for sub in dept_subjects:
                    grade = s["subjects"].get(sub, "")
                    row[sub] = grade
                    
                    # Count arrears
                    if grade in ["F", "FE", "AB", "Absent", "Withheld"]:
                        arrears.append(sub)
                
                # Add status column
                if len(arrears) == 0:
                    row["Status"] = "✓ PASS"
                else:
                    row["Status"] = f"✗ {len(arrears)} ARREAR(S)"
                
                rows.append(row)
            
            # Create DataFrame and write to Excel (start at row 6 for header space)
            df = pd.DataFrame(rows).sort_values("Register No")
            df.to_excel(writer, sheet_name=dept, index=False, startrow=5)
            
            # Access worksheet for formatting
            ws = writer.sheets[dept]
            
            # Calculate statistics
            fail_grades = ["F", "FE", "AB", "Absent", "Withheld"]
            
            def has_fail(row):
                return any(
                    row[sub] in fail_grades
                    for sub in dept_subjects
                    if sub in row
                )
            
            total_students = len(df)
            failed_students = sum(1 for _, row in df.iterrows() if has_fail(row))
            passed_students = total_students - failed_students
            pass_pct = round((passed_students / total_students) * 100, 2) if total_students > 0 else 0
            
            # Add statistics below the data
            last_row = len(df) + 8  # 5 (header) + len(df) + 1 (data) + 2 (spacing)
            
            # Department Summary
            ws[f"A{last_row}"] = "DEPARTMENT SUMMARY"
            ws[f"A{last_row}"].font = Font(name='Calibri', size=12, bold=True)
            ws[f"A{last_row}"].fill = PatternFill("solid", fgColor="1E3A8A")
            ws[f"A{last_row}"].font = Font(name='Calibri', size=12, bold=True, color="FFFFFF")
            
            ws[f"A{last_row + 1}"] = "Total Students"
            ws[f"B{last_row + 1}"] = total_students
            ws[f"B{last_row + 1}"].font = Font(bold=True)
            
            ws[f"A{last_row + 2}"] = "Students with Arrears"
            ws[f"B{last_row + 2}"] = failed_students
            ws[f"B{last_row + 2}"].font = Font(bold=True, color="CC0000")
            
            ws[f"A{last_row + 3}"] = "Pass Percentage"
            ws[f"B{last_row + 3}"] = f"{pass_pct}%"
            ws[f"B{last_row + 3}"].font = Font(bold=True, color="16A34A")
            
            # Subject-wise Analysis (FIXED - Only count students who attempted)
            subject_analysis_start = last_row + 5
            ws[f"A{subject_analysis_start}"] = "SUBJECT-WISE ANALYSIS"
            ws[f"A{subject_analysis_start}"].font = Font(name='Calibri', size=12, bold=True, color="FFFFFF")
            ws[f"A{subject_analysis_start}"].fill = PatternFill("solid", fgColor="1E3A8A")
            
            # Merge cells for section header
            ws.merge_cells(f"A{subject_analysis_start}:F{subject_analysis_start}")
            ws[f"A{subject_analysis_start}"].alignment = Alignment(horizontal="center", vertical="center")
            
            # Headers
            headers_row = subject_analysis_start + 1
            ws[f"A{headers_row}"] = "Subject Code"
            ws[f"B{headers_row}"] = "Appeared"
            ws[f"C{headers_row}"] = "Passed"
            ws[f"D{headers_row}"] = "Failed"
            ws[f"E{headers_row}"] = "Pass %"
            ws[f"F{headers_row}"] = "Performance"
            
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                ws[f"{col}{headers_row}"].font = Font(name='Calibri', size=10, bold=True, color="FFFFFF")
                ws[f"{col}{headers_row}"].fill = PatternFill("solid", fgColor="3B82F6")
                ws[f"{col}{headers_row}"].alignment = Alignment(horizontal="center", vertical="center")
            
            # Calculate statistics per subject
            current_row = headers_row + 1
            
            for subject in dept_subjects:
                # FIXED: Only count students who actually appeared for this subject
                # (not everyone opts for electives)
                subject_grades = [
                    s["subjects"].get(subject) 
                    for s in dept_list 
                    if subject in s["subjects"] and s["subjects"][subject] != ""
                ]
                
                appeared = len(subject_grades)  # Only those who appeared
                failed = sum(1 for g in subject_grades if g in fail_grades)
                passed = appeared - failed
                pass_pct = (passed / appeared * 100) if appeared > 0 else 0
                
                # Performance rating
                if pass_pct >= 90:
                    performance = "Excellent"
                    perf_color = "16A34A"
                elif pass_pct >= 75:
                    performance = "Good"
                    perf_color = "2563EB"
                elif pass_pct >= 60:
                    performance = "Average"
                    perf_color = "CA8A04"
                else:
                    performance = "Needs Improvement"
                    perf_color = "DC2626"
                
                ws[f"A{current_row}"] = subject
                ws[f"B{current_row}"] = appeared
                ws[f"C{current_row}"] = passed
                ws[f"D{current_row}"] = failed
                ws[f"E{current_row}"] = f"{round(pass_pct, 1)}%"
                ws[f"F{current_row}"] = performance
                ws[f"F{current_row}"].font = Font(bold=True, color=perf_color)
                
                # Highlight high failure rate (>50%)
                if pass_pct < 50:
                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        ws[f"{col}{current_row}"].fill = PatternFill("solid", fgColor="FEE2E2")
                
                current_row += 1
    
    # Apply beautiful formatting
    apply_formatting(output_path, COLLEGE_NAME, COLLEGE_LOCATION)
    
    print(f"✅ Beautiful Excel generated: {output_path}")
    print(f"   📊 {len(students)} students across {len(dept_students)} departments")


def apply_formatting(excel_path: str, college_name: str, location: str):
    """Apply professional formatting to all sheets"""
    
    wb = load_workbook(excel_path)
    
    # Color scheme
    colors = {
        'header_blue': '1E3A8A',
        'header_light': '3B82F6',
        'pass_green': 'D1FAE5',
        'fail_red': 'FEE2E2',
        'white': 'FFFFFF',
        'light_gray': 'F3F4F6',
        'dark_text': '1F2937',
    }
    
    # Fonts
    college_font = Font(name='Calibri', size=16, bold=True, color=colors['white'])
    college_fill = PatternFill(start_color=colors['header_blue'], end_color=colors['header_blue'], fill_type='solid')
    
    title_font = Font(name='Calibri', size=12, bold=True, color=colors['dark_text'])
    title_fill = PatternFill(start_color=colors['header_light'], end_color=colors['header_light'], fill_type='solid')
    
    header_font = Font(name='Calibri', size=11, bold=True, color=colors['white'])
    header_fill = PatternFill(start_color=colors['header_blue'], end_color=colors['header_blue'], fill_type='solid')
    header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    pass_font = Font(name='Calibri', size=10, color='065F46', bold=True)
    pass_fill = PatternFill(start_color=colors['pass_green'], end_color=colors['pass_green'], fill_type='solid')
    
    fail_font = Font(name='Calibri', size=10, color='991B1B', bold=True)
    fail_fill = PatternFill(start_color=colors['fail_red'], end_color=colors['fail_red'], fill_type='solid')
    
    cell_alignment = Alignment(horizontal='center', vertical='center')
    
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Get the last column with data
        max_col = ws.max_column
        max_col_letter = get_column_letter(max_col)
        
        # ==================== HEADER ROWS ====================
        
        # Row 1: College Name (merge across all columns)
        ws.merge_cells(f'A1:{max_col_letter}1')
        ws['A1'] = college_name
        ws['A1'].font = college_font
        ws['A1'].fill = college_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 30
        
        # Row 2: Location (merge across all columns)
        ws.merge_cells(f'A2:{max_col_letter}2')
        ws['A2'] = location
        ws['A2'].font = Font(name='Calibri', size=11, italic=True, color=colors['dark_text'])
        ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[2].height = 20
        
        # Row 3: Title (merge across all columns)
        ws.merge_cells(f'A3:{max_col_letter}3')
        ws['A3'] = f"University Examination Results - {sheet_name} Department"
        ws['A3'].font = title_font
        ws['A3'].fill = title_fill
        ws['A3'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 25
        
        # Row 4: Date (merge across all columns)
        ws.merge_cells(f'A4:{max_col_letter}4')
        ws['A4'] = f"Generated on: {datetime.now().strftime('%d %B %Y at %I:%M %p')}"
        ws['A4'].font = Font(name='Calibri', size=9, italic=True, color='6B7280')
        ws['A4'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 18
        
        # Row 5: Blank
        ws.row_dimensions[5].height = 8
        
        # Row 6: Column Headers
        header_row = 6
        for col_idx in range(1, max_col + 1):
            cell = ws.cell(row=header_row, column=col_idx)
            if cell.value:
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border
        
        ws.row_dimensions[header_row].height = 35
        
        # ==================== COLUMN WIDTHS ====================
        
        ws.column_dimensions['A'].width = 18  # Register No
        
        # Subject columns
        for col_idx in range(2, max_col):
            col_letter = get_column_letter(col_idx)
            ws.column_dimensions[col_letter].width = 12
        
        # Status column (last column) - wider
        ws.column_dimensions[max_col_letter].width = 18
        
        # ==================== DATA ROW FORMATTING ====================
        
        for row_idx in range(7, ws.max_row + 1):
            # Check if this is a data row or summary section
            first_cell = ws.cell(row=row_idx, column=1)
            
            # Skip formatting for summary sections
            if first_cell.value and isinstance(first_cell.value, str):
                if "DEPARTMENT SUMMARY" in first_cell.value or "SUBJECT-WISE ANALYSIS" in first_cell.value:
                    continue
            
            # Alternating row colors for data
            if row_idx % 2 == 0:
                row_fill = PatternFill(start_color=colors['light_gray'], end_color=colors['light_gray'], fill_type='solid')
            else:
                row_fill = PatternFill(start_color=colors['white'], end_color=colors['white'], fill_type='solid')
            
            for col_idx in range(1, max_col + 1):
                cell = ws.cell(row=row_idx, column=col_idx)
                
                if cell.value is not None:
                    cell.alignment = cell_alignment
                    cell.border = thin_border
                    
                    # Apply background color if not already colored
                    if not cell.fill or cell.fill.start_color.rgb == '00000000':
                        cell.fill = row_fill
                    
                    # Highlight specific values
                    if isinstance(cell.value, str):
                        value_upper = cell.value.upper()
                        
                        # Pass status
                        if 'PASS' in value_upper and '✓' in cell.value:
                            cell.font = pass_font
                            cell.fill = pass_fill
                        
                        # Fail status
                        elif 'ARREAR' in value_upper and '✗' in cell.value:
                            cell.font = fail_font
                            cell.fill = fail_fill
                        
                        # Failed grades
                        elif cell.value in ['F', 'FE', 'Absent', 'AB', 'Withheld']:
                            cell.font = Font(color='991B1B', bold=True)
                            cell.fill = fail_fill
                        
                        # Passing grades
                        elif cell.value in ['S', 'A+', 'A', 'B+', 'B', 'C+', 'C', 'D', 'P']:
                            cell.font = Font(color='065F46', bold=False)
        
        # Freeze panes
        ws.freeze_panes = 'A7'
    
    wb.save(excel_path)
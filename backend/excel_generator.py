import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side


def get_department_from_regno(regno: str) -> str:
    regno = regno.upper()
    if "EE" in regno:
        return "EEE"
    if "EC" in regno:
        return "ECE"
    if "CS" in regno:
        return "CSE"
    if "ME" in regno:
        return "ME"
    if "CE" in regno:
        return "CE"
    return "OTHER"


def generate_excel_report(students, output_path):

    dept_students = {}

    for student in students:
        regno = student["register_no"]
        dept = get_department_from_regno(regno)

        dept_students.setdefault(dept, []).append(student)

  
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        for dept, dept_list in dept_students.items():

            dept_subjects = set()
            for s in dept_list:
                dept_subjects.update(s["subjects"].keys())
            dept_subjects = sorted(dept_subjects)

            rows = []

            for s in dept_list:
                row = {
                    "Register No": s["register_no"],
                    "Name": ""
                }

                for sub in dept_subjects:
                    row[sub] = s["subjects"].get(sub, "")

                rows.append(row)

            df = pd.DataFrame(rows).sort_values("Register No")
            df.to_excel(writer, sheet_name=dept, index=False)

            ws = writer.sheets[dept]
            last_row = len(df) + 3

            # Overall department summary
            def has_fail(row):
                return any(
                    row[sub] in ["F", "FE", "AB", "Absent", "Withheld"]
                    for sub in dept_subjects
                )

            total_students = len(df)
            failed_students = df.apply(has_fail, axis=1).sum()
            passed_students = total_students - failed_students

            ws[f"A{last_row}"] = "DEPARTMENT SUMMARY"
            ws[f"A{last_row}"].font = Font(bold=True, size=12)

            ws[f"A{last_row + 1}"] = "Total Students"
            ws[f"B{last_row + 1}"] = total_students

            ws[f"A{last_row + 2}"] = "Students with Arrears"
            ws[f"B{last_row + 2}"] = failed_students

            ws[f"A{last_row + 3}"] = "Pass Percentage"
            ws[f"B{last_row + 3}"] = f"{round((passed_students / total_students) * 100, 2)}%"

            # Subject-wise analysis
            subject_analysis_start = last_row + 5
            ws[f"A{subject_analysis_start}"] = "SUBJECT-WISE ANALYSIS"
            ws[f"A{subject_analysis_start}"].font = Font(bold=True, size=12)

            # Headers for subject analysis
            headers_row = subject_analysis_start + 1
            ws[f"A{headers_row}"] = "Subject Code"
            ws[f"B{headers_row}"] = "Total"
            ws[f"C{headers_row}"] = "Passed"
            ws[f"D{headers_row}"] = "Failed"
            ws[f"E{headers_row}"] = "Pass %"
            ws[f"F{headers_row}"] = "Fail %"
            
            # Make headers bold
            for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                ws[f"{col}{headers_row}"].font = Font(bold=True)
                ws[f"{col}{headers_row}"].fill = PatternFill("solid", fgColor="E0E0E0")

            # Calculate statistics for each subject
            fail_grades = ["F", "FE", "AB", "Absent", "Withheld"]
            current_row = headers_row + 1

            for subject in dept_subjects:
                # Get all grades for this subject
                subject_grades = [s["subjects"].get(subject) for s in dept_list if subject in s["subjects"]]
                
                total = len(subject_grades)
                failed = sum(1 for g in subject_grades if g in fail_grades)
                passed = total - failed
                pass_pct = (passed / total * 100) if total > 0 else 0
                fail_pct = (failed / total * 100) if total > 0 else 0

                ws[f"A{current_row}"] = subject
                ws[f"B{current_row}"] = total
                ws[f"C{current_row}"] = passed
                ws[f"D{current_row}"] = failed
                ws[f"E{current_row}"] = round(pass_pct, 2)
                ws[f"F{current_row}"] = round(fail_pct, 2)

                # Highlight subjects with high failure rate (>50%)
                if fail_pct > 50:
                    for col in ['A', 'B', 'C', 'D', 'E', 'F']:
                        ws[f"{col}{current_row}"].fill = PatternFill("solid", fgColor="FFE6E6")
                        ws[f"{col}{current_row}"].font = Font(color="CC0000")

                current_row += 1

    # Apply formatting
    wb = load_workbook(output_path)

    for sheet in wb.sheetnames:
        ws = wb[sheet]

        # Header formatting (first row with student data)
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4F46E5")
            cell.alignment = Alignment(horizontal="center")

        # Column widths
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 15
        ws.column_dimensions["C"].width = 12
        ws.column_dimensions["D"].width = 12
        ws.column_dimensions["E"].width = 12
        ws.column_dimensions["F"].width = 12

        # Highlight failed grades in student data
        for row in ws.iter_rows(min_row=2):
            for cell in row[2:]:
                if cell.value in ["F", "FE", "AB", "Absent", "Withheld"]:
                    cell.font = Font(color="FF0000", bold=True)

    wb.save(output_path)
    print(f"✅ Excel generated with subject-wise analysis per department: {output_path}")
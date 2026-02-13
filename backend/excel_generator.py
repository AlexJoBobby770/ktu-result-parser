import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment


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


def generate_subject_analysis(students):
    """
    Generate subject-wise statistics across all departments
    Returns a list of dicts with subject analysis
    """
    subject_data = {}
    
    # Collect all subject data
    for student in students:
        for subject_code, grade in student["subjects"].items():
            if subject_code not in subject_data:
                subject_data[subject_code] = {
                    "grades": [],
                    "departments": set()
                }
            subject_data[subject_code]["grades"].append(grade)
            subject_data[subject_code]["departments"].add(student["department"])
    
    # Calculate statistics for each subject
    fail_grades = ["F", "FE", "AB", "Absent", "Withheld"]
    analysis = []
    
    for subject_code, data in sorted(subject_data.items()):
        grades = data["grades"]
        total_students = len(grades)
        failed = sum(1 for g in grades if g in fail_grades)
        passed = total_students - failed
        pass_percentage = (passed / total_students * 100) if total_students > 0 else 0
        
        # Grade distribution
        grade_counts = {}
        for grade in grades:
            grade_counts[grade] = grade_counts.get(grade, 0) + 1
        
        analysis.append({
            "Subject Code": subject_code,
            "Total Students": total_students,
            "Passed": passed,
            "Failed": failed,
            "Pass %": round(pass_percentage, 2),
            "Departments": ", ".join(sorted(data["departments"])),
            "Grade Distribution": ", ".join([f"{g}({c})" for g, c in sorted(grade_counts.items())])
        })
    
    return analysis


def generate_excel_report(students, output_path):

    dept_students = {}

    for student in students:
        regno = student["register_no"]
        dept = get_department_from_regno(regno)

        dept_students.setdefault(dept, []).append(student)

  
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        # Generate department-wise sheets
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

            def has_fail(row):
                return any(
                    row[sub] in ["F", "FE", "AB", "Absent", "Withheld"]
                    for sub in dept_subjects
                )

            total_students = len(df)
            failed_students = df.apply(has_fail, axis=1).sum()
            passed_students = total_students - failed_students

            ws[f"A{last_row}"] = "SUMMARY"
            ws[f"A{last_row}"].font = Font(bold=True)

            ws[f"A{last_row + 1}"] = "Total Students"
            ws[f"B{last_row + 1}"] = total_students

            ws[f"A{last_row + 2}"] = "Students with Arrears"
            ws[f"B{last_row + 2}"] = failed_students

            ws[f"A{last_row + 3}"] = "Pass Percentage"
            ws[f"B{last_row + 3}"] = f"{round((passed_students / total_students) * 100, 2)}%"

        # Generate subject-wise analysis sheet
        subject_stats = generate_subject_analysis(students)
        if subject_stats:
            subject_df = pd.DataFrame(subject_stats)
            subject_df.to_excel(writer, sheet_name="Subject Analysis", index=False)

    # Apply formatting
    wb = load_workbook(output_path)

    for sheet in wb.sheetnames:
        ws = wb[sheet]

        # Header formatting
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4F46E5")
            cell.alignment = Alignment(horizontal="center")

        # Column widths
        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 35
        
        # Special formatting for Subject Analysis sheet
        if sheet == "Subject Analysis":
            ws.column_dimensions["A"].width = 15  # Subject Code
            ws.column_dimensions["B"].width = 15  # Total Students
            ws.column_dimensions["C"].width = 12  # Passed
            ws.column_dimensions["D"].width = 12  # Failed
            ws.column_dimensions["E"].width = 12  # Pass %
            ws.column_dimensions["F"].width = 20  # Departments
            ws.column_dimensions["G"].width = 40  # Grade Distribution
            
            # Highlight failed subjects (pass % < 50)
            for row in ws.iter_rows(min_row=2, max_row=ws.max_row):
                pass_percentage_cell = row[4]  # Column E (Pass %)
                try:
                    if isinstance(pass_percentage_cell.value, (int, float)) and pass_percentage_cell.value < 50:
                        for cell in row:
                            cell.fill = PatternFill("solid", fgColor="FFE6E6")
                except:
                    pass

        # Highlight failed grades in department sheets
        for row in ws.iter_rows(min_row=2):
            for cell in row[2:]:
                if cell.value in ["F", "FE", "AB", "Absent", "Withheld"]:
                    cell.font = Font(color="FF0000", bold=True)

    wb.save(output_path)
    print(f"✅ Excel generated with subject analysis: {output_path}")
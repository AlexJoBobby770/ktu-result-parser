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


def generate_excel_report(students, output_path):

    # ---------- STEP 1: GROUP STUDENTS BY DEPARTMENT ----------
    dept_students = {}

    for student in students:
        regno = student["register_no"]
        dept = get_department_from_regno(regno)

        dept_students.setdefault(dept, []).append(student)

    # ---------- STEP 2: WRITE EXCEL ----------
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

        for dept, dept_list in dept_students.items():

            # ✅ Collect ONLY subjects of THIS department
            dept_subjects = set()
            for s in dept_list:
                dept_subjects.update(s["subjects"].keys())
            dept_subjects = sorted(dept_subjects)

            # ✅ Build rows (one row = one student)
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

            # ---------- SUMMARY ----------
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

    # ---------- STYLING ----------
    wb = load_workbook(output_path)

    for sheet in wb.sheetnames:
        ws = wb[sheet]

        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill("solid", fgColor="4F46E5")
            cell.alignment = Alignment(horizontal="center")

        ws.column_dimensions["A"].width = 18
        ws.column_dimensions["B"].width = 35

        for row in ws.iter_rows(min_row=2):
            for cell in row[2:]:
                if cell.value in ["F", "FE", "AB", "Absent", "Withheld"]:
                    cell.font = Font(color="FF0000", bold=True)

    wb.save(output_path)
    print(f"✅ Excel generated correctly (dept-specific subjects): {output_path}")

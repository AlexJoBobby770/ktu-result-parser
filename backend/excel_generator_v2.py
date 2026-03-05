# backend/excel_generator_v2.py
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from typing import List
from models import MergedRecord
from datetime import datetime


def generate_merged_excel(merged_records: List[MergedRecord], output_path: str):
    from collections import defaultdict
    from models import compute_sgpa

    COLLEGE_NAME = "ALBERTIAN INSTITUTE OF SCIENCE AND TECHNOLOGY (AISAT)"
    COLLEGE_LOCATION = "Kalamassery, Kerala"
    FAIL_GRADES = {'F', 'FE', 'Absent', 'AB'}

    df = pd.DataFrame([r.to_dict() for r in merged_records])
    df = df.sort_values(['Register No', 'Subject Code'])
    departments = df['Department'].unique()

    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:

        # ── One sheet per department ──────────────────────────────
        for dept in departments:
            dept_df = df[df['Department'] == dept].copy()
            students = sorted(dept_df['Register No'].unique())
            subjects = sorted(dept_df['Subject Code'].unique())

            dept_rows = []
            for regno in students:
                student_data = dept_df[dept_df['Register No'] == regno].iloc[0]
                row = {
                    'Register No': regno,
                    'Student Name': student_data['Student Name']
                }

                grade_dict = {}
                internal_dict = {}

                for code in subjects:
                    rec = dept_df[
                        (dept_df['Register No'] == regno) &
                        (dept_df['Subject Code'] == code)
                    ]
                    if not rec.empty:
                        r = rec.iloc[0]

                        # detect skipped elective
                        if r['Internal Mark'] == 0 and r['Grade'] in ['Absent','AB','F','FE']:
                            row[f"{r['Subject Name']} ({code}) - Internal"] = "—"
                            row[f"{r['Subject Name']} ({code}) - Grade"] = "NOT ELECTED"
                        else:
                            row[f"{r['Subject Name']} ({code}) - Internal"] = r['Internal Mark']
                            row[f"{r['Subject Name']} ({code}) - Grade"] = r['Grade']
                            grade_dict[code] = r['Grade']
                            internal_dict[code] = r['Internal Mark']
                    else:
                        row[f"{code} - Internal"] = '—'
                        row[f"{code} - Grade"]    = '—'

                internal_dict = {r['Subject Code']: r['Internal Mark']
                 for _, r in dept_df[dept_df['Register No'] == regno].iterrows()}

                arrears = [
                    c for c, g in grade_dict.items()
                    if g in FAIL_GRADES and internal_dict.get(c, 0) != 0
                ]


                row['SGPA'] = compute_sgpa(grade_dict, internal_dict)
                row['Arrears'] = len(arrears)
                row['Status']  = '✓ PASS' if not arrears else f'✗ {len(arrears)} ARREAR(S)'
                dept_rows.append(row)

            pd.DataFrame(dept_rows).to_excel(writer, sheet_name=dept, index=False, startrow=5)

        # ── Subject Analysis only ─────────────────────────────────
        subject_stats = []
        for code in sorted(df['Subject Code'].unique()):
            sd = df[df['Subject Code'] == code]
            total   = len(sd)
            passed  = len(sd[~sd['Grade'].isin(FAIL_GRADES)])
            failed  = total - passed
            pass_pct = round(passed / total * 100, 2) if total else 0

            subject_stats.append({
                'Subject Code': code,
                'Subject Name': sd['Subject Name'].iloc[0],
                'Faculty':      sd['Faculty Name'].iloc[0],
                'Total':        total,
                'Passed':       passed,
                'Failed':       failed,
                'Pass %':       pass_pct,
                'Avg Internal': round(sd['Internal Mark'].mean(), 2),
                'Performance':  'Excellent' if pass_pct >= 90 else
                                'Good'      if pass_pct >= 75 else
                                'Average'   if pass_pct >= 60 else
                                'Needs Improvement'
            })

        pd.DataFrame(subject_stats).to_excel(
            writer, sheet_name='Subject Analysis', index=False, startrow=5)

    apply_gorgeous_formatting(output_path, COLLEGE_NAME, COLLEGE_LOCATION,
                              "Result Analysis Report", {
                                  'header_blue': '1E3A8A', 'header_light': '3B82F6',
                                  'pass_green': 'D1FAE5', 'fail_red': 'FEE2E2',
                                  'white': 'FFFFFF', 'light_gray': 'F3F4F6', 'dark_text': '1F2937',
                              }, df)

    print(f"✅ Excel generated: {output_path}")
    print(f"   📊 {len(merged_records)} records, {df['Register No'].nunique()} students")


def apply_gorgeous_formatting(excel_path: str, college_name: str, location: str, 
                              title: str, colors: dict, df: pd.DataFrame):
    """Apply professional formatting to all sheets"""
    
    wb = load_workbook(excel_path)
    
    # Styles
    college_font = Font(name='Calibri', size=16, bold=True, color=colors['white'])
    college_fill = PatternFill(start_color=colors['header_blue'], end_color=colors['header_blue'], fill_type='solid')
    
    title_font = Font(name='Calibri', size=12, bold=True, color=colors['dark_text'])
    title_fill = PatternFill(start_color=colors['header_light'], end_color=colors['header_light'], fill_type='solid')
    
    column_header_font = Font(name='Calibri', size=11, bold=True, color=colors['white'])
    column_header_fill = PatternFill(start_color=colors['header_blue'], end_color=colors['header_blue'], fill_type='solid')
    column_header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
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
        
        # College Header
        ws.merge_cells('A1:L1')
        ws['A1'] = college_name
        ws['A1'].font = college_font
        ws['A1'].fill = college_fill
        ws['A1'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[1].height = 25
        
        ws.merge_cells('A2:L2')
        ws['A2'] = location
        ws['A2'].font = Font(name='Calibri', size=10, italic=True, color=colors['dark_text'])
        ws['A2'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[2].height = 18
        
        ws.merge_cells('A3:L3')
        ws['A3'] = f"{title} - {sheet_name}"
        ws['A3'].font = title_font
        ws['A3'].fill = title_fill
        ws['A3'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[3].height = 22
        
        ws.merge_cells('A4:L4')
        ws['A4'] = f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}"
        ws['A4'].font = Font(name='Calibri', size=9, italic=True, color='6B7280')
        ws['A4'].alignment = Alignment(horizontal='center', vertical='center')
        ws.row_dimensions[4].height = 16
        
        ws.row_dimensions[5].height = 8
        
        # Column Headers
        header_row = 6
        for cell in ws[header_row]:
            if cell.value:
                cell.font = column_header_font
                cell.fill = column_header_fill
                cell.alignment = column_header_alignment
                cell.border = thin_border
        
        ws.row_dimensions[header_row].height = 40
        
        # Set fixed column widths (safer than auto-calculation)
        column_widths = {
            'A': 18, 'B': 25, 'C': 15, 'D': 30, 'E': 25, 'F': 12,
            'G': 12, 'H': 12, 'I': 10, 'J': 12, 'K': 15, 'L': 15
        }
        
        for col_letter, width in column_widths.items():
            ws.column_dimensions[col_letter].width = width
        
        # Set remaining columns to default
        for col_idx in range(13, 30):  # Up to column AD
            ws.column_dimensions[get_column_letter(col_idx)].width = 15
        
        # Data rows
        for row_idx, row in enumerate(ws.iter_rows(min_row=7), start=7):
            if row_idx % 2 == 0:
                row_fill = PatternFill(start_color=colors['light_gray'], end_color=colors['light_gray'], fill_type='solid')
            else:
                row_fill = PatternFill(start_color=colors['white'], end_color=colors['white'], fill_type='solid')
            
            for cell in row:
                if cell.value:
                    cell.alignment = cell_alignment
                    cell.border = thin_border
                    
                    if not cell.fill or cell.fill.start_color.rgb == '00000000':
                        cell.fill = row_fill
                    
                    if isinstance(cell.value, str):
                        if 'PASS' in cell.value.upper() or '✓' in cell.value:
                            cell.font = pass_font
                            cell.fill = pass_fill
                        elif 'FAIL' in cell.value.upper() or 'ARREAR' in cell.value.upper() or '✗' in cell.value:
                            cell.font = fail_font
                            cell.fill = fail_fill
                        elif 'EXCELLENT' in cell.value.upper():
                            cell.fill = PatternFill(start_color='D1FAE5', end_color='D1FAE5', fill_type='solid')
                            cell.font = Font(bold=True, color='065F46')
                        elif 'GOOD' in cell.value.upper():
                            cell.fill = PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid')
                            cell.font = Font(bold=True, color='1E40AF')
                        elif 'AVERAGE' in cell.value.upper():
                            cell.fill = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
                            cell.font = Font(bold=True, color='92400E')
                        elif 'NEEDS IMPROVEMENT' in cell.value.upper():
                            cell.fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                            cell.font = Font(bold=True, color='991B1B')
        
        ws.freeze_panes = 'A7'
    
    wb.save(excel_path)

if __name__ == "__main__":
    print("Excel Generator V2 - Beautiful Edition with Charts")
    print("Generates professional Excel reports with 6 interactive visualizations")
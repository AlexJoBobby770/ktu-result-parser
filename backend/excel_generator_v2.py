# backend/excel_generator_v2.py
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, PieChart, Reference
from typing import List
from models import MergedRecord
from datetime import datetime


def generate_merged_excel(merged_records: List[MergedRecord], output_path: str):
    """
    Generate a BEAUTIFUL, professional Excel report with:
    - College branding and header
    - Subject names (not just codes)
    - Color-coded results
    - Multiple analysis sheets
    - Charts and visualizations
    """
    
    # College Information
    COLLEGE_NAME = "ALBERTIAN INSTITUTE OF SCIENCE AND TECHNOLOGY (AISAT)"
    COLLEGE_LOCATION = "Kalamassery, Kerala"
    REPORT_TITLE = "Comprehensive Result Analysis Report"
    
    # Convert to DataFrame
    df = pd.DataFrame([r.to_dict() for r in merged_records])
    df = df.sort_values(['Register No', 'Subject Code'])
    
    # Color Palette
    COLORS = {
        'header_blue': '1E3A8A',      # Dark blue
        'header_light': '3B82F6',     # Light blue
        'pass_green': 'D1FAE5',       # Light green
        'fail_red': 'FEE2E2',         # Light red
        'excellent': '10B981',        # Green
        'good': '3B82F6',            # Blue
        'average': 'F59E0B',         # Amber
        'poor': 'EF4444',            # Red
        'white': 'FFFFFF',
        'light_gray': 'F3F4F6',
        'dark_text': '1F2937',
    }
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ═══════════════════════════════════════════════════════════
        # SHEET 1: MASTER DATA (with full subject names)
        # ═══════════════════════════════════════════════════════════
        
        master_df = df[[
            'Register No', 'Student Name', 
            'Subject Code', 'Subject Name', 'Faculty Name',
            'Internal Mark', 'External Mark', 'Total Mark',
            'Grade', 'Result', 'Department'
        ]].copy()
        
        master_df.to_excel(writer, sheet_name='Master Data', index=False, startrow=5)
        
        # ═══════════════════════════════════════════════════════════
        # SHEET 2-N: DEPARTMENT SHEETS (Beautiful & Organized)
        # ═══════════════════════════════════════════════════════════
        
        departments = df['Department'].unique()
        
        for dept in departments:
            dept_df = df[df['Department'] == dept].copy()
            
            # Create a pivot-like view: Student info + subjects as columns
            students = dept_df['Register No'].unique()
            subjects = dept_df['Subject Code'].unique()
            
            # Build department sheet
            dept_rows = []
            for student_reg in students:
                student_data = dept_df[dept_df['Register No'] == student_reg].iloc[0]
                row = {
                    'Register No': student_reg,
                    'Student Name': student_data['Student Name']
                }
                
                # Add subject columns with full names
                for subj_code in sorted(subjects):
                    subj_records = dept_df[
                        (dept_df['Register No'] == student_reg) & 
                        (dept_df['Subject Code'] == subj_code)
                    ]
                    
                    if not subj_records.empty:
                        record = subj_records.iloc[0]
                        # Use subject name as column header
                        col_name = f"{record['Subject Name']}\n({subj_code})"
                        row[col_name] = f"{record['Total Mark']}\n({record['Grade']})"
                    else:
                        col_name = f"{subj_code}"
                        row[col_name] = "—"
                
                # Add summary
                student_records = dept_df[dept_df['Register No'] == student_reg]
                total_subjects = len(student_records)
                failed_subjects = len(student_records[student_records['Result'] == 'Fail'])
                
                row['Total Subjects'] = total_subjects
                row['Failed'] = failed_subjects
                row['Status'] = '✓ PASS' if failed_subjects == 0 else f'✗ {failed_subjects} ARREAR(S)'
                
                dept_rows.append(row)
            
            dept_sheet_df = pd.DataFrame(dept_rows)
            dept_sheet_df.to_excel(writer, sheet_name=dept, index=False, startrow=5)
        
        # ═══════════════════════════════════════════════════════════
        # SHEET: SUBJECT ANALYSIS (Detailed Statistics)
        # ═══════════════════════════════════════════════════════════
        
        subject_stats = []
        
        for subject_code in sorted(df['Subject Code'].unique()):
            subject_data = df[df['Subject Code'] == subject_code]
            
            total_students = len(subject_data)
            passed = len(subject_data[subject_data['Result'] == 'Pass'])
            failed = total_students - passed
            pass_pct = (passed / total_students * 100) if total_students > 0 else 0
            
            avg_internal = subject_data['Internal Mark'].mean()
            avg_external = subject_data['External Mark'].mean()
            avg_total = subject_data['Total Mark'].mean()
            
            max_total = subject_data['Total Mark'].max()
            min_total = subject_data['Total Mark'].min()
            
            # Get subject name and faculty
            subject_name = subject_data['Subject Name'].iloc[0]
            faculty_name = subject_data['Faculty Name'].iloc[0]
            
            # Performance category
            if pass_pct >= 90:
                performance = "Excellent"
            elif pass_pct >= 75:
                performance = "Good"
            elif pass_pct >= 60:
                performance = "Average"
            else:
                performance = "Needs Improvement"
            
            subject_stats.append({
                'Subject Code': subject_code,
                'Subject Name': subject_name,
                'Faculty': faculty_name,
                'Total Students': total_students,
                'Passed': passed,
                'Failed': failed,
                'Pass %': round(pass_pct, 2),
                'Avg Internal': round(avg_internal, 2),
                'Avg External': round(avg_external, 2),
                'Avg Total': round(avg_total, 2),
                'Highest': max_total,
                'Lowest': min_total,
                'Performance': performance
            })
        
        subject_stats_df = pd.DataFrame(subject_stats)
        subject_stats_df.to_excel(writer, sheet_name='Subject Analysis', index=False, startrow=5)
        
        # ═══════════════════════════════════════════════════════════
        # SHEET: FACULTY ANALYSIS (Performance by Faculty)
        # ═══════════════════════════════════════════════════════════
        
        faculty_stats = []
        
        for faculty in sorted(df['Faculty Name'].unique()):
            if faculty == "N/A":
                continue
                
            faculty_data = df[df['Faculty Name'] == faculty]
            
            total_students = len(faculty_data)
            passed = len(faculty_data[faculty_data['Result'] == 'Pass'])
            pass_pct = (passed / total_students * 100) if total_students > 0 else 0
            
            avg_internal = faculty_data['Internal Mark'].mean()
            avg_external = faculty_data['External Mark'].mean()
            avg_total = faculty_data['Total Mark'].mean()
            
            subjects_taught = faculty_data['Subject Name'].unique()
            subjects_list = ', '.join(subjects_taught)
            
            faculty_stats.append({
                'Faculty Name': faculty,
                'Subjects': subjects_list,
                'Total Records': total_students,
                'Passed': passed,
                'Failed': total_students - passed,
                'Pass %': round(pass_pct, 2),
                'Avg Internal Given': round(avg_internal, 2),
                'Avg External Score': round(avg_external, 2),
                'Avg Total': round(avg_total, 2)
            })
        
        faculty_stats_df = pd.DataFrame(faculty_stats)
        faculty_stats_df.to_excel(writer, sheet_name='Faculty Analysis', index=False, startrow=5)
        
        # ═══════════════════════════════════════════════════════════
        # SHEET: OVERALL SUMMARY (Executive Dashboard)
        # ═══════════════════════════════════════════════════════════
        
        total_records = len(df)
        total_students = df['Register No'].nunique()
        total_passed = len(df[df['Result'] == 'Pass'])
        overall_pass_pct = (total_passed / total_records * 100) if total_records > 0 else 0
        
        # Grade distribution
        grade_counts = df['Grade'].value_counts().to_dict()
        
        summary_data = {
            'Metric': [
                'Total Records',
                'Unique Students',
                'Total Subjects',
                'Departments',
                '',  # Spacer
                'Records Passed',
                'Records Failed',
                'Overall Pass %',
                '',  # Spacer
                'Average Internal Mark',
                'Average External Mark',
                'Average Total Mark',
                '',  # Spacer
                'Highest Total Mark',
                'Lowest Total Mark',
            ],
            'Value': [
                total_records,
                total_students,
                df['Subject Code'].nunique(),
                len(departments),
                '',
                total_passed,
                total_records - total_passed,
                f"{round(overall_pass_pct, 2)}%",
                '',
                round(df['Internal Mark'].mean(), 2),
                round(df['External Mark'].mean(), 2),
                round(df['Total Mark'].mean(), 2),
                '',
                df['Total Mark'].max(),
                df['Total Mark'].min(),
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Overall Summary', index=False, startrow=8)
        
        # ═══════════════════════════════════════════════════════════
        # SHEET: STUDENT WISE SUMMARY (Individual Performance)
        # ═══════════════════════════════════════════════════════════
        
        student_summary = []
        
        for student_reg in sorted(df['Register No'].unique()):
            student_data = df[df['Register No'] == student_reg]
            student_name = student_data['Student Name'].iloc[0]
            department = student_data['Department'].iloc[0]
            
            total_subjects = len(student_data)
            passed_subjects = len(student_data[student_data['Result'] == 'Pass'])
            failed_subjects = total_subjects - passed_subjects
            
            avg_internal = student_data['Internal Mark'].mean()
            avg_external = student_data['External Mark'].mean()
            avg_total = student_data['Total Mark'].mean()
            
            status = "✓ ALL CLEAR" if failed_subjects == 0 else f"✗ {failed_subjects} ARREAR(S)"
            
            student_summary.append({
                'Register No': student_reg,
                'Student Name': student_name,
                'Department': department,
                'Total Subjects': total_subjects,
                'Passed': passed_subjects,
                'Failed': failed_subjects,
                'Avg Internal': round(avg_internal, 2),
                'Avg External': round(avg_external, 2),
                'Avg Total': round(avg_total, 2),
                'Status': status
            })
        
        student_summary_df = pd.DataFrame(student_summary)
        student_summary_df.to_excel(writer, sheet_name='Student Summary', index=False, startrow=5)
    
    # ═══════════════════════════════════════════════════════════
    # APPLY BEAUTIFUL FORMATTING
    # ═══════════════════════════════════════════════════════════
    
    apply_gorgeous_formatting(
        output_path, 
        COLLEGE_NAME, 
        COLLEGE_LOCATION,
        REPORT_TITLE,
        COLORS,
        df
    )
    
    print(f"✅ Beautiful Excel generated: {output_path}")
    print(f"   📊 {len(merged_records)} records")
    print(f"   👥 {total_students} students")
    print(f"   🏛️ {len(departments)} departments")


def apply_gorgeous_formatting(excel_path: str, college_name: str, location: str, 
                              title: str, colors: dict, df: pd.DataFrame):
    """Apply professional, eye-catching formatting to all sheets"""
    
    wb = load_workbook(excel_path)
    
    # ═══════════════════════════════════════════════════════════
    # DEFINE REUSABLE STYLES
    # ═══════════════════════════════════════════════════════════
    
    # Header styles
    college_font = Font(name='Calibri', size=16, bold=True, color=colors['white'])
    college_fill = PatternFill(start_color=colors['header_blue'], 
                               end_color=colors['header_blue'], fill_type='solid')
    
    title_font = Font(name='Calibri', size=12, bold=True, color=colors['dark_text'])
    title_fill = PatternFill(start_color=colors['header_light'], 
                            end_color=colors['header_light'], fill_type='solid')
    
    column_header_font = Font(name='Calibri', size=11, bold=True, color=colors['white'])
    column_header_fill = PatternFill(start_color=colors['header_blue'], 
                                     end_color=colors['header_blue'], fill_type='solid')
    column_header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
    
    # Data styles
    pass_font = Font(name='Calibri', size=10, color='065F46', bold=True)
    pass_fill = PatternFill(start_color=colors['pass_green'], 
                           end_color=colors['pass_green'], fill_type='solid')
    
    fail_font = Font(name='Calibri', size=10, color='991B1B', bold=True)
    fail_fill = PatternFill(start_color=colors['fail_red'], 
                           end_color=colors['fail_red'], fill_type='solid')
    
    cell_alignment = Alignment(horizontal='center', vertical='center')
    
    thin_border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )
    
    # ═══════════════════════════════════════════════════════════
    # FORMAT EACH SHEET
    # ═══════════════════════════════════════════════════════════
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # ─────────────────────────────────────────────────────────
        # ADD COLLEGE HEADER (Rows 1-3)
        # ─────────────────────────────────────────────────────────
        
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
        
        # Empty row 5 for spacing
        ws.row_dimensions[5].height = 8
        
        # ─────────────────────────────────────────────────────────
        # FORMAT COLUMN HEADERS (Row 6)
        # ─────────────────────────────────────────────────────────
        
        header_row = 6
        for cell in ws[header_row]:
            if cell.value:
                cell.font = column_header_font
                cell.fill = column_header_fill
                cell.alignment = column_header_alignment
                cell.border = thin_border
        
        ws.row_dimensions[header_row].height = 40
        
        # ─────────────────────────────────────────────────────────
        # AUTO-ADJUST COLUMN WIDTHS
        # ─────────────────────────────────────────────────────────
        
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            # Set width with min and max limits
            adjusted_width = min(max(max_length + 3, 12), 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # ─────────────────────────────────────────────────────────
        # FORMAT DATA ROWS (Starting from row 7)
        # ─────────────────────────────────────────────────────────
        
        for row_idx, row in enumerate(ws.iter_rows(min_row=7), start=7):
            # Alternate row colors for readability
            if row_idx % 2 == 0:
                row_fill = PatternFill(start_color=colors['light_gray'], 
                                      end_color=colors['light_gray'], fill_type='solid')
            else:
                row_fill = PatternFill(start_color=colors['white'], 
                                      end_color=colors['white'], fill_type='solid')
            
            for cell in row:
                if cell.value:
                    cell.alignment = cell_alignment
                    cell.border = thin_border
                    
                    # Apply alternating row color only if not already colored
                    if not cell.fill or cell.fill.start_color.rgb == '00000000':
                        cell.fill = row_fill
                    
                    # Highlight Pass/Fail
                    if isinstance(cell.value, str):
                        if 'PASS' in cell.value.upper() or '✓' in cell.value:
                            cell.font = pass_font
                            cell.fill = pass_fill
                        elif 'FAIL' in cell.value.upper() or 'ARREAR' in cell.value.upper() or '✗' in cell.value:
                            cell.font = fail_font
                            cell.fill = fail_fill
                        
                        # Highlight performance categories
                        elif 'EXCELLENT' in cell.value.upper():
                            cell.fill = PatternFill(start_color='D1FAE5', end_color='D1FAE5', fill_type='solid')
                            cell.font = Font(bold=True, color='065F46')
                        elif 'GOOD' in cell.value.upper():
                            cell.fill = PatternFill(start_color='DBEAFE', end_color='DBEAFE', fill_type='solid')
                            cell.font = Font(bold=True, color='1E40AF')
                        elif 'AVERAGE' in cell.value.upper():
                            cell.fill = PatternFill(start_color='FEF3C7', end_color='FEF3C7', fill_type='solid')
                            cell.font = Font(bold=True, color='92400E')
                        elif 'NEEDS IMPROVEMENT' in cell.value.upper() or 'POOR' in cell.value.upper():
                            cell.fill = PatternFill(start_color='FEE2E2', end_color='FEE2E2', fill_type='solid')
                            cell.font = Font(bold=True, color='991B1B')
        
        # ─────────────────────────────────────────────────────────
        # FREEZE TOP ROWS
        # ─────────────────────────────────────────────────────────
        
        ws.freeze_panes = 'A7'  # Freeze header rows
        
        # ─────────────────────────────────────────────────────────
        # ADD CHARTS FOR ANALYSIS SHEETS
        # ─────────────────────────────────────────────────────────
        
        if sheet_name == 'Subject Analysis' and len(ws['A']) > 7:
            # Create bar chart for pass percentages
            chart = BarChart()
            chart.title = "Subject-wise Pass Percentage"
            chart.y_axis.title = "Pass Percentage (%)"
            chart.x_axis.title = "Subjects"
            
            # Data for chart (assuming Pass % is in column G)
            data = Reference(ws, min_col=7, min_row=6, max_row=ws.max_row)
            cats = Reference(ws, min_col=1, min_row=7, max_row=ws.max_row)
            
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(cats)
            chart.height = 12
            chart.width = 20
            
            ws.add_chart(chart, f"A{ws.max_row + 3}")
    
    wb.save(excel_path)
    print("✨ Gorgeous formatting applied!")


# ═══════════════════════════════════════════════════════════
# TEST FUNCTION
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("Excel Generator V2 - Beautiful Edition")
    print("This module generates professional, color-coded Excel reports")
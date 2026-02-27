# backend/excel_generator_v2.py
import pandas as pd
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows
from typing import List
from models import MergedRecord


def generate_merged_excel(merged_records: List[MergedRecord], output_path: str):
    """
    Generate comprehensive Excel report with merged internal + external data
    
    Sheets:
    1. Master Data - All student records with internal + external marks
    2. Department Sheets - Separated by department
    3. Subject Analysis - Subject-wise statistics
    4. Faculty Analysis - Faculty-wise performance
    """
    
    # Convert to DataFrame
    df = pd.DataFrame([r.to_dict() for r in merged_records])
    
    # Sort by register number and subject
    df = df.sort_values(['Register No', 'Subject Code'])
    
    with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
        
        # ===== SHEET 1: MASTER DATA =====
        df.to_excel(writer, sheet_name='Master Data', index=False)
        
        # ===== SHEET 2-N: DEPARTMENT SHEETS =====
        departments = df['Department'].unique()
        
        for dept in departments:
            dept_df = df[df['Department'] == dept].copy()
            dept_df = dept_df.drop('Department', axis=1)  # Remove redundant column
            dept_df.to_excel(writer, sheet_name=dept, index=False)
        
        # ===== SUBJECT ANALYSIS SHEET =====
        subject_stats = []
        
        for subject_code in df['Subject Code'].unique():
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
                'Max Total': max_total,
                'Min Total': min_total
            })
        
        subject_stats_df = pd.DataFrame(subject_stats)
        subject_stats_df.to_excel(writer, sheet_name='Subject Analysis', index=False)
        
        # ===== FACULTY ANALYSIS SHEET =====
        faculty_stats = []
        
        for faculty in df['Faculty Name'].unique():
            faculty_data = df[df['Faculty Name'] == faculty]
            
            total_students = len(faculty_data)
            passed = len(faculty_data[faculty_data['Result'] == 'Pass'])
            pass_pct = (passed / total_students * 100) if total_students > 0 else 0
            
            avg_internal = faculty_data['Internal Mark'].mean()
            avg_total = faculty_data['Total Mark'].mean()
            
            subjects_taught = faculty_data['Subject Code'].nunique()
            
            faculty_stats.append({
                'Faculty Name': faculty,
                'Subjects Taught': subjects_taught,
                'Total Students': total_students,
                'Passed': passed,
                'Pass %': round(pass_pct, 2),
                'Avg Internal Given': round(avg_internal, 2),
                'Avg Total Score': round(avg_total, 2)
            })
        
        faculty_stats_df = pd.DataFrame(faculty_stats)
        faculty_stats_df.to_excel(writer, sheet_name='Faculty Analysis', index=False)
        
        # ===== OVERALL SUMMARY SHEET =====
        total_records = len(df)
        total_students = df['Register No'].nunique()
        total_passed = len(df[df['Result'] == 'Pass'])
        overall_pass_pct = (total_passed / total_records * 100) if total_records > 0 else 0
        
        summary_data = {
            'Metric': [
                'Total Records',
                'Unique Students',
                'Total Subjects',
                'Records Passed',
                'Records Failed',
                'Overall Pass %',
                'Average Internal Mark',
                'Average External Mark',
                'Average Total Mark'
            ],
            'Value': [
                total_records,
                total_students,
                df['Subject Code'].nunique(),
                total_passed,
                total_records - total_passed,
                f"{round(overall_pass_pct, 2)}%",
                round(df['Internal Mark'].mean(), 2),
                round(df['External Mark'].mean(), 2),
                round(df['Total Mark'].mean(), 2)
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        summary_df.to_excel(writer, sheet_name='Overall Summary', index=False)
    
    # ===== APPLY FORMATTING =====
    apply_excel_formatting(output_path)
    
    print(f"✅ Excel generated: {output_path}")
    print(f"   - {len(merged_records)} records")
    print(f"   - {total_students} students")
    print(f"   - {len(departments)} departments")


def apply_excel_formatting(excel_path: str):
    """Apply professional formatting to all sheets"""
    
    wb = load_workbook(excel_path)
    
    # Define styles
    header_font = Font(bold=True, color="FFFFFF", size=11)
    header_fill = PatternFill(start_color="4F46E5", end_color="4F46E5", fill_type="solid")
    header_alignment = Alignment(horizontal="center", vertical="center")
    
    fail_font = Font(color="DC2626", bold=True)
    fail_fill = PatternFill(start_color="FEE2E2", end_color="FEE2E2", fill_type="solid")
    
    pass_font = Font(color="059669", bold=True)
    pass_fill = PatternFill(start_color="D1FAE5", end_color="D1FAE5", fill_type="solid")
    
    border = Border(
        left=Side(style='thin', color='E5E7EB'),
        right=Side(style='thin', color='E5E7EB'),
        top=Side(style='thin', color='E5E7EB'),
        bottom=Side(style='thin', color='E5E7EB')
    )
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Format headers
        for cell in ws[1]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = header_alignment
            cell.border = border
        
        # Auto-adjust column widths
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
        
        # Apply borders to all cells
        for row in ws.iter_rows(min_row=1):
            for cell in row:
                cell.border = border
        
        # Highlight Pass/Fail in Result column
        if sheet_name in ['Master Data'] + list(wb.sheetnames):
            for row in ws.iter_rows(min_row=2):
                for cell in row:
                    if cell.column_letter == 'K':  # Result column (adjust if needed)
                        if cell.value == 'Fail':
                            cell.font = fail_font
                            cell.fill = fail_fill
                        elif cell.value == 'Pass':
                            cell.font = pass_font
                            cell.fill = pass_fill
        
        # Freeze top row
        ws.freeze_panes = 'A2'
    
    wb.save(excel_path)
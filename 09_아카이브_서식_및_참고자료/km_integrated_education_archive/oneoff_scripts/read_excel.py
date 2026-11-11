import openpyxl
import os
import sys

excel_path = r"d:\행정\한의학 교육과 의료 통합\한의학 교육 분석.xlsx"
wb = openpyxl.load_workbook(excel_path)
print("Sheets in '한의학 교육 분석.xlsx':", wb.sheetnames)

for s in wb.sheetnames:
    ws = wb[s]
    print(f"\n================ Sheet: {s} ({ws.max_row} rows, {ws.max_column} cols) ================")
    for row in ws.iter_rows(values_only=True):
        if any(row):
            print([str(c) if c is not None else "" for c in row])

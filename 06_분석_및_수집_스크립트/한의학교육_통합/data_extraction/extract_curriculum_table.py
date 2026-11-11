import fitz
import re
import csv
import json

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

# Extract all text from pages 17 to 26 (0-indexed 16 to 25)
curriculum_text = ""
for p in range(16, 26):
    curriculum_text += f"\n--- Page {p+1} ---\n" + doc[p].get_text("text")

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\curriculum_table_raw.txt", "w", encoding="utf-8") as f:
    f.write(curriculum_text)

print("Saved raw curriculum table text.")

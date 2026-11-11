import fitz # PyMuPDF
import json
import csv

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

# Extract pages 1 to 35
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\curriculum_summary_pages_1_35.txt", "w", encoding="utf-8") as f:
    for page_num in range(min(35, len(doc))):
        f.write(f"\n==================== PAGE {page_num + 1} ====================\n")
        f.write(doc[page_num].get_text("text"))

print("Extracted pages 1-35.")

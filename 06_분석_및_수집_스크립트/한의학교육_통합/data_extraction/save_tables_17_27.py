import fitz
import json
import pandas as pd

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

# Let's inspect pages 17 to 27 in detail
pages_info = []

for pno in range(16, 27):
    page = doc[pno]
    text = page.get_text("text")
    pages_info.append({"page": pno + 1, "text": text})

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\curriculum_table_pages_17_27.txt", "w", encoding="utf-8") as f:
    for p in pages_info:
        f.write(f"\n==================== PAGE {p['page']} ====================\n")
        f.write(p['text'])

print("Saved pages 17-27.")

import fitz
import json

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

all_rows = []
for pno in range(16, 26):
    page = doc[pno]
    tab_finder = page.find_tables()
    for tab in tab_finder:
        df = tab.extract()
        for row in df:
            all_rows.append({"page": pno + 1, "row": row})

print(f"Total extracted rows: {len(all_rows)}")
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\extracted_tables.json", "w", encoding="utf-8") as f:
    json.dump(all_rows, f, ensure_ascii=False, indent=2)

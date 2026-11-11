import fitz
import json

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\kascom_evaluation_standards.pdf")
print("Total Pages:", len(doc))
print("TOC:", doc.get_toc())

full_text = ""
for i in range(len(doc)):
    page_text = doc[i].get_text("text")
    full_text += f"\n\n==================== PAGE {i+1} ====================\n" + page_text

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters.")
print("\n--- First 1500 chars ---")
print(full_text[:1500])

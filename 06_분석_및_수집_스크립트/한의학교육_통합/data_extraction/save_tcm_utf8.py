import fitz
import sys

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\세계중의본과교육표준(정체판).pdf")

# Let's inspect pages and write to a file in UTF-8
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\tcm_pages_utf8.txt", "w", encoding="utf-8") as f:
    for i in range(len(doc)):
        f.write(f"\n\n==================== PAGE {i+1} ====================\n")
        f.write(doc[i].get_text("text"))

print("Saved tcm_pages_utf8.txt.")

import fitz

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\세계중의본과교육표준(정체판).pdf")
print("Total Pages:", len(doc))

full_text = ""
for i, page in enumerate(doc):
    text = page.get_text("text")
    full_text += f"\n==================== PAGE {i+1} ====================\n" + text

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\세계중의본과교육표준_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted {len(full_text)} characters. First 2000 chars:")
print(full_text[:2000])

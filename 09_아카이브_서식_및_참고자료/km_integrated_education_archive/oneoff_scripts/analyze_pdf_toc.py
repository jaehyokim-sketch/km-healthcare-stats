import fitz # PyMuPDF
import json

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\curriculum.pdf")
print("Total Pages:", len(doc))
toc = doc.get_toc()
print(f"TOC items ({len(toc)}):")
for item in toc[:50]:
    print(item)

# Extract first 5 pages text
print("\n--- First 5 pages sample ---")
for i in range(min(5, len(doc))):
    print(f"=== Page {i+1} ===")
    print(doc[i].get_text("text")[:1000])

# Search for curriculum tables or key terms
keywords = ["교육과정", "이수", "편성표", "교과목", "학점", "시수", "예과", "본과", "임상실습"]
found_pages = {}
for i, page in enumerate(doc):
    text = page.get_text("text")
    for kw in keywords:
        if kw in text:
            found_pages.setdefault(kw, []).append(i+1)

print("\n--- Keyword occurrences by page ---")
for kw, pages in found_pages.items():
    print(f"{kw}: {len(pages)} pages (first few: {pages[:10]})")

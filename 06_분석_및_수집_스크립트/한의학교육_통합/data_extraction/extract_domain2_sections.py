import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_standards_all.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for criteria in Domain 2
# Let's find patterns like: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 2.10
criteria_sections = []
for p in text.split("==================== PAGE "):
    if "기본기준 2." in p or "우수기준 2." in p or "평가기준 2." in p or "2.1." in p or "2.2." in p or "2.3." in p:
        criteria_sections.append(p)

print(f"Found {len(criteria_sections)} pages with Domain 2 criteria.")
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_domain2_extracted.txt", "w", encoding="utf-8") as f:
    for c in criteria_sections:
        f.write("\n========================================\n" + c)

print("Saved kascom_domain2_extracted.txt.")

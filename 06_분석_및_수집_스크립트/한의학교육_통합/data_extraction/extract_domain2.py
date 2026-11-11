import json
import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

pages = text.split("==================== PAGE ")

print(f"Total parsed pages: {len(pages)}")

# Search for Domain 2 (교육과정)
curriculum_pages = []
for p in pages[1:]:
    p_num = p.split(" ====================")[0]
    p_content = p.split(" ====================")[1] if " ====================" in p else p
    if "영역 2" in p_content or "2. 교육과정" in p_content or "기본기준 2." in p_content:
        curriculum_pages.append((int(p_num), p_content))

print(f"Found {len(curriculum_pages)} pages mentioning Domain 2 (교육과정).")

# Save Domain 2 text for analysis
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_domain2_curriculum.txt", "w", encoding="utf-8") as f:
    for p_num, content in curriculum_pages:
        f.write(f"\n\n--- PAGE {p_num} ---\n\n" + content)

print("Saved kascom_domain2_curriculum.txt.")

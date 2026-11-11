import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's extract all evaluation standards list (e.g. from Chapter 3 or overview)
# In KAS2022: 
# 영역 1: 사명과 발전계획
# 영역 2: 교육과정 (기초의학, 기초한의학, 임상한의학, 임상실습, 통합교육 등)
# 영역 3: 학생평가
# 영역 4: 학생
# 영역 5: 교수
# 영역 6: 시설 및 설비

# Let's find pages 60 to 180 and extract the evaluation items
pages = text.split("==================== PAGE ")

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_standards_all.txt", "w", encoding="utf-8") as f:
    for idx, p in enumerate(pages):
        f.write(f"\n\n==================== PAGE {idx} ====================\n")
        f.write(p)

print("Saved kascom_standards_all.txt.")

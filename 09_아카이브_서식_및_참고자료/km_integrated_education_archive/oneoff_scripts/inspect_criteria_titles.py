import re

with open(r"d:\행정\한의학 교육과 의료 통합\kascom_domain2_extracted.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Let's extract all criteria numbers and titles
criteria = re.findall(r'(\d+\.\d+[\.\d]*\s+[^\n]+)', content)
print("Found criteria titles:")
unique_crit = []
for c in criteria:
    if any(k in c for k in ["교육과정", "기초", "임상", "실습", "인문", "통합", "평가", "역량", "한의학", "의생명"]):
        if c not in unique_crit:
            unique_crit.append(c)

for c in unique_crit[:40]:
    print(" -", c)

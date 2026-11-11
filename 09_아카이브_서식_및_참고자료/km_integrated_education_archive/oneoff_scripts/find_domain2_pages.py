import re

with open(r"d:\행정\한의학 교육과 의료 통합\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for "영역 2" or "교육과정" section in chapter 3
# Let's inspect where "2. 교육과정" or "영역 2" appears with its full text
pages = text.split("==================== PAGE ")

domain2_full = []
for p in pages:
    if "영역 2" in p or "교육과정" in p:
        lines = p.splitlines()
        for l in lines:
            if "2." in l and ("기준" in l or "교육" in l or "실습" in l or "평가" in l):
                domain2_full.append((p.split(" ====================")[0], l))

print("Found lines:")
for pno, l in domain2_full[:50]:
    print(f"Page {pno}: {l}")

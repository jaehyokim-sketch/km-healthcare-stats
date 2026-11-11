import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect TOC pages (usually pages 3 to 15)
pages = text.split("==================== PAGE ")

toc_text = ""
for p in pages[1:15]:
    toc_text += "\n" + p

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_toc.txt", "w", encoding="utf-8") as f:
    f.write(toc_text)

print("Saved KAS2022 TOC.")

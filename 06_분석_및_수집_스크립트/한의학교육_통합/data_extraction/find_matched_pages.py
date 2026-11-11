with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's find occurrences of "기본기준 2." or "2.3.1" or "2.5.3"
pages = text.split("==================== PAGE ")

found = []
for p in pages:
    if "2.3.1." in p or "2.5.3." in p or "2.5.1." in p or "2.6.2." in p or "2.6.1." in p:
        pno = p.split(" ====================")[0]
        found.append((pno, p[:2000]))

print(f"Found {len(found)} matching pages.")

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_matched_pages.txt", "w", encoding="utf-8") as out:
    for pno, content in found:
        out.write(f"\n\n==================== MATCHED PAGE {pno} ====================\n")
        out.write(content)

print("Saved kascom_matched_pages.txt.")

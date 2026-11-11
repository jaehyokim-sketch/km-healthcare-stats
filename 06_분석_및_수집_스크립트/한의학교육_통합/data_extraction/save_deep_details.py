with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

pages = text.split("==================== PAGE ")

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_domain2_deep_details.txt", "w", encoding="utf-8") as out:
    for idx in range(100, 160):
        if idx < len(pages):
            out.write(f"\n\n==================== PAGE {idx} ====================\n")
            out.write(pages[idx])

print("Saved kascom_domain2_deep_details.txt.")

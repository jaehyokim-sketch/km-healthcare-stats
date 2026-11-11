import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's search for the criteria definitions in Chapter 3
criteria_codes = ["P2.1.1", "P2.1.2", "P2.2.1", "P2.3.1", "P2.4.1", "P2.5.1", "P2.5.2", "P2.5.3", "P2.5.4", "A2.5.1", "A2.5.2", "A2.5.3", "A2.5.4", "P2.6.1", "P2.6.2", "A2.6.1", "A2.6.2", "P3.1.1", "P3.1.2", "P3.2.1"]

extracted_details = {}

pages = text.split("==================== PAGE ")

for p in pages:
    for code in criteria_codes:
        if f"[{code}]" in p or f"【{code}】" in p or f"기준 {code}" in p or f"{code}." in p or f"기본기준 {code}" in p:
            extracted_details.setdefault(code, []).append(p)

print(f"Extracted criteria details for {len(extracted_details)} codes.")

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_criteria_full_text.txt", "w", encoding="utf-8") as f:
    for code, chunks in extracted_details.items():
        f.write(f"\n\n############################################################\n")
        f.write(f"### CRITERION: {code}\n")
        f.write(f"############################################################\n")
        for chunk in chunks:
            f.write(chunk + "\n" + "-"*50 + "\n")

print("Saved kascom_criteria_full_text.txt.")

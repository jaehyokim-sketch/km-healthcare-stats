import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_domain2_extracted.txt", "r", encoding="utf-8") as f:
    content = f.read()

# Let's extract the criteria list from the beginning of Domain 2 in KAS2022
# Let's find the table or list of criteria 2.1 to 2.8
# Let's write out a clear summary
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_domain2_readable_summary.txt", "w", encoding="utf-8") as f:
    for block in content.split("========================================"):
        if "기준" in block or "교육" in block:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            f.write("\n\n" + "-"*60 + "\n")
            f.write("\n".join(lines[:60]))

print("Saved readable summary of Domain 2.")

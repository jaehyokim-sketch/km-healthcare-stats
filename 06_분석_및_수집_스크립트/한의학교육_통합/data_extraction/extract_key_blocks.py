import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_criteria_full_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\key_criteria_extracted.txt", "w", encoding="utf-8") as out:
    blocks = text.split("############################################################")
    for b in blocks:
        if any(k in b for k in ["CRITERION: P2.3.1", "CRITERION: P2.5.1", "CRITERION: P2.5.3", "CRITERION: P2.6.1", "CRITERION: P2.6.2", "CRITERION: A2.6.1", "CRITERION: P3.1.2"]):
            out.write("\n\n" + "="*80 + "\n")
            out.write(b[:4000]) # write first 4000 chars of block

print("Saved key_criteria_extracted.txt.")

import re

with open(r"d:\행정\한의학 교육과 의료 통합\kascom_criteria_full_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect P2.3.1, P2.5.1, P2.5.2, P2.5.3, P2.5.4, P2.6.1, P2.6.2
blocks = text.split("############################################################")
for b in blocks:
    if "### CRITERION: P2.3.1" in b or "### CRITERION: P2.5.3" in b or "### CRITERION: P2.6.1" in b or "### CRITERION: P2.6.2" in b or "### CRITERION: A2.6.1" in b:
        lines = [l.strip() for l in b.splitlines() if l.strip()]
        print(f"=== {lines[1]} ===")
        print("\n".join(lines[2:35]))
        print("\n" + "="*50 + "\n")

import re

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\kascom_text.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Search for the detailed criteria of Domain 2 in Chapter 3
# Let's find pages where Domain 2 criteria are detailed
lines = text.splitlines()

domain2_items = []
recording = False
for idx, line in enumerate(lines):
    if "제2영역" in line or "영역 2" in line or "2. 교육과정" in line:
        # print some context
        context = "\n".join(lines[max(0, idx-2):min(len(lines), idx+30)])
        domain2_items.append((idx, context))

print(f"Occurrences of Domain 2 markers: {len(domain2_items)}")

# Let's extract the criteria list from pages 80 to 200
# Let's find criteria starting with [기본기준 2. or [우수기준 2.
criteria_pattern = re.compile(r'(기본기준\s*2\.\d+[\.\d]*|우수기준\s*2\.\d+[\.\d]*|[기준]\s*2\.\d+[\.\d]*)')
found_criteria = []
for idx, line in enumerate(lines):
    m = criteria_pattern.search(line)
    if m:
        found_criteria.append((idx, line, "\n".join(lines[idx:idx+40])))

print(f"Found criteria matches: {len(found_criteria)}")
with open(r"d:\행정\한의학 교육과 의료 통합\_archive\intermediate_outputs\kascom_domain2_detailed_criteria.txt", "w", encoding="utf-8") as f:
    for idx, line, chunk in found_criteria:
        f.write(f"\n==================== Line {idx}: {line} ====================\n")
        f.write(chunk)

print("Saved kascom_domain2_detailed_criteria.txt.")

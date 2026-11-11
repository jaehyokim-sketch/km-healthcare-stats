import re
import pandas as pd
import json

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\curriculum_table_raw.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Let's inspect how the text flows
pages = text.split("--- Page ")
courses = []

# Pattern to extract course entries
# Example:
# 교 / 필 / 001111 / 종교와원불교 / 3 / 3 / 0 / Religion and ...
# Let's write a comprehensive state machine parser

current_year = ""
current_sem = ""

lines = [line.strip() for line in text.splitlines() if line.strip()]

i = 0
while i < len(lines):
    line = lines[i]
    if line.startswith("예1") or line.startswith("예2") or line.startswith("본1") or line.startswith("본2") or line.startswith("본3") or line.startswith("본4") or line.startswith("의예") or line.startswith("의학"):
        current_year = line
    elif line in ["1학기", "2학기", "1", "2"] and i > 0 and lines[i-1] in ["학기", "학", "년", "구", "분", "예1", "예2", "본1", "본2", "본3", "본4"]:
        current_sem = line
    
    # Check if this line is course code (6 digits or specific format)
    # or if we have classification like 교필, 교선, 전필, 전선
    # Let's look at numbers and subject names
    i += 1

print(f"Total lines: {len(lines)}")

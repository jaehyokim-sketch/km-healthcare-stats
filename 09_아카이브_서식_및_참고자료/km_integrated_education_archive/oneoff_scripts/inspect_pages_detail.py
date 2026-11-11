import os
import re
import pandas as pd

# Let's see how each page text is formatted
courses = []

year_map = {
    17: ("예1", "1/2"),
    18: ("예1", "2"),
    19: ("예2", "1"),
    20: ("예2", "2"),
    21: ("본1", "1"),
    22: ("본1", "2"),
    23: ("본2", "1/2"),
    24: ("본2/3", "2/1"),
    25: ("본3", "1/2"),
    26: ("본4", "1/2")
}

# Let's inspect page 17 to 26 text directly with Python
for pno in range(17, 27):
    with open(rf"d:\행정\한의학 교육과 의료 통합\page_{pno}_lines.txt", "r", encoding="utf-8") as f:
        content = f.read()
    print(f"=== Page {pno} (Length: {len(content)}) ===")
    lines = [l.strip() for l in content.splitlines() if l.strip()]
    print("\n".join(lines[:40]))

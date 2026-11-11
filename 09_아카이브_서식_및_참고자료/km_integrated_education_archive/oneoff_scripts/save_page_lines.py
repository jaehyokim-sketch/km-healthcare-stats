import fitz
import re
import json
import pandas as pd

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\curriculum.pdf")

# Let's inspect pages 17 to 26 text line by line to get accurate korean characters
# PyMuPDF get_text("text") extracts unicode accurately
all_courses = []

current_year = ""
current_sem = ""

for pno in range(16, 26):
    text = doc[pno].get_text("text")
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    
    # We can parse the exact structure
    # Let's log each page's raw lines
    with open(rf"d:\행정\한의학 교육과 의료 통합\page_{pno+1}_lines.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

print("Saved raw text of pages 17-26")

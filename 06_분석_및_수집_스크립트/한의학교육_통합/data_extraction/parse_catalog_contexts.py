import fitz
import re
import pandas as pd
import json

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\원문\curriculum.pdf")

# Let's map page by page
# Let's extract each page 17-27 block by block or line by line
catalog = []

for pno in range(16, 27):
    page = doc[pno]
    text = page.get_text("text")
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    
    # Let's find course codes and their data
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r'^\d{6}$', line):
            code = line
            # Course name (Korean is above or right before code, or classification is above)
            # Let's find classification before code
            clf = ""
            for back_i in range(max(0, i-4), i):
                if lines[back_i] in ["교필", "전필", "전선", "교선", "일선"]:
                    clf = lines[back_i]
            
            # The next tokens are usually: name (if after), or credit, theory, lab, eng name
            # Let's see: in the text layout:
            # Code is followed by Name, or Name is before Code
            # Let's inspect tokens around i
            context = lines[max(0, i-4):min(len(lines), i+12)]
            catalog.append({
                "page": pno + 1,
                "code": code,
                "context": context
            })
        i += 1

print(f"Total course code occurrences: {len(catalog)}")
with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\catalog_contexts.json", "w", encoding="utf-8") as f:
    json.dump(catalog, f, ensure_ascii=False, indent=2)

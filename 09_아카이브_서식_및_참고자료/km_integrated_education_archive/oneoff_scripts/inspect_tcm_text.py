import fitz

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\세계중의본과교육표준(정체판).pdf")

for page_num in range(min(10, len(doc))):
    page = doc[page_num]
    text = page.get_text()
    print(f"--- Page {page_num+1} ---")
    # Print lines that have ascii or text
    for line in text.splitlines():
        if line.strip():
            print(line[:100])

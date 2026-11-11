import fitz

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\세계중의본과교육표준(정체판).pdf")

print("PDF metadata:", doc.metadata)
for p in range(min(5, len(doc))):
    print(f"Page {p+1} fonts:")
    for f in doc[p].get_fonts():
        print(" ", f)

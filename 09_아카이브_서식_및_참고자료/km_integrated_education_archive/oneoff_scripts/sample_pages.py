import fitz

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\curriculum.pdf")

for pno in [26, 27, 28, 29, 30, 50, 100, 200, 500]:
    print(f"==================== PAGE {pno+1} ====================")
    text = doc[pno].get_text("text")
    print(text[:800])

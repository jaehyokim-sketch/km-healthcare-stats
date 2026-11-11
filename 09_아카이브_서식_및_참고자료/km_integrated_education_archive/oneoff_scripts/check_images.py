import fitz

doc = fitz.open(r"d:\행정\한의학 교육과 의료 통합\curriculum.pdf")

for pno in [27, 28, 29, 30, 31, 32]:
    page = doc[pno]
    imgs = page.get_images()
    text = page.get_text()
    print(f"Page {pno+1}: text len = {len(text)}, images count = {len(imgs)}")
    for img in imgs:
        print("  Image:", img)

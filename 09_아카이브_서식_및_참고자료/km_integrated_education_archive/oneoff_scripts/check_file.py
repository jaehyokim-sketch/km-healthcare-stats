import os

with open(r"d:\행정\한의학 교육과 의료 통합\curriculum_downloaded.bin", "rb") as f:
    header = f.read(100)
    print("Header bytes:", header[:32])
    print("Header ASCII/text:", header[:100])

if header.startswith(b"%PDF"):
    print("It is a PDF file!")
    os.rename(r"d:\행정\한의학 교육과 의료 통합\curriculum_downloaded.bin", r"d:\행정\한의학 교육과 의료 통합\curriculum.pdf")
    print("Renamed to curriculum.pdf")
elif header.startswith(b"PK"):
    print("It is a ZIP/Office file!")
    # Check if docx or xlsx or zip
elif header.startswith(b"\xd0\xcf\x11\xe0"):
    print("It is a compound binary file (doc/xls/hwp)!")
elif b"<!DOCTYPE html" in header or b"<html" in header:
    print("It is HTML! (Download confirmation page)")

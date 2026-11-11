import sys

for pkg in ['pypdf', 'pypdf2', 'pdfplumber', 'fitz', 'pdfminer']:
    try:
        __import__(pkg)
        print(f"Package {pkg}: available")
    except ImportError:
        print(f"Package {pkg}: NOT available")

import json
import pandas as pd

with open(r"d:\행정\한의학 교육과 의료 통합\extracted_tables.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data[:25]:
    print(item)

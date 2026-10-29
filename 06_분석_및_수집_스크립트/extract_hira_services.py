import re
import json
import pandas as pd
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '05_원천_통계_데이터셋', 'hira_medinfo_page.html'), 'r', encoding='utf-8', errors='ignore') as f:
    html = f.read()

tables = re.findall(r'<table[^>]*>([\s\S]*?)</table>', html)
if not tables:
    print("No table found")
    sys.exit(1)

t = tables[0]
rows = re.findall(r'<tr[^>]*>([\s\S]*?)</tr>', t)

header_row = rows[0]
headers = [re.sub(r'<[^>]+>', '', c).strip() for c in re.findall(r'<th[^>]*>([\s\S]*?)</th>', header_row)]
print("Headers:", headers)

data_list = []
for r in rows[1:]:
    # extract cells
    cells = re.findall(r'<td[^>]*>([\s\S]*?)</td>', r)
    row_data = {}
    for idx, c in enumerate(cells):
        col_name = headers[idx] if idx < len(headers) else f"col_{idx}"
        
        # extract text
        clean_text = re.sub(r'<[^>]+>', '', c).strip()
        row_data[col_name] = clean_text
        
        # check for links, onclick, or buttons
        onclicks = re.findall(r'onclick=\"([^\"]*)\"', c)
        hrefs = re.findall(r'href=\"([^\"]*)\"', c)
        if onclicks:
            row_data[f"{col_name}_onclick"] = onclicks[0]
        if hrefs and hrefs[0] != "#":
            row_data[f"{col_name}_href"] = hrefs[0]
            
    data_list.append(row_data)

df = pd.DataFrame(data_list)
print(f"\nTotal Services Extracted: {len(df)}")
print("\nSample (first 10 rows):")
print(df[['번호', '대분류', '중분류', '소분류']].head(10))

# Save all services to CSV and JSON
output_dir = r"d:\한의 의료서비스 통계\05_원천_통계_데이터셋\06_HIRA_한의의료_마스터DB"
os.makedirs(output_dir, exist_ok=True)

all_csv_path = os.path.join(output_dir, "HIRA_의료정보서비스_전체목록_147종.csv")
df.to_csv(all_csv_path, index=False, encoding='utf-8-sig')
print(f"\nSaved all services to: {all_csv_path}")

# Filter for Korean Medicine / Hospital / Clinic / Disease / Fee related
km_keywords = ["한방", "한의", "한의원", "한의사", "침구", "탕전", "요양기관", "질병", "진료비", "수가", "약제", "의료이용"]
matched_rows = []

for idx, row in df.iterrows():
    combined_text = f"{row.get('대분류', '')} {row.get('중분류', '')} {row.get('소분류', '')}"
    is_km = any(kw in combined_text for kw in km_keywords)
    if is_km:
        matched_rows.append(row)

df_km = pd.DataFrame(matched_rows)
print(f"\nTotal Matched Services for Healthcare / Korean Medicine: {len(df_km)}")
print(df_km[['번호', '대분류', '중분류', '소분류']].to_string())

km_csv_path = os.path.join(output_dir, "HIRA_한의약_및_주요의료서비스_목록.csv")
df_km.to_csv(km_csv_path, index=False, encoding='utf-8-sig')
print(f"\nSaved filtered services to: {km_csv_path}")

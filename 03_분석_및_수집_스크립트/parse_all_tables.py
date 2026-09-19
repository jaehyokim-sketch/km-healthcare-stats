from bs4 import BeautifulSoup
import re

with open("datagov_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

rows = soup.find_all("tr")
print(f"Total Rows: {len(rows)}")

# 각 row가 다운로드나 과거 버전과 관련이 있는지 검사
for idx, row in enumerate(rows):
    row_text = row.get_text(strip=True)
    # '개정', '변경', '이력', '2023', '2022', '2021', '2020', '다운로드' 등이 포함되어 있는지 확인
    if any(k in row_text for k in ["2023", "2022", "2021", "2020", "이력", "제공"]):
        print(f"\nRow [{idx}]: {row_text[:150]}")
        # row 내의 모든 a 태그와 button 태그 출력
        for tag in row.find_all(["a", "button"]):
            print(f"  Tag: <{tag.name}> Text: {tag.get_text(strip=True)} -> onclick: {tag.get('onclick')}, href: {tag.get('href')}")

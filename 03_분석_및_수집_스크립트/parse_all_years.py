from bs4 import BeautifulSoup
import re

with open("datagov_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# 과거 파일 목록이나 다른 다운로드 링크들을 찾아봅니다.
# 보통 tbody 내의 행들에 과거 파일 이력이 있습니다.
rows = soup.find_all("tr")
print(f"Found {len(rows)} table rows in the detail page.")

# fn_fileDataDown 이나 fileDetailObj.fn_fileDataDown 호출이 포함된 요소들을 찾습니다.
matches = []
for tag in soup.find_all(lambda t: t.has_attr("onclick") and "fn_fileDataDown" in t["onclick"]):
    onclick = tag["onclick"]
    text = tag.get_text(strip=True)
    # parent tr을 찾아서 어떤 연도 데이터인지 알아봅니다.
    parent_tr = tag.find_parent("tr")
    tr_text = parent_tr.get_text(strip=True) if parent_tr else "No parent tr"
    matches.append((onclick, text, tr_text))

print(f"\nFound {len(matches)} download actions:")
for idx, (onclick, text, tr_text) in enumerate(matches):
    print(f"[{idx}] Onclick: {onclick}")
    print(f"    Text: {text}")
    print(f"    Row Text: {tr_text[:200]}")

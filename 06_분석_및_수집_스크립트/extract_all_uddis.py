import re

with open("datagov_detail.html", "r", encoding="utf-8") as f:
    html = f.read()

# 'uddi:...' 패턴 모두 찾기 (대소문자 구분 없이)
uddis = re.findall(r'uddi:[a-zA-Z0-9_\-]+', html, re.IGNORECASE)
print(f"Found {len(uddis)} UDDI codes:")
for u in set(uddis):
    print("  ", u)

# fn_fileDataDown 또는 fileDetailObj.fn_fileDataDown 호출에서 인자값들 모두 추출
calls = re.findall(r'fn_fileDataDown\s*\(\s*[\'"]?(\d+)[\'"]?\s*,\s*[\'"]?(uddi:[a-zA-Z0-9_\-]+)[\'"]?', html, re.IGNORECASE)
print(f"\nFound {len(calls)} fn_fileDataDown calls:")
for c in set(calls):
    print("  ", c)

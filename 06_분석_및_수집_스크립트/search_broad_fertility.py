import urllib.request
import urllib.parse
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

keywords = ["난임", "불임", "한방", "한의약", "모자보건", "임신지원"]

for kw in keywords:
    url = f"https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword={urllib.parse.quote(kw)}&dataType=FILE"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            links = re.findall(r'href="/data/(\d+)/fileData\.do"[^>]*>([\s\S]*?)</a>', html)
            print(f"\n=== 키워드: '{kw}' 검색 결과 ({len(links)}건) ===")
            for pk, raw_t in links[:6]:
                t = re.sub(r'<[^>]+>', '', raw_t).strip()
                if t:
                    print(f"  [{pk}] {t}")
    except Exception as e:
        print(f"Error for {kw}: {e}")

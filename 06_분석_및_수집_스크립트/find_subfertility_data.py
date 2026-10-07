import urllib.request
import urllib.parse
import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

print("=== data.go.kr '난임' 데이터셋 크롤링/검색 ===")
url = "https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword=" + urllib.parse.quote("난임") + "&dataType=FILE"
req = urllib.request.Request(url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Extract title and link
        # pattern: /data/(\d+)/fileData.do
        links = re.findall(r'href="/data/(\d+)/fileData\.do"[^>]*>([\s\S]*?)</a>', html)
        print(f"Found {len(links)} fileData links:")
        for pk, raw_t in links:
            t = re.sub(r'<[^>]+>', '', raw_t).strip()
            if t:
                print(f"  [PK: {pk}] {t}")
                
        # Also check pagination or count
        total_m = re.search(r'전체\s*<strong[^>]*>([\d,]+)</strong>\s*건', html)
        if total_m:
            print(f"Total Results on data.go.kr: {total_m.group(1)}")
except Exception as e:
    print("Error:", e)

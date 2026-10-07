import urllib.request
import urllib.parse
import json
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

keywords = ["한방 난임", "한의약 난임", "한방난임", "한의약난임", "난임 한방"]
all_datasets = {}

for kw in keywords:
    print(f"\n==========================================")
    print(f"Searching data.go.kr for: '{kw}'")
    print(f"==========================================")
    
    url = f"https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword={urllib.parse.quote(kw)}&dataType=ALL"
    req = urllib.request.Request(url, headers=headers)
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
            
            # Extract items: /data/{pk}/fileData.do or /data/{pk}/openapi.do
            # Match titles, organization, dataset type
            items = re.findall(r'href="/data/(\d+)/(fileData|openapi)\.do"[^>]*>[\s\S]*?<span class="title">([\s\S]*?)</span>', html)
            
            # Find organization names
            orgs = re.findall(r'<span class="publicDataOpnInstNm"[^>]*>([\s\S]*?)</span>', html)
            
            print(f"Found {len(items)} results:")
            for idx, (pk, dtype, title_raw) in enumerate(items):
                title = re.sub(r'<[^>]+>', '', title_raw).strip()
                org = re.sub(r'<[^>]+>', '', orgs[idx]).strip() if idx < len(orgs) else "Unknown"
                if pk not in all_datasets:
                    all_datasets[pk] = {
                        "pk": pk,
                        "type": dtype,
                        "title": title,
                        "org": org,
                        "keyword": kw
                    }
                    print(f"  [{dtype.upper()}] PK: {pk} | Org: {org} | Title: {title}")
    except Exception as e:
        print(f"Error searching for {kw}: {e}")

print(f"\n==========================================")
print(f"Total Unique Datasets Found: {len(all_datasets)}")
print(f"==========================================")
for pk, info in all_datasets.items():
    print(f"- PK: {info['pk']} | Type: {info['type']} | Org: {info['org']} | Title: {info['title']}")

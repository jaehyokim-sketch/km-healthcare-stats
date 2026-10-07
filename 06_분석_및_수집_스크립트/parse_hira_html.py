import urllib.request
import urllib.parse
import json
import re
import sys
import ssl

sys.stdout.reconfigure(encoding='utf-8')

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.options |= 0x4

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://opendata.hira.or.kr/op/opc/selectMedInfoSvcList.do"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        
        # Save HTML for inspection
        with open("hira_medinfo_page.html", "w", encoding="utf-8") as f:
            f.write(html)
        print(f"Saved HTML ({len(html)} bytes)")
        
        # Search for form actions, ajax URLs, data tables
        forms = re.findall(r'<form[^>]*action=\"([^\"]*)\"[^>]*>', html)
        print("Forms found:", forms)
        
        # Search for list items, titles, buttons
        titles = re.findall(r'<strong[^>]*class=\"[^\"]*tit[^\"]*\"[^>]*>([\s\S]*?)</strong>', html)
        print(f"Found {len(titles)} tit strong tags:")
        for t in titles[:10]:
            print("  -", re.sub(r'<[^>]+>', '', t).strip())
            
        # Search for table subjects
        subjects = re.findall(r'<td[^>]*class=\"subject\"[^>]*>([\s\S]*?)</td>', html)
        print(f"Found {len(subjects)} subjects:")
        for s in subjects[:10]:
            print("  -", re.sub(r'<[^>]+>', '', s).strip())

        # Search for any API names
        apis = re.findall(r'(?:get[A-Z][a-zA-Z0-9]+|Service[0-9.]*)', html)
        print(f"Found {len(set(apis))} API patterns:")
        for a in sorted(set(apis))[:15]:
            print("  -", a)
            
except Exception as e:
    print("Error:", e)

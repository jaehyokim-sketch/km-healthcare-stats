import urllib.request
import urllib.parse
import json
import re
import sys
import ssl

sys.stdout.reconfigure(encoding='utf-8')

# SSL context for public websites
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
ctx.options |= 0x4  # SSL_OP_LEGACY_SERVER_CONNECT

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

url = "https://opendata.hira.or.kr/op/opc/selectMedInfoSvcList.do"
print(f"Connecting to: {url}")

req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
        html = resp.read().decode('utf-8', errors='ignore')
        print(f"Response Status: {resp.status}, HTML Length: {len(html)}")
        
        # Look for service titles, API links, tables, or list items
        # Usually HIRA lists services in table or list with onclick or href
        services = re.findall(r'<a[^>]*href=\"[^\"]*(?:selectMedInfoSvcDetail|fn_selectMedInfoSvcDetail|selectOpenApiDetail)[^\"]*\"[^>]*>([\s\S]*?)</a>', html)
        if not services:
            services = re.findall(r'<span class=\"title\"[^>]*>([\s\S]*?)</span>', html)
        if not services:
            services = re.findall(r'<td[^>]*class=\"subject\"[^>]*>[\s\S]*?<a[^>]*>([\s\S]*?)</a>', html)
            
        print(f"Found {len(services)} services directly:")
        for s in services[:15]:
            clean = re.sub(r'<[^>]+>', '', s).strip()
            print("  -", clean)
            
        # Also find all text containing 한방, 한의, 한의원, 한의사
        km_matches = set(re.findall(r'[^.\n]*?(?:한방|한의|한의원|한의사|침구|한약)[^.\n]*', html))
        print(f"\nFound {len(km_matches)} Korean medicine related snippets on page:")
        for m in list(km_matches)[:10]:
            print("  *", m.strip())

except Exception as e:
    print("Error:", e)

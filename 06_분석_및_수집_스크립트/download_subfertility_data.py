import requests
import json
import urllib.parse
import os
import sys
import re

sys.stdout.reconfigure(encoding='utf-8')

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

output_dir = os.path.join(os.path.dirname(__file__), "..", "02_통계_데이터셋", "05_난임_및_한방모자보건")
os.makedirs(output_dir, exist_ok=True)

target_pks = [
    ("15143044", "NHIS_불임_및_유산_상병별_진료현황"),
    ("15127567", "NHIS_난임진료_F021_시도별_연령별_진료인원_건수"),
    ("15120483", "NHIS_특정지역_난임_진료인원_및_진료건수"),
    ("15085119", "서울시_모자보건사업_통계_한의약난임포함"),
    ("15064879", "인천시_모자보건사업_실적"),
    ("15140374", "보건복지부_임신사전건강관리_지원사업_청구현황")
]

for pk, desc in target_pks:
    print(f"\n==========================================")
    print(f"Downloading [{desc}] (PK: {pk})...")
    print(f"==========================================")
    
    detail_url = f"https://www.data.go.kr/data/{pk}/fileData.do"
    try:
        res_page = session.get(detail_url, timeout=15)
        html = res_page.text
        
        # Extract UDDI
        uddis = re.findall(r'uddi:[a-zA-Z0-9_\-]+', html, re.IGNORECASE)
        if not uddis:
            print(f"[-] No UDDI found for PK {pk}")
            continue
            
        uddi = uddis[0]
        print(f"[+] Found UDDI: {uddi}")
        
        meta_url = "https://www.data.go.kr/tcs/dss/selectFileDataDownload.do"
        meta_data = {
            "publicDataPk": pk,
            "publicDataDetailPk": uddi
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": detail_url
        }
        
        res_meta = session.post(meta_url, data=meta_data, headers=headers, timeout=15)
        meta_json = res_meta.json()
        
        if meta_json.get("status") is True:
            atchFileId = meta_json.get("atchFileId")
            fileDetailSn = meta_json.get("fileDetailSn")
            dataNm = meta_json.get("dataSetFileDetailInfo", {}).get("dataNm", f"{desc}.csv")
            
            # Clean filename
            safe_name = re.sub(r'[\\/*?:"<>|]', '_', dataNm)
            output_file = os.path.join(output_dir, safe_name)
            
            download_url = f"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId={atchFileId}&fileDetailSn={fileDetailSn}&dataNm={urllib.parse.quote(dataNm)}"
            print(f"[+] Downloading file from: {download_url}")
            
            res_file = session.get(download_url, timeout=30)
            with open(output_file, "wb") as f:
                f.write(res_file.content)
                
            print(f"[+] Saved: {output_file} (Size: {len(res_file.content):,} bytes)")
        else:
            print(f"[-] Meta request failed: {meta_json}")
    except Exception as e:
        print(f"[-] Error processing PK {pk}: {e}")

print("\n[+] Download process finished.")

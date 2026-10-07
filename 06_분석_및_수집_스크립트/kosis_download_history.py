import requests
import json
import urllib.parse
import os

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

# general (15139381) 의 과거 버전으로 보이는 UDDI 목록
history_uddis = [
    "uddi:8eaaef27-2b44-4bc1-9397-ce7c5313630f_202210311641",
    "uddi:1a15d1d4-d4f6-4e1b-967a-b813120c9f5f_202301101341",
    "uddi:5a09990b-4f58-43ea-a59d-fae7b5ec72a3"
]

pk = "15139381"
detail_url = f"https://www.data.go.kr/data/{pk}/fileData.do"
session.get(detail_url, timeout=10)

for idx, uddi in enumerate(history_uddis):
    print(f"\nTrying to download history file {idx+1}: {uddi}")
    
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
    
    try:
        res_meta = session.post(meta_url, data=meta_data, headers=headers, timeout=10)
        meta_json = res_meta.json()
        print("Meta Response:", meta_json)
        
        if meta_json.get("status") is True:
            atchFileId = meta_json.get("atchFileId")
            fileDetailSn = meta_json.get("fileDetailSn")
            dataNm = meta_json.get("dataSetFileDetailInfo", {}).get("dataNm", f"general_hist_{idx+1}.csv")
            
            download_url = f"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId={atchFileId}&fileDetailSn={fileDetailSn}&dataNm={urllib.parse.quote(dataNm)}"
            print(f"Downloading from: {download_url}")
            
            res_file = session.get(download_url, timeout=30)
            output_path = f"general_hist_{idx+1}.csv"
            with open(output_path, "wb") as f:
                f.write(res_file.content)
            print(f"Saved to {output_path} (Size: {os.path.getsize(output_path)} bytes)")
            
            # 첫 2줄 검사해서 연도 확인
            with open(output_path, "r", encoding="cp949", errors="ignore") as f_check:
                lines = [f_check.readline() for _ in range(3)]
                print("Content Preview:")
                for l in lines:
                    print("  ", l.strip())
        else:
            print("Failed to get meta info")
    except Exception as e:
        print("Error:", e)

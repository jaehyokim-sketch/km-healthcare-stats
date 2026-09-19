import requests
import json
import urllib.parse
import os

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
})

datasets = {
    "clinic_2023": {
        "pk": "15055562",
        "dpk": "uddi:844cdb4d-3ee4-4e6a-84a6-e1f3c7ca40a4",
        "output": "clinic_2023.csv"
    },
    "clinic_2022": {
        "pk": "15055562",
        "dpk": "uddi:59187f89-1264-4a06-9482-f154b2f979ff",
        "output": "clinic_2022.csv"
    },
    "clinic_2021": {
        "pk": "15055562",
        "dpk": "uddi:fc9fda19-2bc3-4620-bfae-c1b3028e938e",
        "output": "clinic_2021.csv"
    },
    "hospital_2023": {
        "pk": "15055565",
        "dpk": "uddi:f4ffef34-09e3-4cbb-8b7d-9f6d3c35a388",
        "output": "hospital_2023.csv"
    },
    "hospital_2022": {
        "pk": "15055565",
        "dpk": "uddi:86b6d41d-5899-4941-b05f-85807232f92c",
        "output": "hospital_2022.csv"
    },
    "hospital_2021": {
        "pk": "15055565",
        "dpk": "uddi:a7f854d0-86f6-4291-9310-a7d5396ff5dd",
        "output": "hospital_2021.csv"
    }
}

for name, info in datasets.items():
    print(f"\nProcessing {name} ({info['pk']})...")
    detail_url = f"https://www.data.go.kr/data/{info['pk']}/fileData.do"
    session.get(detail_url, timeout=10)
    
    meta_url = "https://www.data.go.kr/tcs/dss/selectFileDataDownload.do"
    meta_data = {
        "publicDataPk": info["pk"],
        "publicDataDetailPk": info["dpk"]
    }
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": detail_url
    }
    
    try:
        res_meta = session.post(meta_url, data=meta_data, headers=headers, timeout=10)
        meta_json = res_meta.json()
        
        if meta_json.get("status") is True:
            atchFileId = meta_json.get("atchFileId")
            fileDetailSn = meta_json.get("fileDetailSn")
            dataNm = meta_json.get("dataSetFileDetailInfo", {}).get("dataNm", f"{name}.csv")
            
            download_url = f"https://www.data.go.kr/cmm/cmm/fileDownload.do?atchFileId={atchFileId}&fileDetailSn={fileDetailSn}&dataNm={urllib.parse.quote(dataNm)}"
            print(f"Downloading from: {download_url}")
            
            res_file = session.get(download_url, timeout=30)
            output_path = info["output"]
            with open(output_path, "wb") as f:
                f.write(res_file.content)
            print(f"Saved to {output_path} (Size: {os.path.getsize(output_path)} bytes)")
        else:
            print(f"Failed to get meta info for {name}")
    except Exception as e:
        print(f"Error processing {name}: {e}")

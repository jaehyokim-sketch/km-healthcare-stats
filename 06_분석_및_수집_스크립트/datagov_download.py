import requests
from bs4 import BeautifulSoup
import re

dataset_ids = ["15139381", "15051060", "15055565", "15055562", "15089587"]
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for did in dataset_ids:
    url = f"https://www.data.go.kr/data/{did}/fileData.do"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 데이터셋 제목 파싱
        # 보통 class="title" 이나 h1 태그 등에 제목이 들어있습니다.
        title_elem = soup.find("h1", class_="title") or soup.find("p", class_="title")
        title = title_elem.get_text(strip=True) if title_elem else f"Unknown({did})"
        
        print(f"\nDataset ID: {did}")
        print(f"Title: {title}")
        
        # 다운로드 버튼 찾기
        # 공공데이터포털의 다운로드 버튼은 보통 '다운로드' 텍스트를 포함하거나
        # class="btn-primary" 이고 onclick에 다운로드 함수가 걸려있습니다.
        # 또는 직접 다운로드 링크가 href에 들어가 있습니다.
        download_links = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if "download" in href.lower() or "download" in text.lower() or "다운로드" in text:
                download_links.append((text, href))
                
        # button 태그의 onclick도 검사
        for btn in soup.find_all("button", onclick=True):
            onclick = btn["onclick"]
            text = btn.get_text(strip=True)
            if "download" in onclick.lower() or "다운로드" in text:
                download_links.append((text, onclick))
                
        for text, link in download_links:
            print(f"  Button: {text} -> Action/Link: {link}")
            
    except Exception as e:
        print(f"Error for dataset {did}: {e}")

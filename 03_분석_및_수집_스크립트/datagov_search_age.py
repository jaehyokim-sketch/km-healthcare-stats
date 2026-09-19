import requests
from bs4 import BeautifulSoup
import urllib.parse

keyword = "건강보험심사평가원 연령별 진료"
encoded_keyword = urllib.parse.quote(keyword)
url = f"https://www.data.go.kr/tcs/dss/selectDataSetList.do?keyword={encoded_keyword}&datasetType=FILE"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

try:
    response = requests.get(url, headers=headers, timeout=15)
    soup = BeautifulSoup(response.text, "html.parser")
    
    titles = soup.find_all("span", class_="title")
    print("Found potential datasets for age:")
    for idx, t in enumerate(titles):
        print(f"[{idx}] {t.get_text(strip=True)}")
        
    links = soup.find_all("a", href=True)
    dataset_links = []
    for link in links:
        href = link["href"]
        text = link.get_text(strip=True)
        if "/data/" in href and "standardData" not in href:
            dataset_links.append((text, href))
            
    print(f"\nLinks:")
    for text, href in set(dataset_links):
        print(f"Text: {text} -> Link: https://www.data.go.kr{href}")
        
except Exception as e:
    print("Error:", e)

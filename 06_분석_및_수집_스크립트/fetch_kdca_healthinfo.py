"""
질병관리청(KDCA) 국가건강정보포털 Open API 수집 및 분석 스크립트
- 검색 End Point: https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchListApi.do
- 상세 End Point: http://api.kdca.go.kr/api/provide/healthInfo
- 인증 토큰: TOKEN=1a0cbb10c9d9
- 기본 콘텐츠: cntntsSn=6753 (재택의료/방문진료)
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
import requests
import ssl
from requests.adapters import HTTPAdapter

sys.stdout.reconfigure(encoding='utf-8')

class LegacySSLAdapter(HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.options |= 0x4  # SSL_OP_LEGACY_SERVER_CONNECT
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.options |= 0x4
        kwargs['ssl_context'] = ctx
        return super().proxy_manager_for(*args, **kwargs)

DEFAULT_TOKEN = "1a0cbb10c9d9"

def search_kdca_health_list(token: str = DEFAULT_TOKEN, srch_wrd: str = "", lclas_sn: str = "", page_index: int = 1) -> dict:
    url = "https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchListApi.do"
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    session.mount('http://', LegacySSLAdapter())
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    data = {
        "TOKEN": token,
        "srchWrd": srch_wrd,
        "lclasSn": lclas_sn,
        "pageIndex": str(page_index)
    }
    
    res = session.post(url, data=data, verify=False, timeout=15)
    res.raise_for_status()
    html = res.text
    
    matches = re.findall(r"fn_goView\s*\(\s*['\"]?(\d+)['\"]?\s*,\s*['\"]([^'\"]+)['\"]\s*\)", html)
    items = [{"cntntsSn": sn, "title": title.strip()} for sn, title in matches]
    
    return {
        "keyword": srch_wrd,
        "lclasSn": lclas_sn,
        "pageIndex": page_index,
        "count": len(items),
        "items": items
    }

def fetch_kdca_health_info(token: str = DEFAULT_TOKEN, cntnts_sn: str = "6753") -> dict:
    url = f"http://api.kdca.go.kr/api/provide/healthInfo?TOKEN={token}&cntntsSn={cntnts_sn}"
    session = requests.Session()
    session.mount('https://', LegacySSLAdapter())
    session.mount('http://', LegacySSLAdapter())
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    res = session.get(url, timeout=15)
    res.raise_for_status()
    
    root = ET.fromstring(res.text)
    code = root.findtext('.//CODE', default='')
    message = root.findtext('.//MESSAGE', default='')
    
    if code != 'S001':
        raise ValueError(f"KDCA API 오류: 코드={code}, 메시지={message}")
        
    title = root.findtext('.//CNTNTSSJ', default='')
    sn = root.findtext('.//CNTNTS_SN', default=cntnts_sn)
    lclass = root.findtext('.//LCLASSN', default='')
    
    sections = []
    for cl in root.findall('.//cntntsCl'):
        sec_name = cl.findtext('CNTNTS_CL_NM', default='')
        sec_sn = cl.findtext('CNTNTSCLSN', default='')
        sec_content = cl.findtext('CNTNTS_CL_CN', default='')
        if sec_name or sec_content:
            sections.append({
                "name": sec_name,
                "sn": sec_sn,
                "content": sec_content.strip() if sec_content else ""
            })
            
    return {
        "code": code,
        "message": message,
        "title": title,
        "cntntsSn": sn,
        "lclass": lclass,
        "total_sections": len(sections),
        "sections": sections
    }

def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith("--search="):
        kw = sys.argv[1].split("=", 1)[1]
        print(f"[*] KDCA 국가건강정보 키워드 검색 중... (검색어: '{kw}')")
        res = search_kdca_health_list(srch_wrd=kw)
        print(f"[+] 검색 결과: {res['count']}건")
        for it in res['items']:
            print(f" - [{it['cntntsSn']}] {it['title']}")
        return

    cntnts_sn = sys.argv[1] if len(sys.argv) > 1 else "6753"
    print(f"[*] 질병관리청(KDCA) 국가건강정보포털 Open API 호출 중... (cntntsSn={cntnts_sn})")
    
    data = fetch_kdca_health_info(cntnts_sn=cntnts_sn)
    print(f"[+] 성공: [{data['title']}] (섹션 수: {data['total_sections']}개)")
    
    # 1. JSON 파일로 저장
    output_json = f"kdca_healthinfo_{cntnts_sn}.json"
    output_path = os.path.join(os.path.dirname(__file__), "..", "05_원천_통계_데이터셋", output_json)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[+] JSON 데이터셋 저장 완료: {output_path}")
    
    # 2. 마크다운 보고서로 변환 저장
    clean_title = data['title'].replace('/', '_').replace(' ', '_')
    output_md = f"KDCA_국가건강정보_{clean_title}_요약.md"
    output_md_path = os.path.join(os.path.dirname(__file__), "..", output_md)
    
    md_lines = [
        f"# 질병관리청(KDCA) 국가건강정보 — {data['title']}",
        f"- **콘텐츠 번호(cntntsSn)**: `{data['cntntsSn']}`",
        f"- **분류 번호(LCLASSN)**: `{data['lclass']}`",
        f"- **출처**: 질병관리청 국가건강정보포털 Open API (`http://api.kdca.go.kr/api/provide/healthInfo`)",
        "\n---",
    ]
    for sec in data['sections']:
        md_lines.append(f"\n## 📌 {sec['name']}")
        md_lines.append(sec['content'])
        
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))
    print(f"[+] 마크다운 보고서 생성 완료: {output_md_path}")
    
    print("\n=== 주요 섹션 요약 ===")
    for sec in data['sections'][:4]:
        snippet = sec['content'][:120].replace('\n', ' ')
        print(f" - [{sec['name']}]: {snippet}...")

if __name__ == "__main__":
    main()

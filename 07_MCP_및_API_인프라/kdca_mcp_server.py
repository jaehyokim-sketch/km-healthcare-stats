"""
질병관리청(KDCA) 국가건강정보포털 통합 Open API FastMCP 서버
- 목록 검색 엔드포인트: https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchListApi.do
- 상세 뷰 엔드포인트: https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchViewApi.do
- 상세 XML 엔드포인트: http://api.kdca.go.kr/api/provide/healthInfo
- 인증 토큰: TOKEN=1a0cbb10c9d9
"""

import os
import sys
import json
import re
import xml.etree.ElementTree as ET
import requests
import ssl
from requests.adapters import HTTPAdapter
from mcp.server.fastmcp import FastMCP

# ── [SSL Compatibility Setup for Korean Public APIs] ──────────────────────────
class LegacySSLAdapter(HTTPAdapter):
    """
    OpenSSL 3.0+ 환경에서 공공기관 구형 TLS renegotiation 호환성을 보장하는 어댑터
    """
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

# ── [Create MCP Server] ────────────────────────────────────────────────────────
mcp = FastMCP("kdca-health-mcp")

# Default KDCA Credentials & Endpoints
DEFAULT_KDCA_TOKEN = "1a0cbb10c9d9"
DEFAULT_KDCA_SEARCH_LIST_ENDPOINT = "https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchListApi.do"
DEFAULT_KDCA_SEARCH_VIEW_ENDPOINT = "https://health.kdca.go.kr/healthinfo/openapi/svcNew/healthSearchViewApi.do"
DEFAULT_KDCA_XML_ENDPOINT = "http://api.kdca.go.kr/api/provide/healthInfo"

# KDCA 8대 대분류 카테고리 매핑
KDCA_LCLASS_MAP = {
    "": "전체",
    "1": "질병/증상",
    "2": "건강증진",
    "3": "치료",
    "4": "자가진단",
    "5": "생활습관",
    "6": "약물",
    "7": "진단/검사",
    "8": "응급처치/보건체계"
}

def _get_session() -> requests.Session:
    session = requests.Session()
    adapter = LegacySSLAdapter()
    session.mount('https://', adapter)
    session.mount('http://', adapter)
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    return session

def _get_token() -> str:
    return os.environ.get("KDCA_API_TOKEN", DEFAULT_KDCA_TOKEN)

def _get_search_list_endpoint() -> str:
    return os.environ.get("KDCA_SEARCH_LIST_ENDPOINT", DEFAULT_KDCA_SEARCH_LIST_ENDPOINT)

def _get_xml_endpoint() -> str:
    return os.environ.get("KDCA_HEALTH_ENDPOINT", DEFAULT_KDCA_XML_ENDPOINT)


@mcp.tool()
def search_kdca_health_list(
    srchWrd: str = "",
    lclasSn: str = "",
    pageIndex: int = 1,
    returnFormat: str = "json"
) -> str:
    """
    질병관리청(KDCA) 국가건강정보포털 건강정보 목록을 검색합니다.
    (질병/증상, 건강증진, 치료, 자가진단, 생활습관, 약물, 검사 등)

    :param srchWrd: 검색할 질환/증상/의료 키워드 (예: '난임', '치매', '감기', '당뇨', '재택의료')
    :param lclasSn: 대분류 번호 ('': 전체, '1': 질병/증상, '2': 건강증진, '3': 치료, '4': 자가진단, '5': 생활습관, '6': 약물, '7': 진단/검사, '8': 응급처치/보건체계)
    :param pageIndex: 페이지 번호 (기본값: 1)
    :param returnFormat: 반환 포맷 ('json' 또는 'markdown')
    :return: 검색 결과 목록 (콘텐츠 일련번호 cntntsSn, 제목 title, 대분류, 총 건수 등)
    """
    token = _get_token()
    endpoint = _get_search_list_endpoint()
    session = _get_session()

    data = {
        "TOKEN": token,
        "srchWrd": srchWrd,
        "lclasSn": lclasSn,
        "pageIndex": str(pageIndex)
    }

    try:
        res = session.post(endpoint, data=data, verify=False, timeout=15)
        res.raise_for_status()
        html = res.text

        # 콘텐츠 파싱: fn_goView('6753', '제목')
        matches = re.findall(r"fn_goView\s*\(\s*['\"]?(\d+)['\"]?\s*,\s*['\"]([^'\"]+)['\"]\s*\)", html)
        
        items = []
        for sn, title in matches:
            items.append({
                "cntntsSn": sn,
                "title": title.strip(),
                "lclasSn": lclasSn,
                "category": KDCA_LCLASS_MAP.get(lclasSn, "기타")
            })

        # 페이지네이션 파싱
        pages = re.findall(r"fn_submit\s*\(\s*['\"]?(\d+)['\"]?", html)
        total_pages = max([int(p) for p in pages] + [pageIndex]) if pages else pageIndex

        category_name = KDCA_LCLASS_MAP.get(lclasSn, "전체")

        if returnFormat.lower() == "markdown":
            md_lines = [
                f"# 🔍 [KDCA 국가건강정보] 검색 결과",
                f"- **검색어**: `{srchWrd if srchWrd else '(전체)'}`",
                f"- **분류**: `{category_name}` (코드: `{lclasSn if lclasSn else '전체'}`)",
                f"- **현재 페이지**: {pageIndex} / {total_pages}",
                f"- **검색 건수**: {len(items)}건",
                "\n---",
                "| 콘텐츠 ID (cntntsSn) | 제목 | 분류 | 상세 조회 명령 |",
                "| :--- | :--- | :--- | :--- |",
            ]
            if not items:
                md_lines.append("| - | *검색 결과가 없습니다.* | - | - |")
            else:
                for it in items:
                    md_lines.append(f"| `{it['cntntsSn']}` | **{it['title']}** | {it['category']} | `get_kdca_health_info(cntntsSn='{it['cntntsSn']}')` |")
            return "\n".join(md_lines)

        return json.dumps({
            "success": True,
            "keyword": srchWrd,
            "lclasSn": lclasSn,
            "category": category_name,
            "pageIndex": pageIndex,
            "totalPages": total_pages,
            "totalCount": len(items),
            "items": items
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"KDCA 검색 API 호출 실패: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def get_kdca_health_info(cntntsSn: str = "6753", returnFormat: str = "json") -> str:
    """
    질병관리청(KDCA) 국가건강정보포털 Open API를 호출하여 건강/질환/의료서비스 콘텐츠 상세 정보를 조회합니다.
    
    :param cntntsSn: 콘텐츠 일련번호 (기본값: '6753' - 재택의료/방문진료, '5423' - 감기 등)
    :param returnFormat: 반환 포맷 ('json' 또는 'markdown')
    :return: 콘텐츠 제목, 분류, 섹션별 상세 내용(개요, 정의, 원인, 증상, 진단, 치료, 수가/시범사업 세부내용, FAQ, 참고문헌)
    """
    token = _get_token()
    endpoint = _get_xml_endpoint()
    session = _get_session()
    
    url = f"{endpoint}?TOKEN={token}&cntntsSn={cntntsSn}"
    
    try:
        res = session.get(url, timeout=15)
        res.raise_for_status()
        
        # Parse XML Response
        root = ET.fromstring(res.text)
        code = root.findtext('.//CODE', default='')
        message = root.findtext('.//MESSAGE', default='')
        
        if code != 'S001':
            return json.dumps({
                "success": False,
                "code": code,
                "message": message or "KDCA API 응답 오류"
            }, ensure_ascii=False, indent=2)
            
        title = root.findtext('.//CNTNTSSJ', default='')
        sn = root.findtext('.//CNTNTS_SN', default=cntntsSn)
        lclass = root.findtext('.//LCLASSN', default='')
        category_name = KDCA_LCLASS_MAP.get(lclass, "기타")
        
        sections = []
        for cl in root.findall('.//cntntsCl'):
            sec_name = cl.findtext('CNTNTS_CL_NM', default='')
            sec_sn = cl.findtext('CNTNTSCLSN', default='')
            sec_content = cl.findtext('CNTNTS_CL_CN', default='')
            if sec_name or sec_content:
                sections.append({
                    "section_name": sec_name,
                    "section_sn": sec_sn,
                    "content": sec_content.strip() if sec_content else ""
                })
                
        if returnFormat.lower() == "markdown":
            md_lines = [
                f"# 🏥 [KDCA 국가건강정보] {title} (콘텐츠 ID: {sn})",
                f"- **응답 코드**: `{code}` ({message})",
                f"- **대분류**: `{category_name}` (분류번호: `{lclass}`)",
                f"- **출처**: 질병관리청 국가건강정보포털 Open API",
                "\n---",
            ]
            for sec in sections:
                md_lines.append(f"\n## 📌 {sec['section_name']}")
                md_lines.append(sec['content'])
            return "\n".join(md_lines)
            
        return json.dumps({
            "success": True,
            "code": code,
            "message": message,
            "title": title,
            "cntntsSn": sn,
            "lclass": lclass,
            "category": category_name,
            "total_sections": len(sections),
            "sections": sections
        }, ensure_ascii=False, indent=2)

    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"KDCA API 호출 및 파싱 실패: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool()
def search_and_get_kdca_info(srchWrd: str, returnFormat: str = "markdown") -> str:
    """
    질병관리청(KDCA) 국가건강정보에서 키워드를 검색한 뒤, 가장 연관성이 높은 첫 번째 콘텐츠의 상세 정보를 원스톱으로 반환합니다.

    :param srchWrd: 검색할 질환/증상 키워드 (예: '감기', '치매', '골다공증', '재택의료')
    :param returnFormat: 반환 포맷 ('markdown' 또는 'json')
    :return: 최우선 매칭 콘텐츠의 상세 정보
    """
    search_res_json = search_kdca_health_list(srchWrd=srchWrd, returnFormat="json")
    try:
        search_data = json.loads(search_res_json)
        if not search_data.get("success") or not search_data.get("items"):
            return f"❌ '{srchWrd}'에 대한 KDCA 국가건강정보 검색 결과가 존재하지 않습니다."
        
        top_item = search_data["items"][0]
        cntntsSn = top_item["cntntsSn"]
        return get_kdca_health_info(cntntsSn=cntntsSn, returnFormat=returnFormat)
    except Exception as e:
        return f"❌ 검색 및 상세 조회 처리 중 오류: {str(e)}"


@mcp.tool()
def get_kdca_categories() -> str:
    """
    질병관리청(KDCA) 국가건강정보포털의 8대 분류 코드 목록을 조회합니다.
    """
    categories = [
        {"lclasSn": k, "name": v} for k, v in KDCA_LCLASS_MAP.items() if k
    ]
    return json.dumps({
        "success": True,
        "description": "질병관리청 국가건강정보 8대 분류 카테고리",
        "categories": categories
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    print("Testing KDCA Open API MCP Tool...")
    print("1. Search Test ('감기'):")
    print(search_kdca_health_list(srchWrd="감기", returnFormat="markdown"))
    print("\n2. Detail Test ('6753'):")
    res = get_kdca_health_info(cntntsSn="6753", returnFormat="json")
    print(res[:400] + "...")
    print("\nStarting FastMCP Server...")
    mcp.run()

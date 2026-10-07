import os
import requests
import json
import urllib.parse
from mcp.server.fastmcp import FastMCP

# Create MCP server for HIRA Health Services
mcp = FastMCP("hira-health-mcp")

# Default API Key provided for HIRA Services
DEFAULT_HIRA_API_KEY = "e8U1shQ3d%2FByDVYStgfpaCdeSsJ1263%2BvNYAPjeZmPV5%2FxDHN6nqHk3EfqjlYZgrlpo5fYeXSSygjrNtRx5Reg%3D%3D"
HIRA_DISEASE_ENDPOINT = "https://apis.data.go.kr/B551182/diseaseInfoService1/getDissNameCodeList1"
HIRA_DETAIL_ENDPOINT = "https://apis.data.go.kr/B551182/MadmDtlInfoService2.8/getDtlInfo2.8"
HIRA_ADSC_DAMT_ENDPOINT = "https://apis.data.go.kr/B551182/adscDamtDmdAdmInqService1.1"
HIRA_MDFEE_ENDPOINT = "https://apis.data.go.kr/B551182/mdfeeCrtrInfoService"
HIRA_NON_PAYMENT_ENDPOINT = "https://apis.data.go.kr/B551182/nonPaymentDamtInfoService"

def _get_api_key():
    return os.environ.get("HIRA_API_KEY", DEFAULT_HIRA_API_KEY)

@mcp.tool()
def search_hira_disease_info(
    sickNm: str = "",
    sickCd: str = "",
    sickType: int = 1,
    medTp: int = 1,
    pageNo: int = 1,
    numOfRows: int = 50
) -> str:
    """
    건강보험심사평가원(HIRA) 질병정보서비스(diseaseInfoService1)를 통해 상병코드 및 질병명 목록을 조회합니다.
    
    :param sickNm: 상병명 검색어 (예: '요통', '관절염', '감기', '한방')
    :param sickCd: 상병코드 필터 (예: 'M54', 'K11', 'A00')
    :param sickType: 상병 구분 (1: 3단 상병코드, 2: 4단 상병코드)
    :param medTp: 진료과목/의과 구분 (1: 의과, 2: 치과 등)
    :param pageNo: 페이지 번호 (기본 1)
    :param numOfRows: 조회 건수 (기본 50, 최대 500)
    :return: 상병코드(sickCd), 질병명(sickNm), 영문 질병명(sickEngNm) 목록 JSON
    """
    api_key = _get_api_key()
    
    max_pages = 10 if (sickNm or sickCd) else 1
    matched_items = []
    total_count = 0

    for p in range(pageNo, pageNo + max_pages):
        url = f"{HIRA_DISEASE_ENDPOINT}?serviceKey={api_key}&sickType={sickType}&medTp={medTp}&pageNo={p}&numOfRows={numOfRows}&_type=json"
        
        try:
            res = requests.get(url, timeout=10)
            res.raise_for_status()
            data = res.json()
            
            body = data.get("response", {}).get("body", {})
            total_count = body.get("totalCount", total_count)
            items = body.get("items", {})
            
            if not items:
                break
                
            item_list = items.get("item", [])
            if isinstance(item_list, dict):
                item_list = [item_list]

            for item in item_list:
                cd = str(item.get("sickCd", ""))
                nm = str(item.get("sickNm", ""))
                eng = str(item.get("sickEngNm", ""))
                
                match_cd = not sickCd or sickCd.upper() in cd.upper()
                match_nm = not sickNm or sickNm in nm or sickNm.lower() in eng.lower()
                
                if match_cd and match_nm:
                    matched_items.append({
                        "sickCd": cd,
                        "sickNm": nm,
                        "sickEngNm": eng
                    })
                    
            if not (sickNm or sickCd) or len(matched_items) >= 50:
                break
                
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": f"API 호출 오류: {str(e)}"
            }, ensure_ascii=False, indent=2)

    return json.dumps({
        "success": True,
        "pageNo": pageNo,
        "numOfRows": numOfRows,
        "totalCount": len(matched_items) if (sickNm or sickCd) else total_count,
        "items": matched_items
    }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_hira_hospital_detail_info(
    ykiho: str = "",
    pageNo: int = 1,
    numOfRows: int = 10
) -> str:
    """
    건강보험심사평가원(HIRA) 의료기관별상세정보서비스(MadmDtlInfoService2.8)를 통해 
    특정 의료기관(요양기호 기준) 또는 의료기관 세부 현황 정보(주소, 전화번호, 시설, 인력 등)를 조회합니다.

    :param ykiho: 암호화된 요양기호 (특정 병의원 지정 시 입력)
    :param pageNo: 페이지 번호 (기본 1)
    :param numOfRows: 조회 건수 (기본 10)
    :return: 의료기관 상세 정보 JSON
    """
    api_key = _get_api_key()
    endpoint = os.environ.get("HIRA_DETAIL_ENDPOINT", HIRA_DETAIL_ENDPOINT)
    
    if not endpoint.endswith("getDtlInfo2.8"):
        endpoint = f"{endpoint.rstrip('/')}/getDtlInfo2.8"
        
    url = f"{endpoint}?serviceKey={api_key}&pageNo={pageNo}&numOfRows={numOfRows}&_type=json"
    if ykiho:
        url += f"&ykiho={ykiho}"
        
    try:
        res = requests.get(url, timeout=10)
        res.raise_for_status()
        data = res.json()
        
        body = data.get("response", {}).get("body", {})
        total_count = body.get("totalCount", 0)
        items = body.get("items", {})
        
        item_list = []
        if items:
            item_list = items.get("item", [])
            if isinstance(item_list, dict):
                item_list = [item_list]

        return json.dumps({
            "success": True,
            "pageNo": pageNo,
            "numOfRows": numOfRows,
            "totalCount": total_count,
            "items": item_list
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"API 호출 오류: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_hira_adsc_damt_info(
    operationName: str = "",
    ykiho: str = "",
    clCd: str = "",
    pageNo: int = 1,
    numOfRows: int = 10,
    extraParamsJson: str = "{}"
) -> str:
    """
    건강보험심사평가원(HIRA) 가산금액 청구관리 정보 조회 서비스(adscDamtDmdAdmInqService1.1)를 조회합니다.

    :param operationName: 세부 오퍼레이션 명칭 (생략 시 기본 엔드포인트 URL 호출)
    :param ykiho: 암호화된 요양기호
    :param clCd: 종별코드 (예: 21 병원, 31 의원, 92 한의원 등)
    :param pageNo: 페이지 번호 (기본 1)
    :param numOfRows: 조회 건수 (기본 10)
    :param extraParamsJson: 추가 요청 파라미터 JSON 문자열 (예: '{"stdrYm": "202401"}')
    :return: 조회 결과 JSON
    """
    api_key = _get_api_key()
    base_endpoint = os.environ.get("HIRA_ADSC_DAMT_ENDPOINT", HIRA_ADSC_DAMT_ENDPOINT).rstrip('/')
    
    endpoint = f"{base_endpoint}/{operationName}" if operationName else base_endpoint
    
    params = {
        "serviceKey": urllib.parse.unquote(api_key),
        "pageNo": pageNo,
        "numOfRows": numOfRows,
        "_type": "json"
    }
    if ykiho:
        params["ykiho"] = ykiho
    if clCd:
        params["clCd"] = clCd
        
    if extraParamsJson:
        try:
            extra = json.loads(extraParamsJson)
            if isinstance(extra, dict):
                params.update(extra)
        except Exception:
            pass
            
    try:
        res = requests.get(endpoint, params=params, timeout=10)
        res.raise_for_status()
        
        try:
            data = res.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({
                "success": True,
                "status_code": res.status_code,
                "raw_text": res.text
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"API 호출 오류: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_hira_mdfee_crtr_info(
    operationName: str = "",
    feeCd: str = "",
    feeNm: str = "",
    pageNo: int = 1,
    numOfRows: int = 10,
    extraParamsJson: str = "{}"
) -> str:
    """
    건강보험심사평가원(HIRA) 수가기준정보서비스(mdfeeCrtrInfoService)를 조회합니다.
    행위수가코드, 한방수가, 약국/진료 수가 기준정보 및 심사 기준을 확인할 수 있습니다.

    :param operationName: 세부 오퍼레이션 명칭 (생략 시 기본 엔드포인트 URL 호출)
    :param feeCd: 의료수가코드 (예: 침술, 첩약, 진찰료 수가코드 등)
    :param feeNm: 의료수가코드명 검색어 (예: '침술', '구술', '부항')
    :param pageNo: 페이지 번호 (기본 1)
    :param numOfRows: 조회 건수 (기본 10)
    :param extraParamsJson: 추가 요청 파라미터 JSON 문자열
    :return: 수가기준정보 조회 결과 JSON
    """
    api_key = _get_api_key()
    base_endpoint = os.environ.get("HIRA_MDFEE_ENDPOINT", HIRA_MDFEE_ENDPOINT).rstrip('/')
    
    endpoint = f"{base_endpoint}/{operationName}" if operationName else base_endpoint
    
    params = {
        "serviceKey": urllib.parse.unquote(api_key),
        "pageNo": pageNo,
        "numOfRows": numOfRows,
        "_type": "json"
    }
    if feeCd:
        params["mdfeeCd"] = feeCd
    if feeNm:
        params["mdfeeNm"] = feeNm
        
    if extraParamsJson:
        try:
            extra = json.loads(extraParamsJson)
            if isinstance(extra, dict):
                params.update(extra)
        except Exception:
            pass
            
    try:
        res = requests.get(endpoint, params=params, timeout=10)
        res.raise_for_status()
        
        try:
            data = res.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({
                "success": True,
                "status_code": res.status_code,
                "raw_text": res.text
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"API 호출 오류: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool()
def get_hira_non_payment_damt_info(
    operationName: str = "getNonPaymentItemCodeList",
    itemCd: str = "",
    ykiho: str = "",
    clCd: str = "",
    sidoCd: str = "",
    sgguCd: str = "",
    pageNo: int = 1,
    numOfRows: int = 10,
    extraParamsJson: str = "{}"
) -> str:
    """
    건강보험심사평가원(HIRA) 비급여진료비정보서비스(nonPaymentDamtInfoService)를 조회합니다.
    비급여 항목 코드 목록, 의료기관별 비급여 진료비용 및 항목 상세 정보를 확인할 수 있습니다.

    :param operationName: 오퍼레이션 명칭 (기본값: 'getNonPaymentItemCodeList', 병원목록: 'getNonPaymentItemHospList', 상세: 'getNonPaymentItemHospDtlList')
    :param itemCd: 비급여 항목코드/분류코드
    :param ykiho: 암호화된 요양기호 (특정 병의원 지정 시)
    :param clCd: 종별코드 (예: 01 상급종합, 11 종합병원, 21 병원, 31 의원, 92 한의원 등)
    :param sidoCd: 시도코드 (예: 11 서울, 35 전북, 31 경기 등)
    :param sgguCd: 시군구코드
    :param pageNo: 페이지 번호 (기본 1)
    :param numOfRows: 조회 건수 (기본 10)
    :param extraParamsJson: 추가 요청 파라미터 JSON 문자열
    :return: 비급여 진료비 정보 JSON
    """
    api_key = _get_api_key()
    base_endpoint = os.environ.get("HIRA_NON_PAYMENT_ENDPOINT", HIRA_NON_PAYMENT_ENDPOINT).rstrip('/')
    
    endpoint = f"{base_endpoint}/{operationName}" if operationName else base_endpoint
    
    params = {
        "serviceKey": urllib.parse.unquote(api_key),
        "pageNo": pageNo,
        "numOfRows": numOfRows,
        "_type": "json"
    }
    if itemCd:
        params["itemCd"] = itemCd
    if ykiho:
        params["ykiho"] = ykiho
    if clCd:
        params["clCd"] = clCd
    if sidoCd:
        params["sidoCd"] = sidoCd
    if sgguCd:
        params["sgguCd"] = sgguCd
        
    if extraParamsJson:
        try:
            extra = json.loads(extraParamsJson)
            if isinstance(extra, dict):
                params.update(extra)
        except Exception:
            pass
            
    try:
        res = requests.get(endpoint, params=params, timeout=10)
        res.raise_for_status()
        
        try:
            data = res.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
        except Exception:
            return json.dumps({
                "success": True,
                "status_code": res.status_code,
                "raw_text": res.text
            }, ensure_ascii=False, indent=2)
            
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"API 호출 오류: {str(e)}"
        }, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    mcp.run()

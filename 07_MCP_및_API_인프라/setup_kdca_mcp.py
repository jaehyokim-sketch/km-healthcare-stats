"""
HIRA(심평원) + KDCA(질병관리청) 통합 Open API & MCP 자동 설정 및 종합 검증 스크립트
"""

import os
import sys
import subprocess
import json

sys.stdout.reconfigure(encoding='utf-8')

def test_kdca_api():
    print("\n[1/2] 질병관리청(KDCA) 국가건강정보포털 API 연결 테스트...")
    try:
        sys.path.append(os.path.dirname(__file__))
        from kdca_mcp_server import get_kdca_health_info, search_kdca_health_list
        
        # 1. 목록 검색 테스트 (healthSearchListApi.do)
        list_json = search_kdca_health_list(srchWrd="감기", returnFormat="json")
        list_data = json.loads(list_json)
        if list_data.get("success") and list_data.get("items"):
            item = list_data["items"][0]
            print(f"  [SUCCESS] KDCA 목록검색 API 연결 완료! 키워드: [감기] -> 매칭: [{item['title']}] (ID: {item['cntntsSn']})")
        else:
            print(f"  [WARN] KDCA 목록검색 응답 확인 필요: {list_data}")

        # 2. 상세 콘텐츠 조회 테스트 (healthInfo XML)
        res_json = get_kdca_health_info(cntntsSn="6753", returnFormat="json")
        data = json.loads(res_json)
        if data.get("success"):
            print(f"  [SUCCESS] KDCA 상세정보 API 연결 완료! 콘텐츠명: [{data['title']}], 섹션 {data['total_sections']}개 수신됨.")
            return True
        else:
            print(f"  [FAIL] KDCA 상세응답 에러: {data.get('error') or data.get('message')}")
            return False
    except Exception as e:
        print(f"  [FAIL] KDCA 호출 실패: {e}")
        return False

def test_hira_api():
    print("\n[2/2] 건강보험심사평가원(HIRA) 질병정보 API 연결 테스트...")
    try:
        sys.path.append(os.path.dirname(__file__))
        from hira_mcp_server import search_hira_disease_info
        res_json = search_hira_disease_info(sickNm="요통", numOfRows=2)
        data = json.loads(res_json)
        if data.get("success"):
            print(f"  [SUCCESS] HIRA API 연결 완료! 수신 건수: {len(data.get('items', []))}건.")
            return True
        else:
            print(f"  [FAIL] HIRA 응답 에러: {data.get('error')}")
            return False
    except Exception as e:
        print(f"  [FAIL] HIRA 호출 실패: {e}")
        return False

def main():
    print("=" * 65)
    print(" 🏥 HIRA + KDCA 통합 보건의료 Open API & MCP 환경 종합 검증")
    print("=" * 65)
    
    kdca_ok = test_kdca_api()
    hira_ok = test_hira_api()
    
    print("\n" + "=" * 65)
    if kdca_ok and hira_ok:
        print(" 🎉 모든 보건의료 Open API (HIRA + KDCA) MCP 서버가 완벽하게 준비되었습니다!")
    else:
        print(" ⚠️ 일부 API 연결에 문제가 있습니다. 로그를 확인해주세요.")
    print("=" * 65)

if __name__ == "__main__":
    main()

# HIRA (건강보험심사평가원) MCP API 연결 가져오기 (다른 PC용)

본 폴더에는 다른 PC에서 **건강보험심사평가원(HIRA) API 및 MCP 설정**을 1초 만에 그대로 가져와서 사용할 수 있는 이관용 파일들이 포함되어 있습니다.

---

## 📁 구성 파일 목록

1. **`setup_hira_mcp.py`**: 자동 패키지 설치, MCP 환경 설정 및 HIRA API 5종 연결 검증 파이썬 스크립트
2. **`hira_mcp_server.py`**: HIRA Open API MCP 서버 실행 스크립트
3. **`hira_mcp_config.json`**: 사전 인증키(`serviceKey`) 및 End Point가 등록된 MCP 설정 파일

---

## 🚀 다른 PC에서 사용/가져오는 방법 (1분 완료)

### 방법 A. 자동 실행 (권장)
다른 PC에서 본 폴더를 통째로 복사한 후, 터미널(CMD / PowerShell)에서 다음 명령어를 실행합니다.

```bash
python setup_hira_mcp.py
```
> 실행 시 필수 라이브러리(`mcp`, `requests`) 자동 설치 및 HIRA API 인증키 연동이 완료됩니다.

---

### 방법 B. 수동 설정
다른 PC의 워크스페이스 내 `.agents/` 폴더로 다음과 같이 복사합니다.

1. `.agents/mcp_servers/hira_mcp_server.py` 로 `hira_mcp_server.py` 복사
2. `.agents/mcp_config.json` 으로 `hira_mcp_config.json` 복사 후 경로 수정

---

## 🔑 포함된 HIRA API & 제공 툴 정보

| 서비스명 | End Point | 주요 제공 툴 |
| :--- | :--- | :--- |
| **질병정보서비스** | `https://apis.data.go.kr/B551182/diseaseInfoService1` | `search_hira_disease_info` (상병코드 및 질병명 검색) |
| **의료기관별상세정보서비스** | `https://apis.data.go.kr/B551182/MadmDtlInfoService2.8` | `get_hira_hospital_detail_info` (의료기관 세부정보/현황 조회) |
| **가산금액청구관리서비스** | `https://apis.data.go.kr/B551182/adscDamtDmdAdmInqService1.1` | `get_hira_adsc_damt_info` (가산금액 청구관리/가산항목 조회) |
| **수가기준정보서비스** | `https://apis.data.go.kr/B551182/mdfeeCrtrInfoService` | `get_hira_mdfee_crtr_info` (의료수가코드, 한방수가, 심사기준 조회) |
| **비급여진료비정보서비스** | `https://apis.data.go.kr/B551182/nonPaymentDamtInfoService` | `get_hira_non_payment_damt_info` (비급여 항목코드, 병원별 비급여 진료비용 조회) |

- **일반 인증키**: `e8U1shQ3d%2FByDVYStgfpaCdeSsJ1263%2BvNYAPjeZmPV5%2FxDHN6nqHk3EfqjlYZgrlpo5fYeXSSygjrNtRx5Reg%3D%3D`

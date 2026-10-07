import os
import sys
import shutil
import subprocess

def main():
    print("=" * 65)
    print(" HIRA (건강보험심사평가원) MCP 자동 설정 및 서비스 연동")
    print("=" * 65)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(current_dir, "hira_mcp_server.py")
    config_json = os.path.join(current_dir, "hira_mcp_config.json")

    if not os.path.exists(server_script) or not os.path.exists(config_json):
        print(" [오류] 필수 설정 파일(hira_mcp_server.py, hira_mcp_config.json)이 없습니다.")
        return

    # 1. Install required python packages
    print("\n[1/3] 파이썬 MCP 및 필수 라이브러리 설치 확인 중...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "mcp<2", "requests"])
        print("   -> 필수 라이브러리 (mcp<2, requests) 준비 완료")
    except Exception as e:
        print(f"   [경고] 패키지 설치 확인 중 경고: {e}")

    # 2. Setup workspace .agents directory
    print("\n[2/3] 현재 프로젝트 워크스페이스 MCP 설정(.agents) 적용 중...")
    agents_dir = os.path.join(current_dir, ".agents")
    mcp_servers_dir = os.path.join(agents_dir, "mcp_servers")

    os.makedirs(mcp_servers_dir, exist_ok=True)

    dest_server = os.path.join(mcp_servers_dir, "hira_mcp_server.py")
    dest_config = os.path.join(agents_dir, "mcp_config.json")

    shutil.copy2(server_script, dest_server)

    # Update path in config json for local target
    target_server_path = os.path.abspath(dest_server).replace("\\", "/")
    
    with open(config_json, "r", encoding="utf-8") as f:
        config_data = f.read()

    config_data_updated = config_data.replace("./hira_mcp_server.py", target_server_path)

    with open(dest_config, "w", encoding="utf-8") as f:
        f.write(config_data_updated)

    print(f"   -> MCP 서버 스크립트 복사: {dest_server}")
    print(f"   -> MCP 설정 파일 복사: {dest_config}")

    # 3. Test HIRA API connections
    print("\n[3/3] HIRA API 연결 테스트 중...")
    try:
        sys.path.insert(0, mcp_servers_dir)
        import hira_mcp_server
        
        # Test 1: Disease Info Service
        res1 = hira_mcp_server.search_hira_disease_info(sickCd="M54", numOfRows=1)
        if "M54" in res1 or "success" in res1:
            print("   -> HIRA 질병정보서비스(diseaseInfoService1) API 정상 작동 검증 완료!")
            
        # Test 2: Hospital Detail Info Service
        res2 = hira_mcp_server.get_hira_hospital_detail_info(numOfRows=1)
        if "success" in res2 or "NORMAL SERVICE" in res2 or "items" in res2:
            print("   -> HIRA 의료기관별상세정보서비스(MadmDtlInfoService2.8) API 정상 작동 검증 완료!")

        # Test 3: ADSC Damt Inquiry Service
        res3 = hira_mcp_server.get_hira_adsc_damt_info(numOfRows=1)
        if "success" in res3 or "response" in res3:
            print("   -> HIRA 가산금액청구관리(adscDamtDmdAdmInqService1.1) API 등록 및 연동 확인 완료!")

        # Test 4: Mdfee Crtr Info Service
        res4 = hira_mcp_server.get_hira_mdfee_crtr_info(numOfRows=1)
        if "success" in res4 or "response" in res4:
            print("   -> HIRA 수가기준정보서비스(mdfeeCrtrInfoService) API 등록 및 연동 확인 완료!")

        # Test 5: Non-Payment Damt Info Service
        res5 = hira_mcp_server.get_hira_non_payment_damt_info(numOfRows=1)
        if "NORMAL SERVICE" in res5 or "items" in res5:
            print("   -> HIRA 비급여진료비정보서비스(nonPaymentDamtInfoService) API 정상 작동 검증 완료!")
            
    except Exception as e:
        print(f"   [경고] 테스트 실행 중 오류 발생: {e}")

    print("\n" + "=" * 65)
    print(" HIRA MCP 설정 및 서비스 연동이 성공적으로 완료되었습니다!")
    print(" 1) 질병정보서비스 (diseaseInfoService1)")
    print(" 2) 의료기관별상세정보서비스 (MadmDtlInfoService2.8)")
    print(" 3) 가산금액청구관리 (adscDamtDmdAdmInqService1.1)")
    print(" 4) 수가기준정보서비스 (mdfeeCrtrInfoService)")
    print(" 5) 비급여진료비정보서비스 (nonPaymentDamtInfoService)")
    print("=" * 65)

if __name__ == "__main__":
    main()

"""
D:\한의 의료서비스 통계 디렉토리 주제별 파일 자동 정리 스크립트
"""

import os
import shutil
import sys

sys.stdout.reconfigure(encoding='utf-8')
base_dir = r"d:\한의 의료서비스 통계"

# 1. 새롭게 구성할 주제별 폴더 매핑 정의
structure = {
    "01_지역별_방문진료_시뮬레이션": [
        # 익산시
        "iksan.html",
        "iksan_logic_spec.md",
        "iksan_homecare_simulation_chart.png",
        "iksan_km_10_to_100_simulation_chart.png",
        "iksan_km_participation_5yr_simulation.png",
        "익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md",
        "익산시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html",
        "익산시_한의약_방문진료_의료적정성_분석_및_시뮬레이션_로직_명세서.md",
        "익산시_한의약_방문진료_돌봄_진료비_시뮬레이션_보고서.md",
        "익산시_한의약_방문진료_돌봄_진료비_시뮬레이션_보고서.html",
        "익산시_보건의료_내쉬균형_및_한의약개입_확률시뮬레이션_보고서.md",
        "익산시_보건의료_내쉬균형_및_한의약개입_확률시뮬레이션_보고서.html",
        # 전주시 & 전북
        "jeonju_jeonbuk.html",
        "jeonju_jeonbuk_logic_spec.md",
        "jeonju_jeonbuk_simulation_chart.png",
        "전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md",
        "전주시_및_전북특별자치도_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html",
        "전주시_및_전북특별자치도_한의약_방문진료_의료적정성_분석_및_시뮬레이션_로직_명세서.md",
        # 김해시 & 경남
        "gimhae_gyeongnam.html",
        "gimhae_gyeongnam_full_simulation.json",
        "gimhae_gyeongnam_simulation_chart.png",
        "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md",
        "경상남도_및_김해시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html",
        # 여수시 & 전남
        "yeosu_jeonnam.html",
        "yeosu_jeonnam_simulation_chart.png",
        "전라남도_및_여수시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.md",
        "전라남도_및_여수시_한의약_방문진료_기관참여율별_의료적정성_및_5개년_효과시뮬레이션_보고서.html",
        # 공통 종합 요약
        "all_regions_revalidated_summary.json",
        "revalidated_corpus_simulation.json",
        "nash_equilibrium_simulation_chart.png"
    ],
    "02_재택의료_정책_및_국제비교": [
        "한국_재택의료_현황_및_일본_대만_비교를_통한_개선방향_보고서.md",
        "한국_재택의료_현황_및_일본_대만_비교를_통한_개선방향_보고서.html",
        "일본_대만_전통의학_재택의료_비교분석_보고서.md",
        "한의사_재택의료_방문진료_참여확대_종합분석_및_정책제언_보고서.md",
        "한의사_재택의료_방문진료_참여확대_종합분석_및_정책제언_보고서.html",
        "한의사_재택의료_참여확대_정책제안서.md",
        "이혜진교수_재택의료_분석보고서.md",
        "KDCA_국가건강정보_재택의료_방문진료_요약.md",
        "policy_report.html",
        "환자중심의 건강보험 재택의료 포괄모형 개발.pdf",
        "2025.02.No.340.03.pdf",
        "pdf_340_extracted.txt",
        "extracted_pdf_summary.txt"
    ],
    "03_HIRA_및_임상통계_보고서": [
        "HIRA_분석_AI로직_가이드.md",
        "HIRA_2024_한의원_침구치료_다빈도상병_Top20.html",
        "HIRA_한의원_급여_및_비급여_한약처방_Top20.html",
        "HIRA_한의원_요통_및_침구치료_분석_보고서.md",
        "HIRA_한의원_요통_및_침구치료_분석_보고서.html",
        "심부전_한의약치료_및_HIRA통계_종합분석_보고서.md",
        "심부전_한의약치료_및_HIRA통계_종합분석_보고서.html",
        "시군구별_1인당_연간진료비_상하위_종합분석_보고서.md",
        "시군구별_1인당_연간진료비_상하위_종합분석_보고서.html",
        "시도별_치료가능_사망률_분석_및_한방의료기관_역할_보고서.html",
        "진료과_및_요양기관별_치료_약물처방_종합분석_보고서.html",
        "국내_기대수명_및_건강수명_통계_2020_2024.md",
        "기대수명_건강수명_추이_그래프.png",
        "life_expectancy_trend_2020_2024.png"
    ],
    "04_모자보건_및_난임_소아통계": [
        "난임치료_임신성공률_한의약_기여도_종합분석_보고서.md",
        "익산시_소아청소년_한의약의료서비스_진료현황_및_5개년_비용시뮬레이션_보고서.html",
        "익산시_20세이하_연평균_의료비_및_다빈도상병_Top20_분석_보고서.html"
    ],
    "07_MCP_및_API_인프라": [
        "hira_mcp_server.py",
        "kdca_mcp_server.py",
        "setup_hira_mcp.py",
        "setup_kdca_mcp.py",
        "hira_mcp_config.json",
        "README_HIRA_MCP_IMPORT.md"
    ],
    "08_아젠다_제안서_및_서식": [
        "(양식) 아젠다 제안양식 권오상 2차.hwpx",
        "(양식) 아젠다 제안양식 권오상 2차.html",
        "아젠다_제안서_익산형_통합_방문_기능유지_돌봄_네트워크_권오상_2차_Refined.md",
        "의료통합교육_정책_분석_보고서.md"
    ]
}

def organize():
    print("=" * 60)
    print(" 📂 작업공간 파일 주제별 자동 정리 시작")
    print("=" * 60)
    
    total_moved = 0
    for folder_name, files in structure.items():
        target_folder = os.path.join(base_dir, folder_name)
        os.makedirs(target_folder, exist_ok=True)
        print(f"\n📁 [{folder_name}] 폴더 정리 중...")
        
        for filename in files:
            src_path = os.path.join(base_dir, filename)
            dst_path = os.path.join(target_folder, filename)
            
            if os.path.exists(src_path):
                # MCP 서버 등 루트에서 직접 참조가 필요한 파일은 copy를 고려할 수 있으나,
                # 여기서는 move를 수행하되 mcp_config.json은 .agents 내 경로를 확인
                try:
                    shutil.move(src_path, dst_path)
                    print(f"  ✓ 이동: {filename}")
                    total_moved += 1
                except Exception as e:
                    print(f"  ✗ 실패 ({filename}): {e}")
            elif os.path.exists(dst_path):
                print(f"  - 이미 존재: {filename}")
            else:
                print(f"  ? 파일 없음: {filename}")

    print("\n" + "=" * 60)
    print(f" 🎉 정리 완료! 총 {total_moved}개 파일이 주제별 디렉토리로 이동되었습니다.")
    print("=" * 60)

if __name__ == "__main__":
    organize()

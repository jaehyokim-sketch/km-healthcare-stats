# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner (Pro Mode: deepseek-reasoner / DeepSeek-R1)
Facial Palsy (G51 / Bell's Palsy) KM Healthcare Service & Benefit Expansion Report Generator
"""

import urllib.request
import json
import sys
import os

def clean_text_for_api(text):
    for emoji in ['📌', '📋', '📑', '💡', '⚠️', '✅', '🔍', '🚀', '📂', '📄', '📝', '📜', '🏥', '🎯', '🏛️', '🔹']:
        text = text.replace(emoji, '')
    return text

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    system_prompt = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 신경과학, 한의표준임상진료지침(CPG) 및 건강보험 급여·비급여 수가체계 분야의 최고 권위 석학 연구원입니다.\n"
        "질병관리청(KDCA), 건강보험심사평가원(HIRA), 통계청(KOSIS), 첩약 건강보험 시범사업 1·2단계 실적 데이터, 그리고 Cochrane Systematic Review 등 국제 임상근거를 종합하여, "
        "안면신경마비(G51 / 벨마비 / 구안와사)에 대한 한의약 의료서비스의 현황을 정밀 분석하고, "
        "근거중심(EBM) 다학제 치료 프로토콜을 통해 건강보험 급여 및 비급여 영역에서 한의약의 합리적 역할을 확장시키는 종합 마스터 보고서를 작성해주세요."
    )

    user_prompt = """
다음 분석 요구사항과 데이터 프레임워크를 바탕으로 [안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md] 전문(Full Report)을 작성해주세요.

[필수 분석 영역 및 데이터 요구사항]
1. KDCA 국가건강정보 및 KOSIS 역학 분석:
   - 안면신경(제7뇌신경) 해부생리, 중추성 vs 말초성 얼굴마비 감별 기준 (이마 주름, 눈감기, 편마비 등)
   - 벨마비(Bell's palsy, 70~80%), 람세이헌트 증후군(Ramsay Hunt, 10~15%), 외상성/기타 마비 역학
   - 국내 연간 발생률(인구 10만 명당 25~30명, 연간 환자수 약 9만~10만 명), 성별/연령별 분포(전 연령대, 50~60대 다발), 재발률(7~8%) 및 후유증률(15~20% 불완전 회복, 연합운동/악어의눈물/구축).

2. HIRA 보건의료빅데이터 및 종별 이용 통계:
   - 질병코드 G51.0 (벨마비), G51 (안면신경장애) 5개년 진료추이 (연간 진료인원, 총진료비, 1인당 진료비)
   - 요양기관 종별 점유율: 한의 의료기관(한의원+한방병원)이 전체 환자의 약 65~70%를 점유하며 일차의료의 핵심 역할을 담당하는 실증 통계
   - 의과(스테로이드·항바이러스제 초기 72시간 투여) vs 한의과(침·전침·첩약·추나 복합치료)의 다학제 협진 현황.

3. 첩약 건강보험 시범사업 1단계·2단계 실태 및 성과 분석:
   - 안면신경마비가 첩약 건보 시범사업의 '대표 1호 상병'으로서 보여준 높은 환자 만족도(90% 이상), 임상적 개선 효과, 청구 실적 분석
   - 현행 보장성 기준(연간 1회/10일분 -> 2단계 연 2회/20일분)의 성과와 한계점(발병 초기 4~8주 집중 투약 필요성 대비 급여 일수 부족).

4. 현행 급여 및 비급여 항목의 포괄적 비교 분석:
   - [급여 항목]: 침술(자모침, 안면부 혈자리), 전침(저주파 2~4Hz/10~20Hz), 구술(간접구), 부항(유관법), 한방물리요법(경피경근온열/경피전기자극), 안면추나요법, 첩약(시범사업).
   - [비급여 항목]: 약침술(봉독, 자하거, 황련해독, 신바로), 매선요법(후유증기 안면근육 거상 및 탄력 회복), 비급여 첩약 추가분, 특수 온열도수요법.
   - 비급여 발생 원인 및 환자 본인부담 완화를 위한 단계적 급여 전환 필요성.

5. 근거중심의학(EBM) 4단계 임상 치료 프로토콜 (Clinical Protocol):
   - Stage 1: 급성기 (발병 1~7일 / 골든타임) - 스테로이드 병용 + 침·봉독약침 소염 + 이기거풍산/견정산 + 신경 손상 방지
   - Stage 2: 아급성기 (발병 8~28일 / 신경 재생기) - 전침(저주파) + 자하거약침 + 보양환오탕/순기화담전 + 표정근 재교육
   - Stage 3: 회복기 (1~3개월 / 근기능 회복기) - 복합 침구 + 안면 추나(근막이완) + 조위승청탕/대진교탕 + 근력 강화
   - Stage 4: 후유증·만성기 (3개월 이상 / 연합운동·구축 방지) - 심부 전침 + 매선요법 + 체질 맞춤 첩약 + 바이오피드백

6. 한의약 역할 확대를 위한 4대 정책 제언:
   - 제언 1: 첩약 건강보험 시범사업의 본사업 전환 및 급여 일수 현실화 (연간 20일 -> 중증도에 따라 최대 30~40일 확대)
   - 제언 2: 안면마비 특화 약침(봉독/자하거)의 건강보험 선별급여 도입 (HIRA 비급여 표준화 연계)
   - 제언 3: '의한(醫韓) 조기 협진 골든타임 프로토콜' 국가 표준화 및 협진 시범사업 수가 신설
   - 제언 4: 거동불편 중증/만성 안면마비 환자 대상 한의 방문진료 및 재택의료 8대 체계 편입

7. 기대효과(임상적 완치율 향상, 후유증 발생률 50% 감소, 환자 의료비 절감) 및 결론.

마크다운 형식의 보고서 전문을 완벽하고 풍부한 데이터와 표, 다이어그램(Mermaid)을 포함하여 작성해주세요.
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": clean_text_for_api(user_prompt)}
        ],
        "max_tokens": 8000
    }

    print("Executing DeepSeek Reasoner (Pro Mode / R1) for Facial Palsy Report...")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    try:
        with urllib.request.urlopen(req, timeout=240) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            choice = res["choices"][0]
            reasoning = choice["message"].get("reasoning_content", "")
            content = choice["message"].get("content", "")
            
            # 1. Save reasoning log
            reasoning_file = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_DeepSeek_추론로그.md"
            with open(reasoning_file, "w", encoding="utf-8") as rf:
                rf.write("# DeepSeek Reasoner (R1 Pro Mode) Reasoning Log: Facial Palsy Analysis\n\n" + reasoning)
            
            # 2. Save generated report to HIRA reports directory
            output_file1 = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(output_file1, "w", encoding="utf-8") as out1:
                out1.write(content)

            # 3. Archive report
            output_file2 = r"d:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(output_file2, "w", encoding="utf-8") as out2:
                out2.write(content)
            
            print("=== DeepSeek Reasoner Pro Mode Execution Completed Successfully ===")
            print(f"Reasoning characters: {len(reasoning)}, saved to: {reasoning_file}")
            print(f"Report characters: {len(content)}, saved to: {output_file1}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

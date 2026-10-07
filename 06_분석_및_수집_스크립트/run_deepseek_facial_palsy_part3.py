# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner Continuation Script (Part 3)
Completes Section 5.3 through Section 11 concisely and thoroughly, then performs final merge.
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
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 신경과학, 한의표준임상진료지침(CPG) 및 건강보험 수가체계 최고 권위 연구원입니다.\n"
        "제5장 5.3절(환자 만족도 및 증상개선 성과)부터 시작하여, 제6장(급여·비급여 비교), 제7장(4단계 EBM 치료프로토콜), "
        "제8장(4대 정책제언), 제9장(기대효과), 제10장(결론), 제11장(참고문헌)까지를 완벽하고 완성도 높은 마크다운 보고서로 작성해주세요."
    )

    user_prompt = """
다음 목차에 맞춰 제5장 5.3절 이하부터 보고서의 마지막까지 완결된 형태로 작성해주세요:

### 5.3 환자 만족도 및 증상 개선 성과 (이어서 작성)
- 종합 만족도 92.4% 해석 및 H-B Grade 개선 효과 (평균 1.94등급 개선, 증상 호전율 87.6%)
### 5.4 현행 급여 기준의 한계점과 개선 필요성
- 2단계 연 2회/20일분 한계와 발병 초기 4~8주 집중 투약 치료창(therapeutic window) 필요성

## 제6장 급여·비급여 항목 포괄 비교 분석
- 6.1 급여 항목 (침술, 전침, 구술, 부항, 한방물리요법, 안면추나요법, 첩약시범사업)
- 6.2 비급여 항목 (봉독·자하거 약침술, 매선요법, 비급여 첩약 추가분)
- 6.3 급여 vs 비급여 종합 비교 매트릭스 표 (항목명, 수가/비용, 임상 목적, 비급여 원인 및 개선 방향)

## 제7장 근거중심의학(EBM) 4단계 임상 치료 프로토콜
- Stage 1: 급성기 (발병 1~7일) - 스테로이드 병용 + 침·봉독약침 + 이기거풍산/견정산 + 신경 손상 억제 (근거수준 B, 권고등급 A)
- Stage 2: 아급성기 (발병 8~28일) - 전침(저주파) + 자하거약침 + 보양환오탕/순기화담전 + 안면근육 재교육 (근거수준 A, 권고등급 A)
- Stage 3: 회복기 (1~3개월) - 복합 침구 + 안면 추나 + 대진교탕/조위승청탕 + 근력 강화 (근거수준 B, 권고등급 B)
- Stage 4: 후유증·만성기 (3개월 이상) - 심부 전침 + 매선요법 + 체질한약 + 연합운동/구축 방지 (근거수준 B, 권고등급 B)
- 4단계 요약 프로토콜 매트릭스 표 및 다이어그램

## 제8장 한의약 역할 확대를 위한 4대 정책 제언
- 제언 1: 첩약 건강보험 본사업 전환 및 급여 일수 현실화 (연 20일 -> 중증도별 30~40일)
- 제언 2: 안면마비 특화 약침(봉독/자하거) 건강보험 선별급여 도입
- 제언 3: '의한(醫韓) 조기 협진 골든타임 프로토콜' 국가 표준화 및 협진 관리료 신설
- 제언 4: 거동불편/중증 환자 대상 한의 방문진료 및 KDCA 8대 재택의료 체계 연계

## 제9장 기대효과 분석
- 임상적 완치율 향상 (H-B I~II 도달률 71% -> 85%), 후유증 발생률 50% 감소
- 환자 1인당 의료비 15~25% 절감 및 건보재정 효율화

## 제10장 결론 및 향후 과제
## 제11장 참고문헌 (KDCA, HIRA, Cochrane, CPG 등)
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": clean_text_for_api(user_prompt)}
        ],
        "max_tokens": 8000
    }

    print("Executing DeepSeek Reasoner for Facial Palsy Report (Part 3 Final Completion)...")
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
            
            part12_file = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(part12_file, "r", encoding="utf-8") as f:
                current_text = f.read()

            # Cut current text at the end of section 5.3 table
            pos = current_text.find("- **종합")
            if pos != -1:
                clean_base = current_text[:pos]
            else:
                clean_base = current_text
                
            final_report = clean_base.strip() + "\n\n" + content.strip()
            
            # Save final merged report
            with open(part12_file, "w", encoding="utf-8") as out1:
                out1.write(final_report)

            archive_file = r"d:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(archive_file, "w", encoding="utf-8") as out2:
                out2.write(final_report)

            print("=== DeepSeek Reasoner Final Completion Completed Successfully ===")
            print(f"Final Merged Report Length: {len(final_report)} chars, saved to: {part12_file}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

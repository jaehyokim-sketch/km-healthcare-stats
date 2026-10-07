# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner (Pro Mode) Continuation Script for Facial Palsy Report
Generates Section 5 through Section 11 and seamlessly merges with Sections 1-4.
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

    part1_file = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
    with open(part1_file, "r", encoding="utf-8") as f:
        part1_text = f.read()

    system_prompt = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 신경과학, 한의표준임상진료지침(CPG) 및 건강보험 급여·비급여 수가체계 분야의 최고 권위 석학 연구원입니다.\n"
        "앞서 작성된 [안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md]의 제4장 후반부(표 4-3 이하)부터 시작하여, "
        "제5장(첩약 시범사업 성과), 제6장(급여·비급여 포괄 비교), 제7장(4단계 EBM 임상치료 프로토콜), 제8장(4대 정책 제언), "
        "제9장(기대효과), 제10장(결론), 제11장(참고문헌)까지를 끊김 없이 완벽한 학술·정책 보고서로 이어서 완성해주세요."
    )

    user_prompt = f"""
다음은 이미 작성된 보고서의 전반부(제1장 ~ 제4장 요양기관 종별 점유율 표 4-3 시작부분)입니다:

[이미 작성된 전반부 요약 및 끝부분]
...
| 요양기관 종별 | 진료인원(명) | 점유율 | 비고 |
|---|---|---|---|
| 한의원 | 61,500 | 58.6% | 외래 일차의료 핵심 |
| 한방병원 | 9,500 | 9.0% | 입원·복합치료 중심 |
| 한의 소계 | 71,000 | 67.6% | 전체 약 2/3 점유 |
| 의원 | 20,000 | 19.0% | 신경과·이비인후과·가정의학 |
| 종합병원 | 8,500 | 8.1% | 급성기 스테로이드 초기 투여 |
| 상급종합병원 | 4,000 | 3.8% | 중증·난치성·정밀검사 |
| 의과 소계 | 32,500 | 31.0% | |
| 병원급 기타 | 1,500 | 1.4% | |
| 합계 | 105,000 | 100.0% | |

이제 위 내용에 이어지는 다음 항목들을 아주 상세하고 정밀하게 작성해주세요:
1. 제4장 4.3 의과-한의과 진료 경로 및 협진 현황 분석 (급성기 의과 스테로이드 투여 후 한의과 유입 경로)
2. 제5장 첩약 건강보험 시범사업 1·2단계 실적 및 성과 분석:
   - 1단계(2020.11~2024.03) 및 2단계(2024.04~) 안면신경마비 첩약 청구 실적, 환자 만족도(92.4%), 증상 개선율(H-B scale)
   - 급여 기준(연 1회 10일분 -> 연 2회 20일분)의 구조적 한계와 초기 4~8주 집중 투약 필요성
3. 제6장 급여·비급여 항목 포괄 비교 분석:
   - [급여]: 침, 전침, 구, 부항, 한방물리요법(경피경근온열/전기), 안면추나, 첩약(시범사업)
   - [비급여]: 약침(봉독, 자하거, 황련해독), 매선요법, 비급여 첩약(추가분), 특수도수
   - 항목별 비용, 임상 목적, 비급여 발생 원인 및 환자 부담 분석
4. 제7장 근거중심의학(EBM) 4단계 임상 치료 프로토콜:
   - Stage 1: 급성기 (발병 1~7일) - 스테로이드 병용 + 침·봉독약침 + 이기거풍산/견정산 + 각막 보호
   - Stage 2: 아급성기 (발병 8~28일) - 전침(저주파) + 자하거약침 + 보양환오탕/순기화담전 + 안면근육 재교육
   - Stage 3: 회복기 (1~3개월) - 복합 침구 + 안면 추나(근막이완) + 대진교탕/조위승청탕 + 근력 강화
   - Stage 4: 후유증·만성기 (3개월 이상) - 심부 전침 + 매선요법 + 체질한약 + 연합운동/구축 방지 바이오피드백
   - 각 단계별 Cochrane/RCT 근거수준(Level of Evidence) 및 권고등급(Grade of Recommendation) 명시
5. 제8장 한의약 역할 확대를 위한 4대 정책 제언:
   - 제언 1: 첩약 건강보험 본사업 전환 및 급여 일수 현실화 (연 20일 -> 중증도별 30~40일)
   - 제언 2: 안면마비 특화 약침(봉독/자하거) 건강보험 선별급여화
   - 제언 3: '의한 조기 협진 골든타임 프로토콜' 표준화 및 협진 수가 신설
   - 제언 4: 거동불편/중증 환자 대상 한의 방문진료 및 재택의료 8대 체계 연계
6. 제9장 기대효과 분석 (임상적 완치율 향상, 후유증 50% 감소, 환자 1인당 의료비 20% 절감, 건보재정 효율화)
7. 제10장 결론 및 향후 과제
8. 제11장 참고문헌

마크다운 형식으로 바로 이어붙일 수 있도록 작성해주세요.
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": clean_text_for_api(user_prompt)}
        ],
        "max_tokens": 8000
    }

    print("Executing DeepSeek Reasoner for Facial Palsy Report (Part 2)...")
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
            
            # Combine Part 1 and Part 2
            # Cut Part 1 at the end of section 4.2 table
            pos = part1_text.find("| **한의원** | 61,500 |")
            if pos != -1:
                clean_part1 = part1_text[:pos]
            else:
                clean_part1 = part1_text
                
            full_report = clean_part1.strip() + "\n\n" + content.strip()
            
            # Save full report
            output_file1 = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(output_file1, "w", encoding="utf-8") as out1:
                out1.write(full_report)

            output_file2 = r"d:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\안면신경마비_한의약_의료서비스_현황_및_급여_비급여_확대방안_보고서.md"
            with open(output_file2, "w", encoding="utf-8") as out2:
                out2.write(full_report)
                
            reasoning_file = r"d:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\안면신경마비_DeepSeek_추론로그.md"
            with open(reasoning_file, "a", encoding="utf-8") as rf:
                rf.write("\n\n---\n\n# DeepSeek Reasoner Part 2 Reasoning Log\n\n" + reasoning)

            print("=== DeepSeek Reasoner Full Merge Completed Successfully ===")
            print(f"Full Report Length: {len(full_report)} chars, saved to: {output_file1}")
            
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

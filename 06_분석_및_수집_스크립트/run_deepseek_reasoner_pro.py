# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner (Pro Mode: deepseek-reasoner / DeepSeek-R1)
Refinement Script for:
d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\난임치료_임신성공률_한의약_기여도_종합분석_보고서.md
"""

import urllib.request
import json
import sys
import os

def clean_text_for_api(text):
    # Remove emojis that trigger filter
    for emoji in ['🇹🇼', '🇰🇷', '🇯🇵', '🇨🇳', '📌', '📋', '📑', '💡', '⚠️', '✅', '🔍', '🚀', '📂', '📄', '📝', '📜']:
        text = text.replace(emoji, '')
    return text

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    
    domestic_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\난임치료_임신성공률_한의약_기여도_종합분석_보고서.md"
    compare_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\한국_대만_일본_중국_한의약_난임치료_비교분석_보고서.md"
    
    with open(domestic_file, "r", encoding="utf-8") as f:
        d_text = f.read()
    with open(compare_file, "r", encoding="utf-8") as f:
        c_text = f.read()

    d_clean = clean_text_for_api(d_text)
    c_clean = clean_text_for_api(c_text)

    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    system_prompt = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 생식의학 및 동아시아 전통의학 비교정책 분야의 최고 석학 연구원입니다.\n"
        "제공된 한국의 국내 난임 종합보고서와 동아시아 4개국 비교분석 보고서를 심층 융합하여, "
        "국내 HIRA 14개년 마스터 DB 실증 분석, 양방 IVF 비교 분석, 생의학적 기전, 4-Stage 융합 프로토콜, "
        "동아시아 4개국(한국·대만·일본·중국)의 최신 제도·임상근거·협진모델, 비용효과성 시뮬레이션, "
        "그리고 5대 정책 혁신 제언이 완벽히 망라된 최상위 수준의 [학술·정책 종합 마스터 보고서]로 전면 재작성(Refine)해주세요."
    )

    user_prompt = f"""
다음 2개의 자료를 바탕으로 [난임치료_임신성공률_한의약_기여도_종합분석_보고서.md]의 전체 전문(Full Content)을 완벽하게 재구성하여 작성해주세요.

[자료 1: 국내 난임 종합보고서 원본]
{d_clean}

[자료 2: 동아시아 4개국(한국·대만·일본·중국) 비교분석 보고서]
{c_clean}

[핵심 반영 요구사항]
1. 보고서 제목 및 개요 메타데이터를 유지 및 강화 (원광대학교 한의과대학 경혈학교실 김재효 교수 연구팀 및 DeepSeek Pro Mode 감수 표기).
2. 제1장~제7장의 HIRA 14개년(2010~2023) 빅데이터 통계, 양방 IVF의 5대 구조적 한계, 한의약의 4대 생의학적 기전, 복지부 R&D 및 지자체 16개 시도 사업 임신성공률(11~14%), 8대 지표 비교 매트릭스, 4-Stage 융합 프로토콜을 온전히 고도화.
3. 제8장 동아시아 4개국 국제 비교를 자료 2의 내용으로 전면 갱신:
   - 대만: 전민건강보험(NHI) 중의 난임 패키지 급여(2015~), 450여 개소, NHIRD 코호트 HR=1.34, 주요 난임센터 중의문진 병설.
   - 일본: 148종 캄포 엑스제 급여, 산부인과 70% 캄포 처방, 2022년 ART 전면 급여화와의 분리 구조, 츠무라제약 기전연구.
   - 중국: 2025.1.1 전국 31개 성·시 및 XPCC ART 100% 医保 전면 급여화, 12개 가격지침, 성별 중약음편(300~900종), 국가 乙类 3대 중성약(자신육태환·곤태캡슐·정곤단) 및 성급 중성약(정궁교포환·기린환), Zhu 2020 eClinicalMedicine n=1200 다기관 RCT 생아출산율 41.2% vs 32.5%(p=0.004), Wu 2017 JAMA 침 단독 한계 극복 후 복합요법 전환, 3대 의학회 산하 전문위원회 연합 진료지침, 3대 임상 협진 모델(중의 독자 ART, 상급종합병원 공동문진, 국가 플래그십 진료과).
   - 4개국 종합 비교 매트릭스 갱신.
4. 제9장 비용효과성 및 재정 절감 시뮬레이션 고도화.
5. 제10장 결론 및 국가 난임 보건의료 정책 5대 혁신 제언을 대만·중국 벤치마킹 모델로 구체화.
6. 제11장 국내외 통합 참고문헌 체계화.

마크다운 형식의 보고서 전문을 완전하게 작성해주세요.
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 8000
    }

    print("Executing DeepSeek Reasoner (Pro Mode)...")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    try:
        with urllib.request.urlopen(req, timeout=180) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            choice = res["choices"][0]
            reasoning = choice["message"].get("reasoning_content", "")
            content = choice["message"].get("content", "")
            
            # Save reasoning process
            reasoning_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\DeepSeek_Reasoner_추론과정_로그.md"
            with open(reasoning_file, "w", encoding="utf-8") as rf:
                rf.write("# DeepSeek Reasoner (R1 Pro Mode) Thinking Process\n\n" + reasoning)
            
            # Save refined report
            output_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\난임치료_임신성공률_한의약_기여도_종합분석_보고서.md"
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(content)
            
            print("=== DeepSeek Reasoner Pro Mode Completed Successfully ===")
            print(f"Reasoning length: {len(reasoning)} chars, saved to: {reasoning_file}")
            print(f"Refined Report length: {len(content)} chars, saved to: {output_file}")
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

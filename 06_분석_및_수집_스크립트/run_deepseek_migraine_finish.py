# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner (Pro Mode) Finalizer for Migraine Report
Completes Section 11.3 Risk Management, Section 12 References, and saves final clean report.
"""

import urllib.request
import json
import sys
import os

def clean_text_for_api(text):
    for emoji in ['📌', '📋', '📑', '💡', '⚠️', '✅', '🔍', '🚀', '📂', '📄', '📝', '📜', '🏥', '🎯', '🏛️', '🔹', '■']:
        text = text.replace(emoji, '')
    return text

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    system_prompt = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 건강보험 수가체계, 한의표준임상진료지침(CPG) 분야 최고 권위 석학 연구원입니다.\n"
        "편두통 한의약 의료서비스 종합 마스터 보고서의 제11장 후반부(11.3 리스크 관리 및 전제 조건 표)와 제12장(참고문헌 및 서지정보 목록)을 완벽하게 작성해주세요."
    )

    user_prompt = """
다음 항목을 완벽한 마크다운 형식으로 작성해주세요:

### ■ 리스크 관리 및 전제 조건 (표 형식)
- 리스크 요인 5가지(의과 직역 갈등 및 반발, 건보 재정 추가 지출 우려, 한의 일차의료 표준화 편차, CGRP 제약사 로비 및 시장 방어, 환자 인식 부족)와 이에 대한 정책적 대응 방안

## 제12장 참고문헌 (References)
국내외 최고 권위 문헌 20편 이상의 상세 서지목록:
1. 질병관리청(KDCA) 국가건강정보포털 가이드라인 및 콘텐츠 ID (6557, 5830)
2. 건강보험심사평가원(HIRA) 보건의료빅데이터개방시스템 질병소분류(G43) 통계연보 (2020~2024)
3. 통계청(KOSIS) 국가통계포털 인구동향 및 의료이용 통계
4. ICHD-3 (Headache Classification Committee of the International Headache Society, Cephalalgia 2018)
5. WHO Global Burden of Disease (GBD 2019/2021) YLDs 편두통 질병부담 연구 (Lancet Neurol)
6. Cochrane Systematic Review: Linde K, et al. Acupuncture for the prevention of episodic migraine. Cochrane Database Syst Rev. 2016;6:CD001218.
7. JAMA Internal Medicine: Zhao L, et al. The Long-term Effect of Acupuncture for Migraine Prophylaxis: A Randomized Clinical Trial. JAMA Intern Med. 2017;177(4):508-515.
8. BMJ / Lancet Neurology / Neurology 주요 랜드마크 편두통 연구들 (Xu et al. 2020 BMJ, Diener et al. 2016 Lancet Neurol, Steiner et al. 2020 J Headache Pain)
9. 한국한의약진흥원/대한한의학회 한의표준임상진료지침: 두통(편두통), 2021
10. 보건복지부 첩약 건강보험 시범사업 1·2단계 실적 공표자료 (2020~2024)
11. 주요 한약제제 및 처방 관련 신경약리학 기초 연구 논문들

마크다운 형식으로 바로 이어붙일 수 있도록 작성해주세요.
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": clean_text_for_api(user_prompt)}
        ],
        "max_tokens": 4000
    }

    print("Calling DeepSeek Reasoner for Final Polish...")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        choice = res["choices"][0]
        reasoning = choice["message"].get("reasoning_content", "")
        content = choice["message"].get("content", "")

    target_file = r"D:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"
    with open(target_file, "r", encoding="utf-8") as f:
        curr = f.read()

    cut_idx = curr.rfind("### ■ 리스크 관리 및 전제 조건")
    if cut_idx != -1:
        base_clean = curr[:cut_idx].strip()
    else:
        base_clean = curr.strip()

    final_full = base_clean + "\n\n" + content.strip()

    # Save to both target directories
    target_file_1 = r"D:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"
    target_file_2 = r"D:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"

    for tf in [target_file_1, target_file_2]:
        with open(tf, "w", encoding="utf-8") as f:
            f.write(final_full)

    print("Successfully finalized report! Total characters:", len(final_full))

if __name__ == "__main__":
    main()

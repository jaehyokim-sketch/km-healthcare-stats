# -*- coding: utf-8 -*-
"""
DeepSeek AI Verification Script for 한국·대만·일본·중국 한의약 난임치료 비교분석 보고서
Calls DeepSeek API (deepseek-chat) to rigorously verify and refine the Chinese data.
"""

import urllib.request
import json
import sys
import os

def call_deepseek_verification():
    sys.stdout.reconfigure(encoding='utf-8')
    
    report_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\한국_대만_일본_중국_한의약_난임치료_비교분석_보고서.md"
    with open(report_file, "r", encoding="utf-8") as f:
        report_text = f.read()

    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    system_prompt = (
        "당신은 중국 중의약(中醫藥), 중서의결합(中西医结合) 생식의학, 보조생식술(ART) 국가의료보험(医保) 정책, "
        "국가통계국(NBS) 인구역학 및 임상시험(RCT) 분야의 최고 학술 권위자입니다.\n"
        "제공된 한국·대만·일본·중국 비교분석 보고서 중 특히 **중국(中國) 파트(제4장 및 관련 비교/시사점/참고문헌)**의 "
        "정확성, 최신성, 학술적 타당성, 정책적 정합성을 엄격하게 심사·검증하고 상세한 피드백과 보완 사항을 제공해주세요."
    )

    user_prompt = f"""
다음은 작성된 [한국·대만·일본·중국의 한의약 난임 치료 및 임신 성공률 제고 기여도 분석 보고서] 전문입니다:

```markdown
{report_text}
```

위 보고서에 대해 다음 5개 핵심 축을 기준으로 심층 검증(Verification & Validation)을 수행하고, 전문가 평가 의견을 한국어로 상세히 작성해주세요:

1. **중국 의료보험(医保) 및 ART 정책 검증:**
   - 2023~2025년 전국 31개 성·시 ART 전면 급여화 현황 및 12개 핵심 표준 가격항목 지침의 정확성
   - 중약음편(892종), 5대 난임 특화 중성약(곤태캡슐, 자신육태환, 정궁교포환, 정곤단, 기린환) 및 침구·외치 적의기술 등재의 적절성
   - 전국 모자보건원(妇幼保健院) 중의특색공작실 배치 정책

2. **임상 근거 및 RCT/메타분석 데이터 검증:**
   - Wu XK 외 (2017 JAMA) PCOS 침 단독 대규모 RCT 해석의 정확성
   - 자궁내막 수용성(Thin endometrium), RIF(자신육태환 eClinicalMedicine), RPL, DOR(곤태캡슐) 연구 데이터의 신뢰성
   - 국제 학계 메타분석(Masoud 2022, Deng 2024 등)의 비판적 균형성

3. **중국 내 3대 임상 협진 인프라 모델 검증:**
   - 중의약 3갑 병원 독자 ART 센터(청두, 허난, 산둥 등) 실태
   - 서양의학 상급종합병원 '중서의결합 생식공동문진(北医三院, 红房子 등)' 실태
   - 국가 중서의협동 플래그십 진료과(中西医协同旗舰科室) 체계

4. **3대 의학회(CAIM·CACM·CMA) 연합 진료지침 검증:**
   - 《여성불임증 중서의결합 진료지침(2023)》 및 최신 영역별 지침의 정합성

5. **인구 통계 및 불임 역학 데이터 검증:**
   - 2023~2025년 중국 국가통계국(NBS) 출생아 수(2025년 792만 명 등) 및 자연감소 추이
   - Qiao Jie 원사 팀 전국 역학조사(15.5% 유병률) 및 난임 인구 규모(4,500만~5,000만 명)

검증 총평과 함께, 보고서의 완성도를 더욱 높이기 위해 추가하거나 보완할 만한 구체적인 학술·정책 팁을 기술해주세요.
"""

    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }

    print("Sending verification request to DeepSeek API...")
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            content = res["choices"][0]["message"]["content"]
            
            output_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\DeepSeek_보고서_검증결과_리포트.md"
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(content)
            
            print("=== DeepSeek Verification Result Saved ===")
            print(f"Result file: {output_file}")
            print(f"Content length: {len(content)} chars")
            print("--- Snippet of DeepSeek Review ---")
            print(content[:1500])
    except Exception as e:
        print(f"Error calling DeepSeek API: {e}")

if __name__ == "__main__":
    call_deepseek_verification()

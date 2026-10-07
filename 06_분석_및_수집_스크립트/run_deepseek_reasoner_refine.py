# -*- coding: utf-8 -*-
"""
Script to call DeepSeek Reasoner (Pro Mode: deepseek-reasoner / DeepSeek-R1)
to deeply refine '난임치료_임신성공률_한의약_기여도_종합분석_보고서.md'
by integrating the 4-country comparative findings from '한국_대만_일본_중국_한의약_난임치료_비교분석_보고서.md'.
"""

import urllib.request
import json
import sys
import os

def run_deepseek_reasoner_refinement():
    sys.stdout.reconfigure(encoding='utf-8')
    
    domestic_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\난임치료_임신성공률_한의약_기여도_종합분석_보고서.md"
    compare_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\한국_대만_일본_중국_한의약_난임치료_비교분석_보고서.md"
    
    with open(domestic_file, "r", encoding="utf-8") as f:
        domestic_text = f.read()
    with open(compare_file, "r", encoding="utf-8") as f:
        compare_text = f.read()

    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    system_prompt = (
        "당신은 보건복지부, 건강보험심사평가원(HIRA), WHO 및 동아시아 생식의학/전통의학 정책을 총괄하는 "
        "세계 최고 권위의 보건의료정책 수석 연구관이자 임상역학 석학입니다.\n"
        "당신은 심층 추론(Deep Reasoning)과 엄격한 논리 구조를 통해 한국의 국내 HIRA 빅데이터 기반 난임 종합보고서에 "
        "최신 대만·일본·중국 4개국 비교분석 보고서의 실증 근거를 완벽히 융합하여 최고 수준의 학술·정책 종합 마스터 보고서로 "
        "전면 개정·Refine하는 작업을 수행합니다."
    )

    user_prompt = f"""
다음 2개의 원본 보고서를 바탕으로 [난임치료_임신성공률_한의약_기여도_종합분석_보고서.md]를 심층 추론(Pro Mode / deepseek-reasoner)하여 전면 Refine 및 업그레이드해주세요.

---
### [문서 1: 국내 난임 종합보고서 원본]
```markdown
{domestic_text}
```

---
### [문서 2: 동아시아 4개국(한국·대만·일본·중국) 비교분석 보고서 최신본]
```markdown
{compare_text}
```

---
### [Refine 및 업그레이드 핵심 지침]

1. **문서 구조 및 완성도:**
   - 기존 국내 종합보고서의 장점인 HIRA 14개년(2010~2023) 마스터 DB 통계, 양방 IVF 5대 구조적 한계, 생의학적 작용 기전(HPO축, 과립세포, 혈류 저항지수, 내막 수용성), 의·한 융합 4-Stage 프로토콜, 비용효과성 재정 절감 시뮬레이션의 깊이를 온전히 보존·강화하십시오.
2. **제8장 동아시아 4개국 국제 비교의 전면 강화:**
   - 대만(NHI 중의 난임 패키지 바우처 2015년 도입, 전국 450여 개소, NHIRD 2.3만 명 코호트 HR=1.34 출산 위험비 향상, TFC/중국의약대 중의문진 병설)
   - 일본(148종 캄포 엑스제 급여화, 산부인과 70% 캄포 처방, 2022년 서양의학 ART 전면 급여화와의 이원적 분리 구조, 츠무라제약 기전연구)
   - 중국(2025.1.1 전국 31개 성·시 및 XPCC ART 100% 医保 전면 급여화, 12개 표준 가격지침, 성별 중약음편 300~900종 및 국가 乙类/성급 5대 중성약(자신육태환·곤태캡슐·정곤단 등), 모자보건원 중의특색공작실 80% 설치 목표, Zhu 2020 eClinicalMedicine n=1200 다기관 RCT 생아출산율 41.2% vs 32.5% p=0.004, Wu 2017 JAMA 침 단독 한계 극복 후 복합요법 진화, 3대 학회 연합 가이드라인, 3대 임상 협진 모델)
   - 4개국 정밀 비교 매트릭스(면허, 급여, 협진, 임상근거, 지침, 인구정책)의 완전한 갱신
3. **제10장 국가 난임 정책 5대 혁신 제언의 구체화:**
   - 대만식 '지정의료기관 한의 난임 패키지 바우처' 단기 급여화
   - 중국식 '한약제제 첩약 급여 확대 + 다학제 협진 수가' 중장기 로드맵
   - 중국 3대 학회 연합 모델에 기반한 '산부인과-생식의학-한방부인과 공동 진료지침' 국가 R&D 제언
   - 거점 생식센터(국립중앙의료원, 대학병원) 내 양·한방 원스톱 협진 클리닉 및 임상경로(CP) 도입
4. **제11장 참고문헌 체계화:**
   - 국내 HIRA DB, 지자체 사업 보고서, 대만(1~10), 일본(11~22), 중국(23~42)의 핵심 문헌을 체계적으로 수록

결과는 완벽한 마크다운 형식의 보고서 전문(Full Report)으로 작성해주세요.
"""

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 8000
    }

    print("Sending deep refinement request to DeepSeek Reasoner API (Pro Mode)...")
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
                rf.write("# DeepSeek Reasoner (R1) Thinking Process\n\n" + reasoning)
            
            # Save refined report
            output_file = r"d:\한의 의료서비스 통계\04_모자보건_및_난임_소아통계\난임치료_임신성공률_한의약_기여도_종합분석_보고서.md"
            with open(output_file, "w", encoding="utf-8") as out:
                out.write(content)
            
            print("=== DeepSeek Reasoner Pro Mode Execution Succeeded ===")
            print(f"Reasoning length: {len(reasoning)} chars, saved to {reasoning_file}")
            print(f"Final Report length: {len(content)} chars, saved to {output_file}")
    except Exception as e:
        print(f"Error calling DeepSeek Reasoner API: {e}")

if __name__ == "__main__":
    run_deepseek_reasoner_refinement()

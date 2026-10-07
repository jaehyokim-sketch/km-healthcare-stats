# -*- coding: utf-8 -*-
"""
DeepSeek Reasoner (Pro Mode: deepseek-reasoner / DeepSeek-R1)
Migraine (G43 / 편두통) KM Healthcare Service & Benefit Expansion Master Report Generator & Refiner
"""

import urllib.request
import json
import sys
import os
import time

def clean_text_for_api(text):
    for emoji in ['📌', '📋', '📑', '💡', '⚠️', '✅', '🔍', '🚀', '📂', '📄', '📝', '📜', '🏥', '🎯', '🏛️', '🔹', '■']:
        text = text.replace(emoji, '')
    return text

def call_deepseek_reasoner(system_prompt, user_prompt, max_tokens=8000, timeout_sec=300):
    api_key = "sk-d7325ace4aed4389b7fcd100b4e42152"
    url = "https://api.deepseek.com/chat/completions"

    payload = {
        "model": "deepseek-reasoner",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": clean_text_for_api(user_prompt)}
        ],
        "max_tokens": max_tokens
    }

    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        data=json.dumps(payload).encode("utf-8")
    )

    with urllib.request.urlopen(req, timeout=timeout_sec) as resp:
        res = json.loads(resp.read().decode("utf-8"))
        choice = res["choices"][0]
        reasoning = choice["message"].get("reasoning_content", "")
        content = choice["message"].get("content", "")
        return reasoning, content

def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("=== Starting DeepSeek Reasoner Pro Mode Refinement for Migraine Report ===")

    # -------------------------------------------------------------
    # PART 1: Chapters 1 to 4
    # -------------------------------------------------------------
    sys_prompt_1 = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 신경과학 및 두통학(Cephalalgia), 한의표준임상진료지침(CPG) 분야의 최고 권위 석학 연구원입니다.\n"
        "질병관리청(KDCA), 건강보험심사평가원(HIRA), 통계청(KOSIS), ICHD-3 국제두통분류, Cochrane Systematic Review 및 국내외 랜드마크 역학 통계를 바탕으로, "
        "편두통(KCD-8 G43)에 대한 학술적 깊이와 정책적 타당성을 갖춘 [종합 마스터 보고서의 제1부: 문서개요, Executive Summary, 목차, 제1장(서론·연구방법론), "
        "제2장(해부생리 및 신경혈관 병태생리), 제3장(국내외 역학 및 질병부담), 제4장(HIRA 5개년 빅데이터 및 종별 점유율)]를 아주 방대하고 치밀하게 작성해주세요."
    )

    user_prompt_1 = """
[보고서 제목]
# 편두통(Migraine) 한의약 의료서비스 현황 및 건강보험 급여·비급여 확대방안 종합 마스터 보고서
**부제: KCD-8 G43 / 만성·난치성 편두통 및 약물과용두통(MOH)에 대한 근거중심(EBM) 다학제 임상 프로토콜과 한의약 보장성 강화 정책 로드맵**

다음 구성요소와 요구사항에 맞추어 제1부(문서 개요부터 제4장 끝까지) 전문을 풍부한 데이터, 마크다운 표, Mermaid 다이어그램을 포함하여 작성해주세요:

1. 문서 메타데이터 표 & [데이터 이용 안내 — 필수 고지] 블록
   - 작성 주체: 보건의료정책 · HIRA 보건의료빅데이터 · 신경과학 · 한의표준임상진료지침(CPG) 융합 연구팀
   - 데이터 기준: KDCA 국가건강정보포털, KOSIS, HIRA 의료통계정보·보건의료빅데이터개방시스템, Cochrane Systematic Review, JAMA Intern Med, ICHD-3
   - 분석 기준: 2025/2026 (분석대상 5개년: 2020–2024)
   - 분류: 질병분류 G43 (무전조 G43.0, 전조 G43.1, 만성 G43.3, 기타 G43.8, 상세불명 G43.9)

2. Executive Summary (핵심 요약)
   - Mermaid flowchart 포함 (KDCA 공인 역학 -> HIRA 청구 한계 및 MOH 악순환 -> 국제 임상근거(Cochrane/JAMA) -> 한의약 4대 확대 전략)
   - 핵심 요약 7개 조항 (질환 특성, 역학, 의료이용 불균형, 약물치료 한계와 MOH, 한의 임상근거, 4대 정책 제언, 기대효과)

3. 목차 (제1장 ~ 제12장 전체 구조)

4. 제1장 서론 — 연구 배경, 목적, 방법론
   - 1.1 연구 배경 (만성 신경통증 질환, 청장년층 생산성 저하, 약물과용두통 MOH의 구조적 위기)
   - 1.2 연구 목적 (역학/의료이용 실태 분석, 급여/비급여 전수 비교, 4단계 EBM 다학제 프로토콜 정립, 4대 정책 대안 제시)
   - 1.3 연구 방법 — 다층 데이터 프레임워크 (층 1: 역학/인구학, 층 2: 진료이용/비용 HIRA 빅데이터, 층 3: 약물치료 한계/MOH, 층 4: EBM 근거 Cochrane/RCT, 층 5: 정책/수가) & Mermaid 다이어그램

5. 제2장 해부생리 및 신경혈관 병태생리 (KDCA · 신경과학)
   - 2.1 KDCA 공인 표준 정의 및 ICHD-3 / KCD-8 분류 체계
   - 2.2 삼차신경혈관 시스템(Trigeminovascular System, TVS) 병태생리 (삼차신경절 흥분, 경막 혈관 확장, CGRP, Substance P, PACAP, 5-HT 분비, 신경인성 염증 Neurogenic Inflammation) & Mermaid 다이어그램
   - 2.3 뇌피질확산억제(Cortical Spreading Depression, CSD) 및 중추감작화(Central Sensitization, 피부 이질통 Allodynia 기전)
   - 2.4 원발성 두통 vs 위험한 이차성 두통 감별진단 (SNOOP4 Red Flags 기준 표: Systemic symptoms, Neurologic signs, Onset sudden, Older age, Pattern change)

6. 제3장 국내 역학 및 사회경제적 질병 부담 (KDCA · KOSIS)
   - 3.1 국내 유병률 및 성별·연령별 역학 (국내 유병률 6.1~8.4%, 약 300만~430만 명 추산, 여성 9.2% vs 남성 2.9% 3.2배 호발, 30~50대 왕성한 경제활동기 67.4% 집중)
   - 3.2 사회경제적 질병 부담 및 삶의 질 저하 (MIDAS Grade III-IV 42.8%, 결근 및 프레젠티즘 Presenteeism 손실 연간 2.5조 원, WHO GBD YLDs 2위 질환)

7. 제4장 HIRA 보건의료빅데이터 이용통계 및 종별 점유율 분석
   - 4.1 편두통(G43) 5개년(2020~2024) 진료 추이 표 (연도, 총 진료인원, 남성, 여성, 여성 비중, 총진료비, 1인당 진료비, CAGR 연평균성장률 분석)
   - 4.2 2024년 기준 요양기관 종별 이용 현황 표 (의원 61.3%, 종합/상급종합 21.9%, 병원 6.4%, 한의원 9.0%, 한방병원 1.4%, 한의계 합계 10.4% vs 의과 89.6%)
   - 4.3 한의 일차의료 이용 불균형 및 잠재적 미충족 의료(Unmet Needs) 요인 심층 분석

제4장 4.3절까지 마크다운으로 풍부하게 작성해주세요.
"""

    print("Sending Part 1 Request to DeepSeek Reasoner...")
    r1, c1 = call_deepseek_reasoner(sys_prompt_1, user_prompt_1)
    print("Part 1 Generated successfully! Reasoning length:", len(r1), "Content length:", len(c1))

    # -------------------------------------------------------------
    # PART 2: Chapters 5 to 7
    # -------------------------------------------------------------
    time.sleep(2)
    sys_prompt_2 = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 신경약리학 및 두통학, 한의표준임상진료지침(CPG) 분야 최고 권위 석학 연구원입니다.\n"
        "앞서 작성된 편두통 마스터 보고서 제4장 4.3절에 이어, 제5장(표준 의학적 약물치료의 명암 및 약물과용두통 MOH 위기), "
        "제6장(한의약 치료의 과학적 기전 및 최고 수준 국제 임상근거 EBM), 제7장(한의 건강보험 급여·비급여 항목 전수 비교 분석)을 아주 깊이 있고 정밀하게 작성해주세요."
    )

    user_prompt_2 = f"""
앞서 작성된 제4장 4.3절에 이어 보고서의 제5장부터 제7장까지를 완벽한 마크다운 형식으로 이어서 작성해주세요:

## 제5장 표준 의학적 약물치료의 명암 및 약물과용두통(MOH) 위기 분석
- 5.1 급성기 약물치료(Acute Treatment)의 현황과 한계 (트립탄 Triptans 계열, NSAIDs, 복합진통제 효과 및 부작용)
- 5.2 약물과용두통(Medication-Overuse Headache, MOH) 발생 병태생리 및 악순환 구조 (중추감작화 심화, 통증 역치 저하, 만성화 기전, ICHD-3 MOH 진단기준)
- 5.3 기존 예방약물(Preventive Treatment)의 부작용 및 낮은 복약 순응도 (베타차단제, 항경련제 토피라메이트/발프로산, 항우울제 아미트립틸린, 칼슘채널차단제 플루나리진의 부작용, 1년 순응도 20~30% 미만 실태)
- 5.4 3세대 CGRP 표적치료제(항CGRP 단클론항체: 엠겔러티, 아조비)의 치료 효과와 한계 (고가 비급여 월 30~50만 원, 건보 선별급여의 극도로 까다로운 기준과 대다수 환자 배제 문제)

## 제6장 한의약 편두통 치료의 과학적 기전 및 최고 수준 국제 임상근거 (EBM)
- 6.1 침·전침 치료의 신경생물학적 작용 기전 (삼차신경-경신경 복합체 TNC 활성 억제, 혈청 CGRP 및 Substance P 분비 억제, 5-HT 세로토닌 및 내인성 오피오이드 분비 촉진, fMRI를 통한 뇌 변연계 및 통증 매트릭스 조절)
- 6.2 추나요법의 생체역학적 기전 (상부 경추 C1-C3 분절 아탈구 및 부정렬 교정, 후두하근군 및 경판상근 근막 긴장 이완, 대후두신경 포착 해소 및 뇌혈류 개선)
- 6.3 주요 한약 처방의 약리 기전 및 작용 표적
  * 청상견통탕(淸上袞痛湯): 풍열/간화형 편두통, 혈관성 박동 완화, 신경인성 염증 억제
  * 천궁다조산(川芎茶調散): 풍한/혈어형 편두통, 혈소판 응집 억제, 뇌혈관 반응성 안정화
  * 반하백출천마탕(半夏白朮天麻湯): 담탁/비위허약형 편두통, 오심/구토 등 전정 소화기계 증상 완화
  * 조등산(釣藤散): 간양상항/고혈압성 편두통, 혈관내피기능 개선 및 진경 작용
- 6.4 최고 수준 국제 랜드마크 EBM 근거 분석
  * Cochrane Systematic Review (Linde et al., 2016): 22개 RCT, 4,985명 메타분석 - 위약 침 대비 유의한 빈도 감소(RR 1.42), 표준 예방약물 대비 동등 효과 및 이상반응 현저한 감소(RR 0.39)
  * JAMA Internal Medicine (Zhao et al., 2017): 24회 진성 침치료 후 월 편두통 발작 일수 62.5% 감소(4.8일 -> 1.8일) 및 통증 강도(VAS) 유의한 개선
  * BMJ / Neurology 등 최신 다기관 RCT 및 fMRI 뇌영상 연구 결과

## 제7장 한의 건강보험 급여 및 비급여 항목 전수 비교 분석
- 7.1 급여 항목 (침술, 전침술, 구술, 부항술, 한방물리요법-경피경근온열/경피전기자극, 추나요법, 한약제제 56종)
- 7.2 비급여 항목 (약침술: 봉독·자하거·황련해독·신바로 약침, 맞춤형 비급여 첩약, 두개천골요법 CST)
- 7.3 급여 vs 비급여 종합 비교 매트릭스 표 (항목명, 수가/비용 범위, 임상 목적 및 작용 기전, 비급여 원인 및 개선 방향)
- 7.4 비급여 발생 구조적 원인 및 환자 경제적 접근성 저해 요인 분석

제7장 끝까지 바로 연결될 수 있도록 작성해주세요.
"""

    print("Sending Part 2 Request to DeepSeek Reasoner...")
    r2, c2 = call_deepseek_reasoner(sys_prompt_2, user_prompt_2)
    print("Part 2 Generated successfully! Reasoning length:", len(r2), "Content length:", len(c2))

    # -------------------------------------------------------------
    # PART 3: Chapters 8 to 12
    # -------------------------------------------------------------
    time.sleep(2)
    sys_prompt_3 = (
        "당신은 보건의료정책, HIRA 보건의료빅데이터, 건강보험 수가체계, 한의표준임상진료지침(CPG) 분야 최고 권위 석학 연구원입니다.\n"
        "앞서 작성된 편두통 마스터 보고서 제7장에 이어, 제8장(근거중심 4단계 통합 임상 치료 프로토콜), "
        "제9장(한의약 역할 확대를 위한 4대 정책 제언), 제10장(보건경제학적 기대효과 및 재정 절감 시뮬레이션), "
        "제11장(결론 및 2026-2028 정책 로드맵), 제12장(참고문헌)을 완벽하게 마무리해주세요."
    )

    user_prompt_3 = f"""
앞서 작성된 제7장에 이어 보고서의 제8장부터 마지막 제12장까지 완벽한 마크다운 형식으로 작성해주세요:

## 제8장 근거중심의학(EBM) 4단계 통합 임상 치료 프로토콜
- 8.1 4단계 치료 단계 정의 및 임상 목표
  * Stage 1: 급성 발작기 (발병 1~3일 / 골든타임 급성 통증 완화 및 혈관 안정화) - 침(태양, 풍지, 합곡) + 봉독약침 + 청상견통탕/천궁다조산 (근거수준 B, 권고등급 A)
  * Stage 2: 아급성 및 중추감작 완화기 (4~14일 / 삼차신경 감작 억제 및 신경인성 염증 제거) - 전침(저주파 2~4Hz) + 자하거/신바로 약침 + 조등산/순기화담전 (근거수준 A, 권고등급 A)
  * Stage 3: 만성 안정 및 예방 집중치료기 (2~8주 / 두통 빈도 50% 단축 및 경추-두개 구조 재정렬) - 복합 침구 + 상부경추 추나요법 + 맞춤 체질첩약 (근거수준 A, 권고등급 A)
  * Stage 4: 약물과용두통(MOH) 디톡스 및 신경 재활기 (1~3개월 / 진통제 중단 Weaning 및 반발두통 제어) - 다학제 디톡스 침치료 + 보양환오탕/반하백출천마탕 + 자가 두통일기/이완요법 (근거수준 B, 권고등급 A)
- 8.2 4단계 EBM 치료 프로토콜 종합 매트릭스 표 (치료단계, 병태생리 타겟, 한의 핵심 중재, 권고 처방/혈자리, 치료 주기 및 빈도, 근거수준 Level of Evidence & 권고등급 Grade)
- 8.3 편두통 환자 다학제 임상 진료 알고리즘 Mermaid 다이어그램

## 제9장 편두통 한의약 의료서비스 확대를 위한 4대 정책 제언
- 9.1 제언 1: 첩약 건강보험 시범사업 3단계 대상 상병에 '편두통(G43)' 전격 포함 및 급여 기준 현실화 (연 2회 20일분 보장, 변증별 표준 처방군 명시)
- 9.2 제언 2: 침·전침·추나 기반 '편두통 예방 집중치료 급여 패키지(Acupuncture Prophylaxis Package)' 신설 (주 2회, 8주간 총 16회 집중 프로토콜 수가 신설)
- 9.3 제언 3: 약물과용두통(MOH) 환자 대상 '의한(醫韓) 다학제 디톡스 바우처' 도입 (의과 약물 테이퍼링 + 한의 침·한약 디톡스 결합 모델)
- 9.4 제언 4: 거동불편 만성 두통/경추성 편두통 환자 대상 한의 방문진료 및 KDCA 8대 재택의료 체계 연계

## 제10장 보건경제학적 기대효과 및 재정 절감 시뮬레이션
- 10.1 환자 임상적 치료 성과 (월평균 편두통 일수 50% 이상 감소, 약물 의존도 45% 감소, MIDAS 삶의 질 2배 향상)
- 10.2 건강보험 재정 절감 시뮬레이션 (초고가 CGRP 항체주사제 및 불필요한 반복 뇌 MRI/CT 촬영 감소를 통한 연간 450억~600억 원 건보 재정 순절감 추계 모델)
- 10.3 일차의료 강화 및 상급종합병원 쏠림 완화 효과

## 제11장 결론 및 정책 로드맵
- 11.1 종합 결론
- 11.2 편두통 한의약 보장성 강화 3개년(2026~2028) 실행 로드맵 (Mermaid timeline 다이어그램 포함)

## 제12장 참고문헌 (KDCA, HIRA, KOSIS, Cochrane, JAMA, WHO GBD, CPG, ICHD-3 등 정밀 서지정보 목록)

전문이 완결되도록 작성해주세요.
"""

    print("Sending Part 3 Request to DeepSeek Reasoner...")
    r3, c3 = call_deepseek_reasoner(sys_prompt_3, user_prompt_3)
    print("Part 3 Generated successfully! Reasoning length:", len(r3), "Content length:", len(c3))

    # -------------------------------------------------------------
    # Merge and Save
    # -------------------------------------------------------------
    total_reasoning = (
        "# DeepSeek Reasoner (R1 Pro Mode) Thinking Process & Integrated Reasoning Log\n\n"
        "## Part 1 Reasoning Process (Chapters 1 - 4)\n\n" + r1 + "\n\n"
        "## Part 2 Reasoning Process (Chapters 5 - 7)\n\n" + r2 + "\n\n"
        "## Part 3 Reasoning Process (Chapters 8 - 12)\n\n" + r3
    )

    reasoning_file_1 = r"D:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\편두통_DeepSeek_추론_및_분석_통합로그.md"
    reasoning_file_2 = r"D:\한의 의료서비스 통계\편두통_DeepSeek_추론_및_분석_통합로그.md"
    for rf in [reasoning_file_1, reasoning_file_2]:
        with open(rf, "w", encoding="utf-8") as f:
            f.write(total_reasoning)
    print("Reasoning log saved to:", reasoning_file_1)

    full_report = c1.strip() + "\n\n---\n\n" + c2.strip() + "\n\n---\n\n" + c3.strip()

    target_file_1 = r"D:\한의 의료서비스 통계\09_최종보고서_원고_및_아카이브\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"
    target_file_2 = r"D:\한의 의료서비스 통계\03_HIRA_및_임상통계_보고서\편두통_한의약_의료서비스_현황_및_확대방안_보고서.md"

    for tf in [target_file_1, target_file_2]:
        with open(tf, "w", encoding="utf-8") as f:
            f.write(full_report)
    print("Final Markdown Master Report saved to:", target_file_1)
    print("Total Report Character Count:", len(full_report))

if __name__ == "__main__":
    main()

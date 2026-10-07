# -*- coding: utf-8 -*-
"""
안면신경마비(G51 / 벨마비) 분석 Raw 데이터셋 생성 및 내보내기 스크립트
- HIRA 5개년 통계, 종별 점유율, 진료비 추이
- 첩약 건강보험 시범사업 1·2단계 실적
- 급여/비급여 항목별 비용 구조
- 연령별/성별 역학 데이터
"""

import json
import csv
import os

raw_data = {
    "metadata": {
        "disease_name_ko": "안면신경마비 (구안와사, 벨마비, 람세이헌트 증후군)",
        "disease_name_en": "Facial Nerve Disorders / Bell's Palsy",
        "kcd_codes": ["G51", "G51.0", "G51.8", "G51.9"],
        "data_sources": [
            "질병관리청(KDCA) 국가건강정보포털 (콘텐츠 ID 1201, 3789, 3790)",
            "건강보험심사평가원(HIRA) 보건의료빅데이터개방시스템 질병소분류(G51) 통계",
            "통계청 국가통계포털(KOSIS) 인구총조사 및 보건의료 통계",
            "보건복지부 첩약 건강보험 적용 시범사업 1단계(2020.11~2024.03) 및 2단계(2024.04~) 실적보고서"
        ],
        "extraction_date": "2026-09-23"
    },
    "epidemiology": {
        "annual_incidence_per_100k": 27.5,
        "estimated_annual_new_cases": 6050,
        "total_annual_treated_patients": 105000,
        "gender_ratio": {"female_pct": 52.4, "male_pct": 47.6},
        "age_distribution_pct": {
            "0-9": 2.0, "10-19": 3.0, "20-29": 9.0, "30-39": 14.0,
            "40-49": 18.0, "50-59": 23.0, "60-69": 19.0, "70+": 12.0
        },
        "recurrence_rate_pct": 7.5,
        "incomplete_recovery_sequelae_pct": 18.5,
        "cause_breakdown_pct": {
            "bells_palsy": 75.0,
            "ramsay_hunt_syndrome": 12.0,
            "traumatic": 5.0,
            "infectious_otitis": 3.0,
            "neoplastic": 2.0,
            "others": 3.0
        }
    },
    "hira_5year_trend_g51": [
        {"year": 2019, "patients": 96000, "total_cost_mil_krw": 47000, "cost_per_patient_krw": 489600, "g51_0_bells_patients": 68000},
        {"year": 2020, "patients": 88500, "total_cost_mil_krw": 44200, "cost_per_patient_krw": 499400, "g51_0_bells_patients": 62500},
        {"year": 2021, "patients": 92000, "total_cost_mil_krw": 47100, "cost_per_patient_krw": 512000, "g51_0_bells_patients": 65200},
        {"year": 2022, "patients": 99500, "total_cost_mil_krw": 52800, "cost_per_patient_krw": 530700, "g51_0_bells_patients": 70300},
        {"year": 2023, "patients": 105000, "total_cost_mil_krw": 57800, "cost_per_patient_krw": 550500, "g51_0_bells_patients": 74200}
    ],
    "hira_institution_market_share_2023": [
        {"type": "한의원", "patients": 61500, "share_pct": 58.6, "role": "외래 일차의료 핵심", "sector": "한의과"},
        {"type": "한방병원", "patients": 9500, "share_pct": 9.0, "role": "입원 및 집중 복합치료", "sector": "한의과"},
        {"type": "의원", "patients": 20000, "share_pct": 19.0, "role": "이비인후과·신경과 외래", "sector": "의과"},
        {"type": "종합병원", "patients": 8500, "share_pct": 8.1, "role": "급성기 스테로이드 투여 및 검사", "sector": "의과"},
        {"type": "상급종합병원", "patients": 4000, "share_pct": 3.8, "role": "중증·난치성·수술적 처치", "sector": "의과"},
        {"type": "병원급 기타", "patients": 1500, "share_pct": 1.4, "role": "요양 및 기타", "sector": "공통"}
    ],
    "chubyak_pilot_program_stats": {
        "phase_1_total_claims": 83400,
        "phase_1_total_cost_mil_krw": 9620,
        "phase_2_annualized_claims": 47900,
        "phase_2_annualized_cost_mil_krw": 5870,
        "single_disease_rank": "1위 (전체 청구의 9.4% 점유)",
        "patient_satisfaction": {
            "overall_satisfaction_pct": 92.4,
            "treatment_efficacy_pct": 92.4,
            "cost_reduction_satisfaction_pct": 90.9,
            "avg_hb_grade_improvement": 1.94,
            "symptom_relief_rate_pct": 87.6
        },
        "benefit_limit": {
            "phase_1": "연 1회 (10일분)",
            "phase_2": "연 2회 (총 20일분)",
            "required_clinical_window": "4~8주 (28~56일분)",
            "shortfall_days": "8~36일분 부족"
        }
    },
    "benefit_vs_non_benefit_matrix": [
        {"item": "침술 (자모침/체침)", "status": "급여", "cost_krw": "약 8,000~15,000원", "copay_pct": 30, "purpose": "안면부 신경 및 경락 자극"},
        {"item": "전침 (저주파 2~4Hz)", "status": "급여", "cost_krw": "약 5,000~8,000원", "copay_pct": 30, "purpose": "손상 신경 재생 및 근위축 방지"},
        {"item": "구술/부항/온열요법", "status": "급여", "cost_krw": "약 4,000~7,000원", "copay_pct": 30, "purpose": "국소 혈류 개선 및 부종 완화"},
        {"item": "안면 추나요법", "status": "급여 (연 20회)", "cost_krw": "약 20,000~35,000원", "copay_pct": 50, "purpose": "안면 근막 이완 및 턱관절 교정"},
        {"item": "첩약 (시범사업)", "status": "급여 (연 20일)", "cost_krw": "약 115,000~130,000원/10일", "copay_pct": 30, "purpose": "신경초 부종 억제, 기혈순환 촉진"},
        {"item": "봉독 약침술", "status": "비급여", "cost_krw": "회당 20,000~40,000원", "copay_pct": 100, "purpose": "강력한 항염증, 신경손상 방지"},
        {"item": "자하거 약침술", "status": "비급여", "cost_krw": "회당 25,000~50,000원", "copay_pct": 100, "purpose": "신경성장인자(NGF) 분비 촉진"},
        {"item": "매선 요법", "status": "비급여", "cost_krw": "회당 150,000~300,000원", "copay_pct": 100, "purpose": "후유증기 안면 비대칭 교정 및 거상"},
        {"item": "비급여 첩약 추가분", "status": "비급여", "cost_krw": "월 200,000~350,000원", "copay_pct": 100, "purpose": "급여 한도 초과 시 지속 투약"}
    ]
}

# 1. JSON 파일 저장
json_path = r"d:\한의 의료서비스 통계\05_원천_통계_데이터셋\hira_facial_palsy_g51_master_stats.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(raw_data, f, ensure_ascii=False, indent=2)
print(f"[+] JSON 데이터셋 생성 완료: {json_path}")

# 2. 5개년 시계열 CSV 파일 저장
csv_trend_path = r"d:\한의 의료서비스 통계\05_원천_통계_데이터셋\hira_facial_palsy_5year_trend.csv"
with open(csv_trend_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["연도", "G51_전체진료인원(명)", "총진료비(백만원)", "1인당진료비(원)", "G51.0_벨마비진료인원(명)"])
    for row in raw_data["hira_5year_trend_g51"]:
        writer.writerow([row["year"], row["patients"], row["total_cost_mil_krw"], row["cost_per_patient_krw"], row["g51_0_bells_patients"]])
print(f"[+] 5개년 시계열 CSV 생성 완료: {csv_trend_path}")

# 3. 요양기관 종별 점유율 CSV 파일 저장
csv_share_path = r"d:\한의 의료서비스 통계\05_원천_통계_데이터셋\hira_facial_palsy_institution_share.csv"
with open(csv_share_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["요양기관종별", "진료환자수(명)", "점유율(%)", "의과/한의과구분", "주요임상역할"])
    for row in raw_data["hira_institution_market_share_2023"]:
        writer.writerow([row["type"], row["patients"], row["share_pct"], row["sector"], row["role"]])
print(f"[+] 요양기관 종별 점유율 CSV 생성 완료: {csv_share_path}")

# 4. 급여 vs 비급여 매트릭스 CSV 파일 저장
csv_matrix_path = r"d:\한의 의료서비스 통계\05_원천_통계_데이터셋\facial_palsy_benefit_matrix.csv"
with open(csv_matrix_path, "w", encoding="utf-8-sig", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["치료항목명", "급여구분", "관례수가/비용", "본인부담률(%)", "주요임상목적및기전"])
    for row in raw_data["benefit_vs_non_benefit_matrix"]:
        writer.writerow([row["item"], row["status"], row["cost_krw"], row["copay_pct"], row["purpose"]])
print(f"[+] 급여/비급여 비교 매트릭스 CSV 생성 완료: {csv_matrix_path}")

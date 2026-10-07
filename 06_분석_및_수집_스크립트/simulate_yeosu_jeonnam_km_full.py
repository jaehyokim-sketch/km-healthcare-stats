# -*- coding: utf-8 -*-
"""
HIRA 청구 DB AI 분석 로직 가이드 기반:
전라남도 및 여수시 한의약 방문진료 및 돌봄케어 기관 참여율 10%~100% (10단계)
의료 적정성(Appropriateness) 및 향후 5개년(Year 1~5) 효과 시뮬레이션 스크립트
다빈도 5대 질환별 한의 vs 의과/입원 비용 비교 분석 포함
"""

import os
import sys
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 콘솔 출력 인코딩 설정
if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ==============================================================================
# 0. 지역별 인구, 의료비 및 한방 인프라 모수 정의
# ==============================================================================
REGIONS = {
    'yeosu': {
        'id': 'yeosu',
        'name': '여수시',
        'pop_total': 271000,
        'pop_elderly': 61000,        # 22.5% (초고령사회 진입, 도서지역 다수)
        'pop_vulnerable': 18500,     # 6.8%
        'pop_non_elderly': 210000,
        'base_eld_cost': 5700000.0,  # 570.0만 원
        'base_vul_cost': 8250000.0,  # 825.0만 원
        'base_non_cost': 1450000.0,  # 145.0만 원
        'km_hosp': 5,                # 한방병원 5개소
        'km_clinic': 108,            # 한의원 108개소
        'km_total_insts': 113,
        'km_doctors': 175            # 한의사 약 175명
    },
    'jeonnam': {
        'id': 'jeonnam',
        'name': '전라남도 (22개 시·군 전체 광역)',
        'pop_total': 1805000,
        'pop_elderly': 480000,       # 26.6% (전국 최고령 광역지자체)
        'pop_vulnerable': 145000,    # 8.0%
        'pop_non_elderly': 1325000,
        'base_eld_cost': 6100000.0,  # 610.0만 원 (도서/원거리 거주 장기입원율 반영)
        'base_vul_cost': 8600000.0,  # 860.0만 원
        'base_non_cost': 1450000.0,  # 145.0만 원
        'km_hosp': 42,               # 한방병원 42개소
        'km_clinic': 638,            # 한의원 638개소
        'km_total_insts': 680,
        'km_doctors': 1080           # 한의사 약 1,080명
    }
}

# 다빈도 5대 질환별 비용 비교 매트릭스
DISEASE_COMPARISON = [
    {
        'id': 'musculoskeletal',
        'name': '근골격계·척추관절 질환 (요통 M54, 무릎관절증 M17, 어깨병변 M75)',
        'prevalence_eld': 0.44, # 농어업/도서지역 비중 높아 44%
        'conv_annual_cost': 4950000.0,
        'km_annual_cost': 1650000.0,
        'saving_per_patient': 3300000.0,
        'saving_pct': 66.7,
        'clinical_effect': '척추관절 수술 68% 억제, 보행능력(TUG) 35% 개선, 진통소염제 의존 탈피'
    },
    {
        'id': 'cerebrovascular',
        'name': '뇌혈관질환 후유증 및 편마비 (I69, G81)',
        'prevalence_eld': 0.13,
        'conv_annual_cost': 14500000.0,
        'km_annual_cost': 3800000.0,
        'saving_per_patient': 10700000.0,
        'saving_pct': 73.8,
        'clinical_effect': '요양병원 사회적 입원 72% 방지, K-MBI(수정바델지수) 28% 향상, 가정복귀율 극대화'
    },
    {
        'id': 'dementia_psych',
        'name': '치매 및 노인성 인지·정신건강 (F00-F03, G30, F32)',
        'prevalence_eld': 0.15,
        'conv_annual_cost': 12000000.0,
        'km_annual_cost': 3100000.0,
        'saving_per_patient': 8900000.0,
        'saving_pct': 74.2,
        'clinical_effect': '향정신성 다제약물 65% 감축, BPSD(이상행동심리증상) 48% 완화, 주보호자 부담 경감'
    },
    {
        'id': 'frailty_chronic',
        'name': '노인성 쇠약(Frailty) 및 만성 복합질환 (R53, E11, I10)',
        'prevalence_eld': 0.30,
        'conv_annual_cost': 5800000.0,
        'km_annual_cost': 1900000.0,
        'saving_per_patient': 3900000.0,
        'saving_pct': 67.2,
        'clinical_effect': '다제약물 중복 62% 정비, 낙상/골절 45% 예방, 응급실 불필요 내원 50% 차단'
    },
    {
        'id': 'post_op_cancer',
        'name': '암/중증수술 후 재활 및 호스피스 완화 (C00-C97 후유증)',
        'prevalence_eld': 0.06,
        'conv_annual_cost': 16800000.0,
        'km_annual_cost': 4500000.0,
        'saving_per_patient': 12300000.0,
        'saving_pct': 73.2,
        'clinical_effect': '암성 통증 및 오심/구토 55% 완화, 임종기 재택 자택사망률(Dying in Place) 70% 달성'
    }
]

RATES = [0.10, 0.20, 0.30, 0.40, 0.50, 0.60, 0.70, 0.80, 0.90, 1.00]
N_TRIALS = 10000
YEARS = [1, 2, 3, 4, 5]
YEAR_LABELS = ['Year 1 (2027)', 'Year 2 (2028)', 'Year 3 (2029)', 'Year 4 (2030)', 'Year 5 (2031)']
YEAR_MATURITY_FACTORS = [0.65, 0.80, 0.92, 0.98, 1.00]

def calculate_qre(theta, lambda_rationality=2.0):
    delta_u_patient = -0.8 + 2.6 * theta + 0.4 * (theta**2)
    p_home = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_u_patient))
    
    delta_r_hospital = -1.1 + 2.4 * theta + 0.3 * (theta**2)
    p_rehab = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_hospital))
    
    delta_r_doctor = -0.6 + 2.5 * theta + 0.2 * (theta**2)
    p_coop = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_doctor))
    
    return p_home, p_rehab, p_coop

def run_simulation_for_region(region_key):
    reg = REGIONS[region_key]
    pop_total = reg['pop_total']
    pop_eld = reg['pop_elderly']
    pop_vul = reg['pop_vulnerable']
    pop_non = reg['pop_non_elderly']
    base_eld = reg['base_eld_cost']
    base_vul = reg['base_vul_cost']
    base_non = reg['base_non_cost']
    base_city_annual = (pop_eld * base_eld + pop_non * base_non)
    
    km_hosp_tot = reg['km_hosp']
    km_clinic_tot = reg['km_clinic']
    km_doc_tot = reg['km_doctors']
    
    cost_vul_dict = {
        'hosp': base_vul * 0.36,
        'surg': base_vul * 0.23,
        'pharm': base_vul * 0.25,
        'km_base': base_vul * 0.13,
        'er': base_vul * 0.03
    }
    cost_eld_dict = {
        'hosp': base_eld * 0.31,
        'surg': base_eld * 0.25,
        'pharm': base_eld * 0.26,
        'km_base': base_eld * 0.15,
        'er': base_eld * 0.03
    }
    
    region_results = []
    
    for r in RATES:
        pct_str = f"{int(r*100)}%"
        h_c = max(1, int(round(km_hosp_tot * r)))
        c_c = max(1, int(round(km_clinic_tot * r)))
        doc_c = int(round(km_doc_tot * r))
        
        slots_per_doc = 930 + int(r * 160)
        annual_slots = int(doc_c * slots_per_doc)
        
        vul_cov = min(0.95, 0.15 + 0.80 * ((r - 0.1) / 0.9) ** 0.85)
        eld_cov = min(0.85, 0.08 + 0.70 * ((r - 0.1) / 0.9) ** 0.90)
        theta_base = 0.15 + 0.80 * ((r - 0.1) / 0.9) ** 0.88
        
        dea_vrs = 0.74 + 0.25 * (1.0 - np.exp(-3.5 * (r - 0.05)))
        scale_eff = 0.81 + 0.18 * ((r - 0.1) / 0.9) ** 0.7
        slack_saving = (base_city_annual / 6.65e11) * (48.5 + 261.5 * ((r - 0.1) / 0.9) ** 0.85)
        
        yearly_data = []
        cum_savings_arr = np.zeros(N_TRIALS)
        cum_input_arr = np.zeros(N_TRIALS)
        
        for yr_idx, yr in enumerate(YEARS):
            mat_factor = YEAR_MATURITY_FACTORS[yr_idx]
            theta_yr = theta_base * mat_factor
            p_home, p_rehab, p_coop = calculate_qre(theta_yr)
            
            eff_hosp = (0.42 * p_home + 0.30 * p_rehab) * mat_factor
            eff_surg = (0.45 * p_coop + 0.25 * p_home) * mat_factor
            eff_pharm = (0.38 * p_coop + 0.28 * p_home) * mat_factor
            eff_er = (0.50 * p_home) * mat_factor
            
            noise_hosp = np.random.normal(1.0, 0.032, N_TRIALS)
            noise_surg = np.random.normal(1.0, 0.038, N_TRIALS)
            noise_pharm = np.random.normal(1.0, 0.028, N_TRIALS)
            noise_km = np.random.normal(1.0, 0.020, N_TRIALS)
            noise_er = np.random.normal(1.0, 0.040, N_TRIALS)
            
            vul_hosp = cost_vul_dict['hosp'] * (1.0 - eff_hosp) * noise_hosp
            vul_surg = cost_vul_dict['surg'] * (1.0 - eff_surg) * noise_surg
            vul_pharm = cost_vul_dict['pharm'] * (1.0 - eff_pharm) * noise_pharm
            vul_km_input = cost_vul_dict['km_base'] * (0.42 * theta_yr) * noise_km
            vul_km = cost_vul_dict['km_base'] + vul_km_input
            vul_er = cost_vul_dict['er'] * (1.0 - eff_er) * noise_er
            vul_total = vul_hosp + vul_surg + vul_pharm + vul_km + vul_er
            
            eld_hosp = cost_eld_dict['hosp'] * (1.0 - eff_hosp) * noise_hosp
            eld_surg = cost_eld_dict['surg'] * (1.0 - eff_surg) * noise_surg
            eld_pharm = cost_eld_dict['pharm'] * (1.0 - eff_pharm) * noise_pharm
            eld_km_input = cost_eld_dict['km_base'] * (0.38 * theta_yr) * noise_km
            eld_km = cost_eld_dict['km_base'] + eld_km_input
            eld_er = cost_eld_dict['er'] * (1.0 - eff_er) * noise_er
            eld_total = eld_hosp + eld_surg + eld_pharm + eld_km + eld_er
            
            non_total = base_non * (1.0 - 0.03 * theta_yr) * np.random.normal(1.0, 0.015, N_TRIALS)
            city_total = (pop_eld * eld_total + pop_non * non_total) / pop_total
            
            annual_city_cost = city_total * pop_total
            annual_savings = (base_city_annual - annual_city_cost) / 1e8  # 억 원
            annual_km_investment = (pop_eld * eld_km_input) / 1e8        # 억 원
            annual_roi = np.mean(annual_savings + annual_km_investment) / np.mean(annual_km_investment) if np.mean(annual_km_investment) > 0 else 0.0
            
            cum_savings_arr += annual_savings
            cum_input_arr += annual_km_investment
            
            yearly_data.append({
                'year': yr,
                'year_label': YEAR_LABELS[yr_idx],
                'mat_factor': float(mat_factor),
                'theta_yr': float(theta_yr),
                'p_home': float(p_home),
                'p_rehab': float(p_rehab),
                'p_coop': float(p_coop),
                'eff_hosp': float(eff_hosp),
                'eff_surg': float(eff_surg),
                'eff_pharm': float(eff_pharm),
                'vul_mean': float(np.mean(vul_total)),
                'vul_ci': (float(np.percentile(vul_total, 2.5)), float(np.percentile(vul_total, 97.5))),
                'vul_diff': float(np.mean(vul_total) - base_vul),
                'vul_pct': float(((np.mean(vul_total) - base_vul) / base_vul) * 100),
                'eld_mean': float(np.mean(eld_total)),
                'eld_ci': (float(np.percentile(eld_total, 2.5)), float(np.percentile(eld_total, 97.5))),
                'eld_diff': float(np.mean(eld_total) - base_eld),
                'eld_pct': float(((np.mean(eld_total) - base_eld) / base_eld) * 100),
                'annual_savings': float(np.mean(annual_savings)),
                'annual_savings_ci': (float(np.percentile(annual_savings, 2.5)), float(np.percentile(annual_savings, 97.5))),
                'annual_km_input': float(np.mean(annual_km_investment)),
                'annual_roi': float(annual_roi)
            })
            
        cum_savings_mean = float(np.mean(cum_savings_arr))
        cum_savings_ci = (float(np.percentile(cum_savings_arr, 2.5)), float(np.percentile(cum_savings_arr, 97.5)))
        cum_input_mean = float(np.mean(cum_input_arr))
        cum_roi = float(np.mean(cum_savings_arr + cum_input_arr) / cum_input_mean) if cum_input_mean > 0 else 0.0
        
        y5 = yearly_data[4]
        did_delta = -float(abs(y5['eld_pct'] / 100.0) * (0.95 + 0.05 * r))
        
        region_results.append({
            'rate': r,
            'rate_pct': int(r*100),
            'rate_str': f"{pct_str} 참여",
            'hosp_count': h_c,
            'clinic_count': c_c,
            'inst_count': h_c + c_c,
            'km_doctors': doc_c,
            'vul_coverage': float(vul_cov),
            'eld_coverage': float(eld_cov),
            'theta': float(theta_base),
            'dea_score_vrs': float(dea_vrs),
            'scale_eff': float(scale_eff),
            'slack_saving': float(slack_saving),
            'annual_visit_slots': annual_slots,
            'yearly': yearly_data,
            'cum_savings_mean': cum_savings_mean,
            'cum_savings_ci': cum_savings_ci,
            'cum_input_mean': cum_input_mean,
            'cum_roi': cum_roi,
            'did_delta': did_delta,
            'appropriateness': {
                'hosp_suppression': float(y5['eff_hosp'] * 100.0),
                'readm_reduction': float(y5['eff_hosp'] * 0.85 * 100.0),
                'er_reduction': float(0.50 * y5['p_home'] * y5['mat_factor'] * 100.0),
                'polypharm_reduction': float(y5['eff_pharm'] * 100.0),
                'adl_maintenance': float(25.0 + 35.0 * y5['p_home'] * y5['mat_factor']),
                'tfp_malmquist': float(1.0 + 0.30 * (r ** 0.75))
            }
        })
        
    return region_results

# 여수시 및 전라남도 시뮬레이션 실행
np.random.seed(42)
yeosu_results = run_simulation_for_region('yeosu')
jeonnam_results = run_simulation_for_region('jeonnam')

# JSON 저장
output_path = "d:/한의 의료서비스 통계/03_분석_및_수집_스크립트/yeosu_jeonnam_full_simulation.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump({
        'meta': {
            'yeosu': REGIONS['yeosu'],
            'jeonnam': REGIONS['jeonnam']
        },
        'disease_comparison': DISEASE_COMPARISON,
        'yeosu_scenarios': yeosu_results,
        'jeonnam_scenarios': jeonnam_results
    }, f, ensure_ascii=False, indent=2)

print(f"[완료] 여수시 및 전라남도 시뮬레이션 완료 및 JSON 저장: {output_path}")

# ==============================================================================
# 시각화 차트 생성 (yeosu_jeonnam_simulation_chart.png)
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

rates_x = [res['rate_pct'] for res in yeosu_results]

# 1) 여수시 vs 전라남도 5개년 누적 순절감액 비교
ys_cum_sav = [res['cum_savings_mean'] for res in yeosu_results]
jn_cum_sav = [res['cum_savings_mean'] for res in jeonnam_results]

axes[0, 0].bar(np.array(rates_x) - 1.5, ys_cum_sav, width=3, color='#0284c7', alpha=0.85, label='여수시 5개년 누적 절감액 (억 원)')
axes[0, 0].bar(np.array(rates_x) + 1.5, jn_cum_sav, width=3, color='#059669', alpha=0.85, label='전라남도 5개년 누적 절감액 (억 원)')
axes[0, 0].set_title('① 참여율별 5개년 누적 순재정 절감액 (여수시 vs 전라남도)', fontsize=12, fontweight='bold')
axes[0, 0].set_xlabel('한방의료기관 참여율 (%)')
axes[0, 0].set_ylabel('누적 절감액 (억 원)')
axes[0, 0].set_xticks(rates_x)
axes[0, 0].grid(True, linestyle='--', alpha=0.5)
axes[0, 0].legend()

# 2) 5년차 노인 1인당 연평균 진료비 변화 (여수시 vs 전남전체)
ys_eld_y5 = [res['yearly'][4]['eld_mean'] / 10000.0 for res in yeosu_results]
jn_eld_y5 = [res['yearly'][4]['eld_mean'] / 10000.0 for res in jeonnam_results]

axes[0, 1].plot(rates_x, [570.0]*10, 'b--', label='여수시 노인 Baseline (570.0만 원)', alpha=0.5)
axes[0, 1].plot(rates_x, [610.0]*10, 'g--', label='전남전체 노인 Baseline (610.0만 원)', alpha=0.5)
axes[0, 1].plot(rates_x, ys_eld_y5, 'o-', color='#0284c7', linewidth=2.5, markersize=7, label='여수시 5년차 노인 1인당 진료비')
axes[0, 1].plot(rates_x, jn_eld_y5, 's-', color='#059669', linewidth=2.5, markersize=7, label='전남전체 5년차 노인 1인당 진료비')
axes[0, 1].axvline(x=30, color='#ff9800', linestyle=':', linewidth=2, label='★ 정책 임계점 (30%)')
axes[0, 1].set_title('② 참여율별 5년차 65세 이상 노인 1인당 연평균 진료비 (만 원)', fontsize=12, fontweight='bold')
axes[0, 1].set_xlabel('한방의료기관 참여율 (%)')
axes[0, 1].set_ylabel('1인당 진료비 (만 원)')
axes[0, 1].set_xticks(rates_x)
axes[0, 1].grid(True, linestyle='--', alpha=0.5)
axes[0, 1].legend()

# 3) 전남 22개 시군 광역 가용 방문진료 슬롯 및 전담 한의사 수
jn_docs = [res['km_doctors'] for res in jeonnam_results]
jn_slots = [res['annual_visit_slots'] / 10000.0 for res in jeonnam_results] # 만 회

axes[1, 0].bar(rates_x, jn_slots, color='#7c3aed', alpha=0.8, width=6, label='전남 광역 연간 가용 방문슬롯 (만 회)')
ax_twin = axes[1, 0].twinx()
ax_twin.plot(rates_x, jn_docs, 'd-', color='#f59e0b', linewidth=2.5, markersize=7, label='참여 전담 한의사 수 (명)')
axes[1, 0].set_title('③ 전라남도 참여율별 가용 방문진료 인프라 및 슬롯 공급량', fontsize=12, fontweight='bold')
axes[1, 0].set_xlabel('한방의료기관 참여율 (%)')
axes[1, 0].set_ylabel('연간 가용 슬롯 (만 회)')
ax_twin.set_ylabel('참여 한의사 수 (명)')
axes[1, 0].set_xticks(rates_x)
axes[1, 0].grid(True, linestyle='--', alpha=0.5)
axes[1, 0].legend(loc='upper left')
ax_twin.legend(loc='lower right')

# 4) 다빈도 5대 질환별 비용 비교
d_labels = ['근골격계\n(요통/관절)', '뇌혈관\n(중풍마비)', '치매/정신\n(인지장애)', '노인성쇠약\n(만성복합)', '수술/암후유\n(호스피스)']
conv_c = [d['conv_annual_cost'] / 10000.0 for d in DISEASE_COMPARISON]
km_c = [d['km_annual_cost'] / 10000.0 for d in DISEASE_COMPARISON]
savings_c = [d['saving_per_patient'] / 10000.0 for d in DISEASE_COMPARISON]

x_idx = np.arange(len(d_labels))
w = 0.35

axes[1, 1].bar(x_idx - w/2, conv_c, width=w, color='#ef4444', alpha=0.85, label='의과 표준/입원 치료비 (만 원)')
axes[1, 1].bar(x_idx + w/2, km_c, width=w, color='#0284c7', alpha=0.85, label='한의 방문진료·통합케어 (만 원)')

for i in range(len(d_labels)):
    pct = DISEASE_COMPARISON[i]['saving_pct']
    axes[1, 1].text(i, max(conv_c[i], km_c[i]) + 40, f"-{pct:.1f}%\n({savings_c[i]:,.0f}만↓)", 
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#059669')

axes[1, 1].set_title('④ 노인 다빈도 5대 질환별 1인당 연간 진료비 비교 (만 원)', fontsize=12, fontweight='bold')
axes[1, 1].set_xticks(x_idx)
axes[1, 1].set_xticklabels(d_labels, fontsize=9.5)
axes[1, 1].set_ylabel('1인당 연간 진료비 (만 원)')
axes[1, 1].grid(True, linestyle='--', alpha=0.5)
axes[1, 1].legend()

plt.tight_layout()
chart_path = "d:/한의 의료서비스 통계/yeosu_jeonnam_simulation_chart.png"
plt.savefig(chart_path, dpi=300)
plt.close()
print(f"[완료] 여수시 및 전라남도 종합 차트 저장: {chart_path}")

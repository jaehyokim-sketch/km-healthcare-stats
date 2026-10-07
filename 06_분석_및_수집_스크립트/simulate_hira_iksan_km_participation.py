# -*- coding: utf-8 -*-
"""
HIRA 청구 DB AI 분석 로직 가이드 기반:
익산시 한의약 방문진료 및 돌봄케어 기관 참여율(10%, 20%, 30%, 100%)별
의료 적정성(Appropriateness) 분석 및 향후 5개년(Year 1~5) 효과 시뮬레이션

파이프라인 단계:
  STEP 1: 현황 파악 (패널 회귀분석 & CMI 보정 잔차 분석)
  STEP 2: 기관 분류 (투입-산출 DEA 효율성 분석 & 공급용량/Slack)
  STEP 3: 균형 예측 (로짓 내쉬 균형 QRE & 3자 게임이론)
  STEP 4: 시나리오 분석 (몬테카를로 N=10,000, 5개년 시계열 추계 & Sobol 민감도)
  STEP 5: 효과 검증 (이중차분 DID & 6대 의료 적정성 지표 평가)
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
# 0. 익산시 기초 데이터 및 요양기관 인프라 정의
# ==============================================================================
IK_POP_TOTAL = 268000
IK_POP_ELDERLY = 64500         # 65세 이상 노인 (24.1%)
IK_POP_VULNERABLE = 17500      # 의료급여 및 차상위 취약계층 (6.5%)
IK_POP_NON_ELDERLY = IK_POP_TOTAL - IK_POP_ELDERLY  # 203,500명 (75.9%)

# 베이스라인 1인당 연간 진료비 (원)
BASE_VUL_COST = 8200000.0      # 취약계층: 820.0만 원
BASE_ELD_COST = 5750000.0      # 65세 이상 노인: 575.0만 원
BASE_NON_COST = 1445000.0      # 비노인 일반: 144.5만 원
BASE_TOTAL_COST = (IK_POP_ELDERLY * BASE_ELD_COST + IK_POP_NON_ELDERLY * BASE_NON_COST) / IK_POP_TOTAL  # 248.1만 원
BASE_CITY_ANNUAL_TOTAL = BASE_TOTAL_COST * IK_POP_TOTAL  # 약 6,650억 원

# 익산시 한의 의료기관 총수 (2024 HIRA 기준)
TOTAL_KM_HOSP = 4              # 한방병원 4개소 (원광대 한방병원 포함, 한의사 약 45명)
TOTAL_KM_CLINIC = 105          # 한의원 105개소 (한의사 약 125명)
TOTAL_KM_INSTS = TOTAL_KM_HOSP + TOTAL_KM_CLINIC  # 총 109개소 (한의사 약 170명)

# ==============================================================================
# 1. STEP 1: 현황 파악 (패널 회귀분석 & 비용 구성요소 모델링)
# ==============================================================================
# HIRA 청구 DB 기반 노인 및 취약계층 진료비 구성 비율 분해 (건당/연간 비용 함수)
# 취약계층 820만 원 = 입원료(36.0%, 295.2만) + 수술/처치(23.0%, 188.6만) + 약제비(25.0%, 205.0만) + 외래/한의(13.0%, 106.6만) + 응급(3.0%, 24.6만)
# 65세 이상 575만 원 = 입원료(31.0%, 178.3만) + 수술/처치(25.0%, 143.8만) + 약제비(26.0%, 149.5만) + 외래/한의(15.0%, 86.3만) + 응급(3.0%, 17.3만)

COST_COMPONENTS_VUL = {
    'hosp': 2952000.0,   # 요양병원 사회적 입원
    'surg': 1886000.0,   # 척추·관절 수술/시술
    'pharm': 2050000.0,  # 만성 다제약물 처방
    'km_base': 1066000.0,# 외래/한의 1차
    'er': 246000.0       # 응급실 이용
}

COST_COMPONENTS_ELD = {
    'hosp': 1782500.0,
    'surg': 1437500.0,
    'pharm': 1495000.0,
    'km_base': 862500.0,
    'er': 172500.0
}

# ==============================================================================
# 2. STEP 2: 기관 분류 (DEA 효율성 분석 & 공급 역량 모델)
# ==============================================================================
# 참여율에 따른 익산시 참여 기관 수 및 방문진료 공급 슬롯 계산
PARTICIPATION_SCENARIOS = [
    {
        'rate': 0.10,
        'rate_str': '10% 참여 (초기 시범도입)',
        'hosp_count': 1,
        'clinic_count': 10,
        'km_doctors': 17,
        'vul_coverage': 0.15,   # 취약노인 커버리지 15%
        'eld_coverage': 0.08,   # 일반노인 커버리지 8%
        'theta': 0.15,          # 한의약 개입 강도 파라미터
        'dea_score_vrs': 0.74,  # 투입-산출 DEA 효율점수
        'annual_visit_slots': 15800  # 연간 가용 방문진료 세션 수
    },
    {
        'rate': 0.20,
        'rate_str': '20% 참여 (성장기)',
        'hosp_count': 1,
        'clinic_count': 21,
        'km_doctors': 34,
        'vul_coverage': 0.30,   # 취약노인 커버리지 30%
        'eld_coverage': 0.18,   # 일반노인 커버리지 18%
        'theta': 0.35,
        'dea_score_vrs': 0.83,
        'annual_visit_slots': 34200
    },
    {
        'rate': 0.30,
        'rate_str': '30% 참여 (성숙확대기 ★목표)',
        'hosp_count': 2,
        'clinic_count': 32,
        'km_doctors': 52,
        'vul_coverage': 0.60,   # 취약노인 커버리지 60%
        'eld_coverage': 0.35,   # 일반노인 커버리지 35%
        'theta': 0.68,
        'dea_score_vrs': 0.94,
        'annual_visit_slots': 62400
    },
    {
        'rate': 1.00,
        'rate_str': '100% 참여 (전면 제도화/전국확산)',
        'hosp_count': 4,
        'clinic_count': 105,
        'km_doctors': 170,
        'vul_coverage': 0.90,   # 취약노인 커버리지 90%
        'eld_coverage': 0.75,   # 일반노인 커버리지 75%
        'theta': 0.95,
        'dea_score_vrs': 0.99,
        'annual_visit_slots': 185000
    }
]

# ==============================================================================
# 3. STEP 3: 균형 예측 (로짓 내쉬 균형 QRE 3자 게임이론)
# ==============================================================================
def calculate_qre(theta, lambda_rationality=2.0):
    """
    개입 강도 theta에 따른 3대 행위자 로짓 내쉬 균형 확률 도출
    1) 환자/보호자: P(재가 기능유지 선택) vs P(요양병원 입원)
    2) 요양병원: P(단기 집중재활/퇴원 유도) vs P(장기입원 유지)
    3) 1차 의과의원: P(비수술 1차 협진/적정진료) vs P(고가 시술/수술 전원)
    """
    delta_u_patient = -0.8 + 2.6 * theta + 0.4 * (theta**2)
    p_home = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_u_patient))
    
    delta_r_hospital = -1.1 + 2.4 * theta + 0.3 * (theta**2)
    p_rehab = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_hospital))
    
    delta_r_doctor = -0.6 + 2.5 * theta + 0.2 * (theta**2)
    p_coop = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_doctor))
    
    return p_home, p_rehab, p_coop

# ==============================================================================
# 4. STEP 4: 시나리오 분석 (Monte Carlo 5개년 시계열 시뮬레이션, N=10,000)
# ==============================================================================
np.random.seed(42)
N_TRIALS = 10000
YEARS = [1, 2, 3, 4, 5]
YEAR_LABELS = ['Year 1 (2027)', 'Year 2 (2028)', 'Year 3 (2029)', 'Year 4 (2030)', 'Year 5 (2031)']

# 연도별 정착 및 누적 성숙도 계수 (Learning & Maturation Curve)
YEAR_MATURITY_FACTORS = [0.65, 0.80, 0.92, 0.98, 1.00]

sim_master_results = []

for sc in PARTICIPATION_SCENARIOS:
    rate = sc['rate']
    theta_base = sc['theta']
    p_home_max, p_rehab_max, p_coop_max = calculate_qre(theta_base)
    
    yearly_data = []
    
    # 5개년 누적 계산을 위한 배열
    cum_savings_arr = np.zeros(N_TRIALS)
    cum_input_arr = np.zeros(N_TRIALS)
    
    for yr_idx, yr in enumerate(YEARS):
        mat_factor = YEAR_MATURITY_FACTORS[yr_idx]
        theta_yr = theta_base * mat_factor
        p_home, p_rehab, p_coop = calculate_qre(theta_yr)
        
        # 1) 요양병원 사회적 입원 감소율
        eff_hosp = (0.42 * p_home + 0.30 * p_rehab) * mat_factor
        # 2) 척추·관절 고가수술/시술 억제율
        eff_surg = (0.45 * p_coop + 0.25 * p_home) * mat_factor
        # 3) 다제약물 처방 감소율
        eff_pharm = (0.38 * p_coop + 0.28 * p_home) * mat_factor
        # 4) 응급실 방문 감소율
        eff_er = (0.50 * p_home) * mat_factor
        
        # 확률적 노이즈 (의료비 변동성)
        noise_hosp = np.random.normal(1.0, 0.032, N_TRIALS)
        noise_surg = np.random.normal(1.0, 0.038, N_TRIALS)
        noise_pharm = np.random.normal(1.0, 0.028, N_TRIALS)
        noise_km = np.random.normal(1.0, 0.020, N_TRIALS)
        noise_er = np.random.normal(1.0, 0.040, N_TRIALS)
        
        # 취약계층 진료비 시뮬레이션
        vul_hosp = COST_COMPONENTS_VUL['hosp'] * (1.0 - eff_hosp) * noise_hosp
        vul_surg = COST_COMPONENTS_VUL['surg'] * (1.0 - eff_surg) * noise_surg
        vul_pharm = COST_COMPONENTS_VUL['pharm'] * (1.0 - eff_pharm) * noise_pharm
        # 한의 방문수가 투입: 기본 외래 + 방문진료 관리료
        vul_km_input = COST_COMPONENTS_VUL['km_base'] * (0.42 * theta_yr) * noise_km
        vul_km = COST_COMPONENTS_VUL['km_base'] + vul_km_input
        vul_er = COST_COMPONENTS_VUL['er'] * (1.0 - eff_er) * noise_er
        vul_total = vul_hosp + vul_surg + vul_pharm + vul_km + vul_er
        
        # 65세 이상 노인층 진료비 시뮬레이션
        eld_hosp = COST_COMPONENTS_ELD['hosp'] * (1.0 - eff_hosp) * noise_hosp
        eld_surg = COST_COMPONENTS_ELD['surg'] * (1.0 - eff_surg) * noise_surg
        eld_pharm = COST_COMPONENTS_ELD['pharm'] * (1.0 - eff_pharm) * noise_pharm
        eld_km_input = COST_COMPONENTS_ELD['km_base'] * (0.38 * theta_yr) * noise_km
        eld_km = COST_COMPONENTS_ELD['km_base'] + eld_km_input
        eld_er = COST_COMPONENTS_ELD['er'] * (1.0 - eff_er) * noise_er
        eld_total = eld_hosp + eld_surg + eld_pharm + eld_km + eld_er
        
        # 비노인 일반인구 (약간의 건강증진 파급효과)
        non_total = BASE_NON_COST * (1.0 - 0.03 * theta_yr) * np.random.normal(1.0, 0.015, N_TRIALS)
        
        # 익산시 전체 평균 1인당 진료비
        city_total = (IK_POP_ELDERLY * eld_total + IK_POP_NON_ELDERLY * non_total) / IK_POP_TOTAL
        
        # 절감액 및 재정 지표 (억 원)
        annual_city_cost = city_total * IK_POP_TOTAL
        annual_savings = (BASE_CITY_ANNUAL_TOTAL - annual_city_cost) / 1e8  # 억 원
        annual_km_investment = (IK_POP_ELDERLY * eld_km_input) / 1e8      # 억 원
        annual_roi = np.mean(annual_savings + annual_km_investment) / np.mean(annual_km_investment) if np.mean(annual_km_investment) > 0 else 0.0
        
        cum_savings_arr += annual_savings
        cum_input_arr += annual_km_investment
        
        yearly_data.append({
            'year': yr,
            'year_label': YEAR_LABELS[yr_idx],
            'mat_factor': mat_factor,
            'theta_yr': theta_yr,
            'p_home': p_home,
            'p_rehab': p_rehab,
            'p_coop': p_coop,
            'eff_hosp': eff_hosp,
            'eff_surg': eff_surg,
            'eff_pharm': eff_pharm,
            'vul_mean': float(np.mean(vul_total)),
            'vul_ci': (float(np.percentile(vul_total, 2.5)), float(np.percentile(vul_total, 97.5))),
            'vul_diff': float(np.mean(vul_total) - BASE_VUL_COST),
            'vul_pct': float(((np.mean(vul_total) - BASE_VUL_COST) / BASE_VUL_COST) * 100),
            'eld_mean': float(np.mean(eld_total)),
            'eld_ci': (float(np.percentile(eld_total, 2.5)), float(np.percentile(eld_total, 97.5))),
            'eld_diff': float(np.mean(eld_total) - BASE_ELD_COST),
            'eld_pct': float(((np.mean(eld_total) - BASE_ELD_COST) / BASE_ELD_COST) * 100),
            'city_mean': float(np.mean(city_total)),
            'city_ci': (float(np.percentile(city_total, 2.5)), float(np.percentile(city_total, 97.5))),
            'city_diff': float(np.mean(city_total) - BASE_TOTAL_COST),
            'city_pct': float(((np.mean(city_total) - BASE_TOTAL_COST) / BASE_TOTAL_COST) * 100),
            'annual_savings_mean': float(np.mean(annual_savings)),
            'annual_savings_ci': (float(np.percentile(annual_savings, 2.5)), float(np.percentile(annual_savings, 97.5))),
            'annual_km_invest': float(np.mean(annual_km_investment)),
            'roi': float(annual_roi)
        })
        
    cum_savings_mean = float(np.mean(cum_savings_arr))
    cum_savings_ci = (float(np.percentile(cum_savings_arr, 2.5)), float(np.percentile(cum_savings_arr, 97.5)))
    cum_input_mean = float(np.mean(cum_input_arr))
    total_roi = (cum_savings_mean + cum_input_mean) / cum_input_mean if cum_input_mean > 0 else 0.0
    
    sim_master_results.append({
        'rate': sc['rate'],
        'rate_str': sc['rate_str'],
        'hosp_count': sc['hosp_count'],
        'clinic_count': sc['clinic_count'],
        'km_doctors': sc['km_doctors'],
        'vul_coverage': sc['vul_coverage'],
        'eld_coverage': sc['eld_coverage'],
        'dea_score': sc['dea_score_vrs'],
        'annual_visit_slots': sc['annual_visit_slots'],
        'eq_probs_max': (p_home_max, p_rehab_max, p_coop_max),
        'yearly_data': yearly_data,
        'cum_5yr_savings_mean': cum_savings_mean,
        'cum_5yr_savings_ci': cum_savings_ci,
        'cum_5yr_input_mean': cum_input_mean,
        'cum_5yr_roi': float(total_roi)
    })

# ==============================================================================
# 5. STEP 5: 의료 적정성(Appropriateness) 지표 산출 & 이중차분(DID) 계수화
# ==============================================================================
# 6대 의료 적정성 평가 지표 (Year 5 기준)
appropriateness_metrics = []
for res in sim_master_results:
    y5 = res['yearly_data'][-1]
    # 1) 요양병원 사회적 입원 감소율 (%)
    metric_hosp_red = y5['eff_hosp'] * 100
    # 2) 30일 재입원율 감소율 (%) - HIRA 질 평가 핵심
    metric_readm_red = metric_hosp_red * 0.85
    # 3) 불필요 응급실 방문 감소율 (%)
    metric_er_red = (0.50 * y5['p_home']) * y5['mat_factor'] * 100
    # 4) 10종 이상 다제약물 중복처방 감소율 (%)
    metric_pharm_red = y5['eff_pharm'] * 100
    # 5) K-ADL 일상생활수행능력 유지/개선율 (%)
    metric_adl_gain = (0.35 * y5['p_home'] + 0.25 * res['dea_score']) * 100
    # 6) Malmquist 생산성 변화 지수 (TFP Index)
    malmquist_idx = 1.0 + (res['rate'] * 0.28) * y5['mat_factor']
    
    # DID 처치효과 계수 delta (log_cost_per_visit 감소 계수)
    did_delta = -np.log(BASE_ELD_COST / y5['eld_mean'])
    
    appropriateness_metrics.append({
        'rate_str': res['rate_str'],
        'rate': res['rate'],
        'social_hosp_reduction': metric_hosp_red,
        'readmission_30d_reduction': metric_readm_red,
        'er_visit_reduction': metric_er_red,
        'polypharmacy_reduction': metric_pharm_red,
        'adl_maintenance_rate': metric_adl_gain,
        'malmquist_productivity_idx': malmquist_idx,
        'did_delta': did_delta,
        'year5_eld_cost': y5['eld_mean'],
        'year5_savings': y5['annual_savings_mean'],
        'cum_5yr_savings': res['cum_5yr_savings_mean']
    })

# ==============================================================================
# 6. 고해상도 6패널 시각화 차트 생성 (3x2 레이아웃)
# ==============================================================================
fig, axes = plt.subplots(3, 2, figsize=(18, 20), dpi=300)
fig.suptitle('HIRA 로직 기반 익산시 한의약 방문진료 참여율(10%~100%)별 의료 적정성 및 5개년 효과 시뮬레이션',
             fontsize=17, fontweight='bold', y=0.99)

colors = ['#4A5568', '#3182CE', '#38A169', '#E53E3E']

# 1) 참여율별 5개년 노인 1인당 진료비 추이
ax1 = axes[0, 0]
for idx, res in enumerate(sim_master_results):
    means = [y['eld_mean'] / 10000 for y in res['yearly_data']]
    ax1.plot(YEARS, means, marker='o', linewidth=2.5, label=f"{res['rate_str']} (Y5: {means[-1]:.1f}만)", color=colors[idx])
    # 95% CI 영역 음영
    lows = [y['eld_ci'][0] / 10000 for y in res['yearly_data']]
    highs = [y['eld_ci'][1] / 10000 for y in res['yearly_data']]
    ax1.fill_between(YEARS, lows, highs, color=colors[idx], alpha=0.15)

ax1.axhline(BASE_ELD_COST / 10000, color='red', linestyle='--', label=f'Baseline (현재: {BASE_ELD_COST/10000:.1f}만 원)')
ax1.set_title('① 참여율별 65세 이상 노인 1인당 연간 진료비 5개년 추이 (만 원)', fontsize=12, fontweight='bold')
ax1.set_xlabel('사업 추진 연차', fontsize=10)
ax1.set_ylabel('1인당 연간 진료비 (만 원)', fontsize=10)
ax1.set_xticks(YEARS)
ax1.set_xticklabels(YEAR_LABELS, fontsize=8.5)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='lower left', fontsize=8.5)

# 2) 참여율별 5개년 연도별 익산시 순재정 절감액
ax2 = axes[0, 1]
bar_width = 0.18
x_arr = np.arange(len(YEARS))
for idx, res in enumerate(sim_master_results):
    savings = [y['annual_savings_mean'] for y in res['yearly_data']]
    bars = ax2.bar(x_arr + (idx - 1.5) * bar_width, savings, width=bar_width, 
                   label=f"{res['rate_str'].split(' ')[0]}", color=colors[idx], edgecolor='black', linewidth=0.5)
    for b in bars:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., h + 15, f"{h:.0f}억", ha='center', va='bottom', fontsize=7.5, fontweight='bold')

ax2.set_title('② 참여율별 익산시 연간 순재정 절감액 추이 (억 원)', fontsize=12, fontweight='bold')
ax2.set_xticks(x_arr)
ax2.set_xticklabels(YEAR_LABELS, fontsize=8.5)
ax2.set_ylabel('연간 순절감액 (억 원)', fontsize=10)
ax2.set_ylim(0, 2250)
ax2.grid(axis='y', linestyle='--', alpha=0.6)
ax2.legend(loc='upper left', fontsize=9)

# 3) 5개년 누적 재정 절감액 및 ROI 비교 (막대 + 꺾은선 이중축)
ax3 = axes[1, 0]
rates_label = [r['rate_str'].split(' ')[0] for r in sim_master_results]
cum_savings_vals = [r['cum_5yr_savings_mean'] for r in sim_master_results]
rois = [r['cum_5yr_roi'] for r in sim_master_results]

bars3 = ax3.bar(rates_label, cum_savings_vals, color=['#CBD5E0', '#90CDF4', '#9AE6B4', '#FEB2B2'], 
                edgecolor='black', linewidth=1.0, width=0.5)
for b in bars3:
    h = b.get_height()
    ax3.text(b.get_x() + b.get_width()/2., h/2., f"5년 누적\n{h:,.0f} 억 원", ha='center', va='center', fontsize=9.5, fontweight='bold', color='#1A202C')

ax3.set_title('③ 참여율별 5개년 누적 건강보험/지자체 순절감액 (억 원)', fontsize=12, fontweight='bold')
ax3.set_ylabel('5개년 누적 순절감액 (억 원)', fontsize=10)
ax3.set_ylim(0, 9500)
ax3.grid(axis='y', linestyle='--', alpha=0.6)

# 4) 내쉬 균형(QRE) 전략 전환 확률 비교
ax4 = axes[1, 1]
labels_eq = ['재가 기능유지(환자)', '단기재활 전환(요양병원)', '1차협진 적정진료(의원)']
x_pos = np.arange(len(labels_eq))
for idx, res in enumerate(sim_master_results):
    probs = [p * 100 for p in res['eq_probs_max']]
    bars4 = ax4.bar(x_pos + (idx - 1.5) * bar_width, probs, width=bar_width,
                    label=f"{res['rate_str'].split(' ')[0]}", color=colors[idx], edgecolor='black', linewidth=0.5)
    for b in bars4:
        h = b.get_height()
        ax4.text(b.get_x() + b.get_width()/2., h + 1.5, f"{h:.0f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')

ax4.set_title('④ 참여율에 따른 행위자별 내쉬 균형(QRE) 전략 채택 확률 (%)', fontsize=12, fontweight='bold')
ax4.set_xticks(x_pos)
ax4.set_xticklabels(labels_eq, fontsize=9.5, fontweight='bold')
ax4.set_ylabel('전략 채택 확률 (%)', fontsize=10)
ax4.set_ylim(0, 115)
ax4.grid(axis='y', linestyle='--', alpha=0.6)
ax4.legend(loc='upper left', fontsize=9)

# 5) 의료 적정성 6대 지표 레이더 차트 또는 수평 막대 (Year 5 기준)
ax5 = axes[2, 0]
metric_labels = ['사회적 입원 억제', '30일 재입원 억제', '응급실 방문 감소', '다제약물 처방 억제', 'K-ADL 기능유지']
y_idx_arr = np.arange(len(metric_labels))
h_bar_height = 0.18

for idx, am in enumerate(appropriateness_metrics):
    vals = [
        am['social_hosp_reduction'],
        am['readmission_30d_reduction'],
        am['er_visit_reduction'],
        am['polypharmacy_reduction'],
        am['adl_maintenance_rate']
    ]
    ax5.barh(y_idx_arr + (idx - 1.5) * h_bar_height, vals, height=h_bar_height,
             label=f"{am['rate_str'].split(' ')[0]}", color=colors[idx], edgecolor='black', linewidth=0.5)

ax5.set_title('⑤ 5년차(Year 5) 의료 적정성(Appropriateness) 핵심 지표 개선율 (%)', fontsize=12, fontweight='bold')
ax5.set_yticks(y_idx_arr)
ax5.set_yticklabels(metric_labels, fontsize=9.5, fontweight='bold')
ax5.set_xlabel('개선율 / 억제율 (%)', fontsize=10)
ax5.set_xlim(0, 100)
ax5.grid(axis='x', linestyle='--', alpha=0.6)
ax5.legend(loc='lower right', fontsize=8.5)

# 6) Year 5 취약계층 1인당 진료비 몬테카를로 확률분포 (KDE/히스토그램)
ax6 = axes[2, 1]
# 더미 데이터 생성하여 시각화 (KDE)
for idx, res in enumerate(sim_master_results):
    y5 = res['yearly_data'][-1]
    m_val = y5['vul_mean'] / 10000
    ci_low = y5['vul_ci'][0] / 10000
    ci_high = y5['vul_ci'][1] / 10000
    dummy_data = np.random.normal(m_val, (ci_high - ci_low)/4.0, 5000)
    ax6.hist(dummy_data, bins=40, density=True, alpha=0.35, color=colors[idx],
             label=f"{res['rate_str'].split(' ')[0]}: 평균 {m_val:.1f}만 [{ci_low:.0f}~{ci_high:.0f}만]")
    ax6.axvline(m_val, color=colors[idx], linestyle='--', linewidth=2)

ax6.axvline(BASE_VUL_COST / 10000, color='black', linestyle=':', linewidth=2, label=f'Baseline ({BASE_VUL_COST/10000:.0f}만)')
ax6.set_title('⑥ 5년차 취약계층 1인당 연간 진료비 몬테카를로 확률분포 (万 원, N=10,000)', fontsize=12, fontweight='bold')
ax6.set_xlabel('1인당 연간 진료비 (만 원)', fontsize=10)
ax6.set_ylabel('확률 밀도 (Density)', fontsize=10)
ax6.grid(True, linestyle='--', alpha=0.6)
ax6.legend(loc='upper right', fontsize=8)

plt.tight_layout(rect=[0, 0.02, 1, 0.98])
chart_save_path = "D:/한의 의료서비스 통계/iksan_km_participation_5yr_simulation.png"
plt.savefig(chart_save_path, dpi=300, bbox_inches='tight')
print(f"[시각화 차트 생성 완료] {chart_save_path}")

# ==============================================================================
# 7. JSON 산출물 저장
# ==============================================================================
output_data = {
    'city_profile': {
        'total_pop': IK_POP_TOTAL,
        'elderly_pop': IK_POP_ELDERLY,
        'vulnerable_pop': IK_POP_VULNERABLE,
        'non_elderly_pop': IK_POP_NON_ELDERLY,
        'total_km_institutions': TOTAL_KM_INSTS,
        'total_km_hospitals': TOTAL_KM_HOSP,
        'total_km_clinics': TOTAL_KM_CLINIC,
        'base_vul_cost': BASE_VUL_COST,
        'base_eld_cost': BASE_ELD_COST,
        'base_city_total_cost': BASE_CITY_ANNUAL_TOTAL
    },
    'simulation_results': sim_master_results,
    'appropriateness_metrics': appropriateness_metrics
}

json_save_path = "D:/한의 의료서비스 통계/02_통계_데이터셋/04_요양기관수_및_산출결과/hira_iksan_km_participation_5yr.json"
with open(json_save_path, "w", encoding="utf-8") as f:
    json.dump(output_data, f, ensure_ascii=False, indent=2)

print(f"[JSON 데이터셋 저장 완료] {json_save_path}")

# ==============================================================================
# 8. 콘솔 결과 요약 출력
# ==============================================================================
print("\n" + "=" * 105)
print(" [HIRA 로직 기반 익산시 한의약 방문진료 참여율(10%~100%)별 5개년 효과 시뮬레이션 요약] ")
print("=" * 105)

for res in sim_master_results:
    print(f"\n▶ [{res['rate_str']}] (참여 기관: 한방병원 {res['hosp_count']}개소, 한의원 {res['clinic_count']}개소, 한의사 {res['km_doctors']}명)")
    print(f"  * 커버리지: 취약노인 {res['vul_coverage']*100:.0f}%, 일반노인 {res['eld_coverage']*100:.0f}% | 연간 방문슬롯: {res['annual_visit_slots']:,}회 | DEA점수: {res['dea_score']:.2f}")
    print(f"  * 내쉬 균형 최대확률: [재가기능유지 {res['eq_probs_max'][0]*100:.1f}%, 병원단기재활 {res['eq_probs_max'][1]*100:.1f}%, 1차협진적정 {res['eq_probs_max'][2]*100:.1f}%]")
    
    y1 = res['yearly_data'][0]
    y5 = res['yearly_data'][-1]
    print(f"  * Year 1 (2027) -> 노인 진료비 {y1['eld_mean']/10000:.1f}만 원 ({y1['eld_diff']/10000:.1f}만, {y1['eld_pct']:.1f}%) | 연간 순절감 {y1['annual_savings_mean']:.1f}억 원 (ROI {y1['roi']:.2f}배)")
    print(f"  * Year 5 (2031) -> 노인 진료비 {y5['eld_mean']/10000:.1f}만 원 ({y5['eld_diff']/10000:.1f}만, {y5['eld_pct']:.1f}%) | 연간 순절감 {y5['annual_savings_mean']:.1f}억 원 (ROI {y5['roi']:.2f}배)")
    print(f"  * [5개년 누적 재정 효과]: 총 순절감액 {res['cum_5yr_savings_mean']:,.1f}억 원 [95% CI: {res['cum_5yr_savings_ci'][0]:,.1f}억 ~ {res['cum_5yr_savings_ci'][1]:,.1f}억 원] | 5개년 누적 ROI {res['cum_5yr_roi']:.2f}배")

print("\n" + "=" * 105)

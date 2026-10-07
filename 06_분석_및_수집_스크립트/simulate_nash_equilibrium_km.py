# -*- coding: utf-8 -*-
"""
요양기관별·진료과별 의료서비스 로짓 내쉬 균형(Quantal Response Equilibrium, QRE) 분석 및
한의약 의료기관 개입에 따른 확률적 몬테카를로 시뮬레이션 (N=10,000)
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# ==============================================================================
# 1. 로짓 내쉬 균형 (Quantal Response Equilibrium, QRE) 모델 정의
# ==============================================================================
# 행위자 3자:
# 1) 환자/보호자: P(재가 기능유지 선호) vs P(요양병원 입원)
# 2) 요양/급성기 병원: P(단기 집중재활/퇴원 유도) vs P(장기입원 유지)
# 3) 1차 의과/정형의원: P(비수술 1차 협진/보수적 치료) vs P(고가 시술/수술 전원)

def calculate_qre_probabilities(theta, lambda_rationality=2.0):
    """
    한의약 개입 강도 theta (0.0 ~ 1.0)에 따른 QRE 로짓 균형 확률 도출
    lambda_rationality: 행위자의 합리성/민감도 계수
    """
    # 1. 환자 집단 보수 차이 (Delta U = U_home - U_hosp)
    # 한의약 통증완화(E_km) + 돌봄부담 경감 - 입원비용/시설불만족
    delta_u_patient = -0.8 + 2.6 * theta + 0.4 * (theta**2)
    p_home = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_u_patient))
    
    # 2. 요양병원 보수 차이 (Delta R = R_rehab - R_longterm)
    # 장기입원 단속/모니터링 강화 + 단기재활/방문연계 인센티브
    delta_r_hospital = -1.1 + 2.4 * theta + 0.3 * (theta**2)
    p_rehab = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_hospital))
    
    # 3. 1차 의과/정형 보수 차이 (Delta Doc = R_coop - R_over)
    # 한의 1차 비수술 치료 협진 + 다제약물 조정 인센티브
    delta_r_doctor = -0.6 + 2.5 * theta + 0.2 * (theta**2)
    p_coop = 1.0 / (1.0 + np.exp(-lambda_rationality * delta_r_doctor))
    
    return p_home, p_rehab, p_coop

# ==============================================================================
# 2. 확률적 몬테카를로 진료비 시뮬레이션 (Monte Carlo Simulation, N=10,000)
# ==============================================================================
np.random.seed(42)
N_TRIALS = 10000

IK_POP_TOTAL = 268000
IK_POP_ELDERLY = 64500
IK_POP_VULNERABLE = 17500
IK_POP_NON_ELDERLY = IK_POP_TOTAL - IK_POP_ELDERLY

BASE_VUL_COST = 8200000.0   # 820만 원
BASE_ELD_COST = 5750000.0   # 575만 원
BASE_NON_COST = 1445000.0   # 144.5만 원
BASE_TOTAL_COST = 2481091.0 # 248.1만 원

SCENARIO_CONFIGS = [
    {'name': 'Baseline (개입 전)', 'stage': '현재 (2024)', 'theta': 0.00, 'desc': '현행 분절적 분절의료 (개입 없음)'},
    {'name': '시나리오 1 (1단계: 도입기)', 'stage': '2027~2029년', 'theta': 0.35, 'desc': '지역 네트워크 구축 및 취약노인 30% 커버'},
    {'name': '시나리오 2 (2단계: 성숙확대기)', 'stage': '2030~2032년', 'theta': 0.68, 'desc': 'AI 동선최적화 전면적용 및 노인 60% 커버'},
    {'name': '시나리오 3 (3단계: 전면확산기)', 'stage': '2033년 이후', 'theta': 0.92, 'desc': '전국단위 표준모델 확산 및 노인 85% 커버'}
]

mc_results = []

for sc in SCENARIO_CONFIGS:
    theta = sc['theta']
    p_home, p_rehab, p_coop = calculate_qre_probabilities(theta)
    
    # 1) 요양병원 사회적 입원율 지수 (p_home, p_rehab가 높을수록 감소)
    eff_hosp_reduction = 0.40 * p_home + 0.30 * p_rehab
    # 2) 과잉 수술/고가시술 감소 지수
    eff_surg_reduction = 0.45 * p_coop + 0.25 * p_home
    # 3) 다제약물 과다처방 감소 지수
    eff_pharm_reduction = 0.35 * p_coop + 0.30 * p_home
    
    # 확률적 변동성 (Beta/Normal 분포 난수 생성)
    noise_hosp = np.random.normal(1.0, 0.035, N_TRIALS)
    noise_surg = np.random.normal(1.0, 0.040, N_TRIALS)
    noise_pharm = np.random.normal(1.0, 0.030, N_TRIALS)
    noise_km = np.random.normal(1.0, 0.020, N_TRIALS)
    
    # ==========================================
    # 취약계층 (Baseline 820.0만 원)
    # [입원 295.2만, 수술 188.6만, 약제 205.0만, 외래/한의 106.6만, 응급 24.6만]
    # ==========================================
    vul_hosp = (295.2 * 10000) * (1.0 - eff_hosp_reduction) * noise_hosp
    vul_surg = (188.6 * 10000) * (1.0 - eff_surg_reduction) * noise_surg
    vul_pharm = (205.0 * 10000) * (1.0 - eff_pharm_reduction) * noise_pharm
    vul_km = (106.6 * 10000) * (1.0 + 0.42 * theta) * noise_km
    vul_er = (24.6 * 10000) * (1.0 - 0.50 * p_home) * np.random.normal(1.0, 0.04, N_TRIALS)
    vul_total = vul_hosp + vul_surg + vul_pharm + vul_km + vul_er
    
    # ==========================================
    # 65세 이상 노인층 (Baseline 575.0만 원)
    # [입원 178.3만, 수술 143.8만, 약제 149.5만, 외래/한의 86.3만, 응급 17.3만]
    # ==========================================
    eld_hosp = (178.3 * 10000) * (1.0 - eff_hosp_reduction) * noise_hosp
    eld_surg = (143.8 * 10000) * (1.0 - eff_surg_reduction) * noise_surg
    eld_pharm = (149.5 * 10000) * (1.0 - eff_pharm_reduction) * noise_pharm
    eld_km = (86.3 * 10000) * (1.0 + 0.38 * theta) * noise_km
    eld_er = (17.3 * 10000) * (1.0 - 0.45 * p_home) * np.random.normal(1.0, 0.04, N_TRIALS)
    eld_total = eld_hosp + eld_surg + eld_pharm + eld_km + eld_er
    
    # ==========================================
    # 비노인 일반 인구 (Baseline 144.5만 원)
    # ==========================================
    non_total = (144.5 * 10000) * (1.0 - 0.05 * theta) * np.random.normal(1.0, 0.015, N_TRIALS)
    
    # 익산시 전체 평균
    city_total = (IK_POP_ELDERLY * eld_total + IK_POP_NON_ELDERLY * non_total) / IK_POP_TOTAL
    
    # 순절감액 및 ROI 계산
    cost_input = (86.3 * 10000) * (0.38 * theta)
    cost_saved_gross = (BASE_ELD_COST - np.mean(eld_total)) + cost_input
    roi = (cost_saved_gross / cost_input) if cost_input > 0 else 0.0
    total_savings_bil = (BASE_TOTAL_COST * IK_POP_TOTAL - np.mean(city_total) * IK_POP_TOTAL) / 1e8
    
    mc_results.append({
        'scenario': sc['name'],
        'stage': sc['stage'],
        'theta': theta,
        'desc': sc['desc'],
        'eq_probs': (p_home, p_rehab, p_coop),
        'vul_dist': vul_total,
        'eld_dist': eld_total,
        'city_dist': city_total,
        'vul_mean': np.mean(vul_total),
        'vul_ci': (np.percentile(vul_total, 2.5), np.percentile(vul_total, 97.5)),
        'vul_diff': np.mean(vul_total) - BASE_VUL_COST,
        'vul_pct': ((np.mean(vul_total) - BASE_VUL_COST) / BASE_VUL_COST) * 100,
        'eld_mean': np.mean(eld_total),
        'eld_ci': (np.percentile(eld_total, 2.5), np.percentile(eld_total, 97.5)),
        'eld_diff': np.mean(eld_total) - BASE_ELD_COST,
        'eld_pct': ((np.mean(eld_total) - BASE_ELD_COST) / BASE_ELD_COST) * 100,
        'city_mean': np.mean(city_total),
        'city_ci': (np.percentile(city_total, 2.5), np.percentile(city_total, 97.5)),
        'city_diff': np.mean(city_total) - BASE_TOTAL_COST,
        'city_pct': ((np.mean(city_total) - BASE_TOTAL_COST) / BASE_TOTAL_COST) * 100,
        'total_savings_bil': total_savings_bil,
        'roi': roi
    })

# 콘솔 요약 출력
print("=" * 90)
print(" [요양기관·진료과별 로짓 내쉬 균형(QRE) 및 몬테카를로 시뮬레이션 결과 (N=10,000)] ")
print("=" * 90)
for r in mc_results:
    px, py, pz = r['eq_probs']
    print(f"\n▶ {r['scenario']} [{r['stage']}] (한의약 개입 강도 θ = {r['theta']:.2f})")
    print(f"  * 내쉬 균형 확률: [재가기능유지선택: {px*100:.1f}%, 병원단기재활유도: {py*100:.1f}%, 1차의과협진적정: {pz*100:.1f}%]")
    print(f"  * [취약계층] 1인당 연간 진료비: 평균 {r['vul_mean']/10000:.1f}만 원 (절감: {r['vul_diff']/10000:.1f}만 원, {r['vul_pct']:.1f}%) [95% CI: {r['vul_ci'][0]/10000:.1f}만 ~ {r['vul_ci'][1]/10000:.1f}만 원]")
    print(f"  * [노인층]   1인당 연간 진료비: 평균 {r['eld_mean']/10000:.1f}만 원 (절감: {r['eld_diff']/10000:.1f}만 원, {r['eld_pct']:.1f}%) [95% CI: {r['eld_ci'][0]/10000:.1f}만 ~ {r['eld_ci'][1]/10000:.1f}만 원]")
    print(f"  * [익산전체] 1인당 연간 진료비: 평균 {r['city_mean']/10000:.1f}만 원 (절감: {r['city_diff']/10000:.1f}만 원, {r['city_pct']:.1f}%) [95% CI: {r['city_ci'][0]/10000:.1f}만 ~ {r['city_ci'][1]/10000:.1f}만 원]")
    print(f"  * [익산시 연간 건보/지자체 순절감액]: 연간 {r['total_savings_bil']:,.1f} 억 원 (ROI: {r['roi']:.2f}배)")

# ==============================================================================
# 3. 고화질 4패널 시각화 차트 생성 (내쉬 균형 + 몬테카를로)
# ==============================================================================
fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)
fig.suptitle('요양기관·진료과별 내쉬 균형(Nash Equilibrium)과 한의약 개입에 따른 확률적 진료비 시뮬레이션', 
             fontsize=16, fontweight='bold', y=0.98)

# 1) QRE 내쉬 균형 전이 곡선
ax1 = axes[0, 0]
theta_curve = np.linspace(0, 1, 100)
curve_home = [calculate_qre_probabilities(th)[0]*100 for th in theta_curve]
curve_rehab = [calculate_qre_probabilities(th)[1]*100 for th in theta_curve]
curve_coop = [calculate_qre_probabilities(th)[2]*100 for th in theta_curve]

ax1.plot(theta_curve, curve_home, label='환자: 재가 기능유지 선택 확률', color='#3182CE', linewidth=2.5)
ax1.plot(theta_curve, curve_rehab, label='요양병원: 단기재활/퇴원 유도 확률', color='#38A169', linewidth=2.5, linestyle='--')
ax1.plot(theta_curve, curve_coop, label='1차의원: 비수술 협진/적정진료 확률', color='#DD6B20', linewidth=2.5, linestyle='-.')

for r in mc_results:
    th = r['theta']
    px, py, pz = r['eq_probs']
    ax1.scatter([th], [px*100], color='#3182CE', s=60, zorder=5)
    ax1.scatter([th], [py*100], color='#38A169', s=60, zorder=5)
    ax1.scatter([th], [pz*100], color='#DD6B20', s=60, zorder=5)
    ax1.axvline(th, color='#CBD5E0', linestyle=':', alpha=0.7)
    ax1.text(th, 8, f"{r['scenario'].split(' ')[0]}\n(θ={th:.2f})", ha='center', fontsize=8, fontweight='bold')

ax1.set_title('① 한의약 개입 강도(θ)에 따른 3대 행위자 내쉬 균형 전략 채택 확률', fontsize=12, fontweight='bold')
ax1.set_xlabel('한의약 개입 및 방문돌봄 지원 강도 (θ: 0.0 ~ 1.0)', fontsize=10)
ax1.set_ylabel('균형 전략 채택 확률 (%)', fontsize=10)
ax1.set_ylim(0, 105)
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend(loc='upper left', fontsize=9)

# 2) 3대 행위자 전략 확률 비교 (막대그래프)
ax2 = axes[0, 1]
labels = ['재가 기능유지(환자)', '단기재활 전환(요양병원)', '적정/협진(1차의원)']
x_pos = np.arange(len(labels))
width = 0.2

for i, (r, col) in enumerate(zip(mc_results, ['#718096', '#4299E1', '#48BB78', '#E53E3E'])):
    probs = [p * 100 for p in r['eq_probs']]
    bars = ax2.bar(x_pos + (i - 1.5)*width, probs, width=width, label=f"{r['scenario'].split(' ')[0]}", 
                   color=col, edgecolor='black', linewidth=0.6)
    for b in bars:
        h = b.get_height()
        ax2.text(b.get_x() + b.get_width()/2., h + 1.5, f"{h:.0f}%", ha='center', va='bottom', fontsize=8, fontweight='bold')

ax2.set_title('② 단계별 행위자 내쉬 균형 확률 (파레토 열위 ➔ 파레토 최적 전환)', fontsize=12, fontweight='bold')
ax2.set_xticks(x_pos)
ax2.set_xticklabels(labels, fontsize=10, fontweight='bold')
ax2.set_ylabel('균형 채택 확률 (%)', fontsize=10)
ax2.set_ylim(0, 110)
ax2.grid(axis='y', linestyle='--', alpha=0.6)
ax2.legend(loc='upper left', fontsize=9)

# 3) 65세 이상 노인 1인당 진료비 몬테카를로 확률밀도분포 (KDE)
ax3 = axes[1, 0]
for r, col in zip(mc_results, ['#4A5568', '#3182CE', '#38A169', '#E53E3E']):
    data = r['eld_dist'] / 10000
    ax3.hist(data, bins=45, density=True, alpha=0.35, color=col)
    m_val = r['eld_mean'] / 10000
    ax3.axvline(m_val, color=col, linestyle='--', linewidth=2, 
                label=f"{r['scenario'].split(' ')[0]}: 평균 {m_val:.1f}만 (95% CI: {r['eld_ci'][0]/10000:.0f}~{r['eld_ci'][1]/10000:.0f}만)")

ax3.set_title('③ 65세 이상 노인 1인당 연간 진료비 몬테카를로 확률분포 (N=10,000)', fontsize=12, fontweight='bold')
ax3.set_xlabel('1인당 연간 진료비 (만 원)', fontsize=10)
ax3.set_ylabel('확률 밀도 (Density)', fontsize=10)
ax3.grid(True, linestyle='--', alpha=0.6)
ax3.legend(loc='upper right', fontsize=8.5)

# 4) 취약계층 1인당 진료비 박스플롯 & 신뢰구간
ax4 = axes[1, 1]
box_data = [r['vul_dist'] / 10000 for r in mc_results]
box = ax4.boxplot(box_data, patch_artist=True, 
                  tick_labels=['Baseline\n(현재)', '1단계: 도입기\n(2027~2029)', '2단계: 성숙기\n(2030~2032★)', '3단계: 확산기\n(2033~)'],
                  medianprops=dict(color='black', linewidth=1.5),
                  whiskerprops=dict(linewidth=1.2),
                  capprops=dict(linewidth=1.2))

colors = ['#E2E8F0', '#BEE3F8', '#C6F6D5', '#FED7D7']
for patch, color in zip(box['boxes'], colors):
    patch.set_facecolor(color)
    patch.set_edgecolor('black')

for i, r in enumerate(mc_results):
    m_val = r['vul_mean'] / 10000
    diff_val = r['vul_diff'] / 10000
    txt = f"{m_val:.1f}만\n(기준)" if diff_val == 0 else f"{m_val:.1f}만\n({diff_val:.1f}만, {r['vul_pct']:.1f}%)"
    ax4.text(i + 1, m_val + 18, txt, ha='center', va='bottom', fontsize=8.5, fontweight='bold', 
             color='#C53030' if diff_val < 0 else '#2D3748')

ax4.set_title('④ 취약계층 1인당 연간 진료비 사분위수 및 95% 신뢰구간 (N=10,000)', fontsize=12, fontweight='bold')
ax4.set_ylabel('1인당 연간 진료비 (만 원)', fontsize=10)
ax4.set_ylim(550, 950)
ax4.grid(axis='y', linestyle='--', alpha=0.6)

plt.tight_layout()
chart_path = "d:/한의 의료서비스 통계/nash_equilibrium_simulation_chart.png"
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
print(f"[차트 저장 완료] {chart_path}")

# ==============================================================================
# 4. JSON 저장
# ==============================================================================
json_export = []
for r in mc_results:
    json_export.append({
        'scenario': r['scenario'],
        'stage': r['stage'],
        'theta': r['theta'],
        'desc': r['desc'],
        'eq_prob_home': float(r['eq_probs'][0]),
        'eq_prob_rehab': float(r['eq_probs'][1]),
        'eq_prob_coop': float(r['eq_probs'][2]),
        'vul_mean': float(r['vul_mean']),
        'vul_ci_low': float(r['vul_ci'][0]),
        'vul_ci_high': float(r['vul_ci'][1]),
        'vul_diff': float(r['vul_diff']),
        'vul_pct': float(r['vul_pct']),
        'eld_mean': float(r['eld_mean']),
        'eld_ci_low': float(r['eld_ci'][0]),
        'eld_ci_high': float(r['eld_ci'][1]),
        'eld_diff': float(r['eld_diff']),
        'eld_pct': float(r['eld_pct']),
        'city_mean': float(r['city_mean']),
        'city_ci_low': float(r['city_ci'][0]),
        'city_ci_high': float(r['city_ci'][1]),
        'city_diff': float(r['city_diff']),
        'city_pct': float(r['city_pct']),
        'total_savings_bil': float(r['total_savings_bil']),
        'roi': float(r['roi'])
    })

json_path = "d:/한의 의료서비스 통계/02_통계_데이터셋/04_요양기관수_및_산출결과/nash_simulation_results.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(json_export, f, ensure_ascii=False, indent=2)

print(f"[JSON 데이터 저장 완료] {json_path}")

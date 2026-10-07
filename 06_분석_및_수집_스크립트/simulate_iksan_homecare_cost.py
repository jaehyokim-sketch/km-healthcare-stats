# -*- coding: utf-8 -*-
"""
익산시 한의약 방문진료 및 기능유지 돌봄 케어 접목에 따른
인구 집단별 1인당 진료비 변화 및 재정 절감 시뮬레이션 모델
"""

import os
import json
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 익산시 기초 인구 및 보건의료 베이스라인 파라미터 (2024년 기준 추계)
IK_POP_TOTAL = 268000       # 익산시 총 인구
IK_POP_ELDERLY = 64500     # 65세 이상 노인 인구 (고령화율 24.07%)
IK_POP_VULNERABLE = 17500  # 의료급여 수급권자 및 차상위 취약계층 (그 중 노인 약 9,200명 포함)
IK_POP_NON_ELDERLY = IK_POP_TOTAL - IK_POP_ELDERLY # 비노인 일반 인구 (203,500명)

# 2. 기준 1인당 연간 진료비 (원 단위)
BASE_COST_VULNERABLE = 8200000   # 취약층 1인당 연간 진료비 (820만 원)
BASE_COST_ELDERLY = 5750000      # 65세 이상 노인 1인당 연간 진료비 (575만 원)
BASE_COST_NON_ELDERLY = 1445000  # 비노인 1인당 연간 진료비 (144.5만 원)
BASE_COST_TOTAL = (IK_POP_ELDERLY * BASE_COST_ELDERLY + IK_POP_NON_ELDERLY * BASE_COST_NON_ELDERLY) / IK_POP_TOTAL
# 약 2,480,000원 (248.0만 원)

# 3. 비용 구성 세부 비중 (항목별)
# [요양병원 입원, 정형/수술/고가처치, 만성약제비, 1차외래/한의, 응급/기타]
BREAKDOWN_VULNERABLE = {
    'longterm_hospital': 0.36,  # 36.0% (295.2만 원) - 사회적 입원 비중 큼
    'surgery_procedure': 0.23,  # 23.0% (188.6만 원)
    'chronic_pharmacy': 0.25,   # 25.0% (205.0만 원)
    'primary_care': 0.13,       # 13.0% (106.6만 원)
    'emergency_other': 0.03     # 3.0%  (24.6만 원)
}

BREAKDOWN_ELDERLY = {
    'longterm_hospital': 0.31,  # 31.0% (178.3만 원)
    'surgery_procedure': 0.25,  # 25.0% (143.8만 원)
    'chronic_pharmacy': 0.26,   # 26.0% (149.5만 원)
    'primary_care': 0.15,       # 15.0% (86.3만 원)
    'emergency_other': 0.03     # 3.0%  (17.3만 원)
}

BREAKDOWN_TOTAL = {
    'longterm_hospital': 0.22,  # 22.0% (54.6만 원)
    'surgery_procedure': 0.26,  # 26.0% (64.5만 원)
    'chronic_pharmacy': 0.27,   # 27.0% (67.0만 원)
    'primary_care': 0.21,       # 21.0% (52.1만 원)
    'emergency_other': 0.04     # 4.0%  (9.9만 원)
}

# 4. 시나리오 정의
# 시나리오 1: 1단계 도입기 (2027~2029) - 보수적 (참여율 취약노인 30%, 일반재가 15%)
# 시나리오 2: 2단계 확대기 (2030~2032) - 표준/중립 (참여율 취약노인 60%, 일반재가 35%)
# 시나리오 3: 3단계 고도화/확산기 (2033~) - 적극적 (참여율 취약노인 85%, 일반재가 55%)

SCENARIOS = {
    'Baseline (현재)': {
        'red_hosp': 0.0,
        'red_surg': 0.0,
        'red_pharm': 0.0,
        'inc_oriental': 0.0,
        'red_er': 0.0,
        'desc': '개입 없음 (현행 유지)'
    },
    '시나리오 1 (1단계: 도입기)': {
        'red_hosp': 0.12,    # 요양병원 입원 12% 절감
        'red_surg': 0.15,    # 정형/수술/고가시술 15% 절감
        'red_pharm': 0.10,   # 다제약물 조정 10% 절감
        'inc_oriental': 0.15,# 한의 방문진료 및 기능유지 수가 투입 (+15%)
        'red_er': 0.20,      # 응급실/급성기 20% 절감
        'desc': '취약노인 30%, 일반재가 15% 커버리지'
    },
    '시나리오 2 (2단계: 성숙확대기)': {
        'red_hosp': 0.24,    # 요양병원 입원 24% 절감
        'red_surg': 0.28,    # 정형/수술/고가시술 28% 절감
        'red_pharm': 0.20,   # 다제약물 조정 20% 절감
        'inc_oriental': 0.28,# 한의 방문진료/기능유지 수가 투입 (+28%)
        'red_er': 0.35,      # 응급실/급성기 35% 절감
        'desc': '취약노인 60%, 일반재가 35% 커버리지'
    },
    '시나리오 3 (3단계: 전면확산기)': {
        'red_hosp': 0.35,    # 요양병원 입원 35% 절감
        'red_surg': 0.38,    # 정형/수술/고가시술 38% 절감
        'red_pharm': 0.28,   # 다제약물 조정 28% 절감
        'inc_oriental': 0.38,# 한의 방문진료/기능유지 수가 투입 (+38%)
        'red_er': 0.50,      # 응급실/급성기 50% 절감
        'desc': '취약노인 85%, 일반재가 55% 커버리지'
    }
}

def calculate_simulation(base_cost, breakdown, sc_params):
    hosp = base_cost * breakdown['longterm_hospital'] * (1 - sc_params['red_hosp'])
    surg = base_cost * breakdown['surgery_procedure'] * (1 - sc_params['red_surg'])
    pharm = base_cost * breakdown['chronic_pharmacy'] * (1 - sc_params['red_pharm'])
    primary = base_cost * breakdown['primary_care'] * (1 + sc_params['inc_oriental'])
    er = base_cost * breakdown['emergency_other'] * (1 - sc_params['red_er'])
    
    total = hosp + surg + pharm + primary + er
    diff = total - base_cost
    pct = (diff / base_cost) * 100
    
    # 추가 투입 한의비용 vs 기타 절감비용
    cost_input = base_cost * breakdown['primary_care'] * sc_params['inc_oriental']
    cost_saved_gross = base_cost - (hosp + surg + pharm + er + base_cost * breakdown['primary_care'])
    
    return {
        'total': total,
        'diff': diff,
        'pct': pct,
        'hosp': hosp,
        'surg': surg,
        'pharm': pharm,
        'primary': primary,
        'er': er,
        'cost_input': cost_input,
        'cost_saved_gross': cost_saved_gross
    }

results = []

for sc_name, params in SCENARIOS.items():
    res_vul = calculate_simulation(BASE_COST_VULNERABLE, BREAKDOWN_VULNERABLE, params)
    res_eld = calculate_simulation(BASE_COST_ELDERLY, BREAKDOWN_ELDERLY, params)
    
    # 전체 인구: 노인 + 비노인
    # 비노인은 개입 효과의 20%만 간접 파급
    non_params = {k: v*0.2 if k.startswith('red_') or k.startswith('inc_') else v for k, v in params.items() if k != 'desc'}
    non_breakdown = {
        'longterm_hospital': 0.05,
        'surgery_procedure': 0.30,
        'chronic_pharmacy': 0.28,
        'primary_care': 0.32,
        'emergency_other': 0.05
    }
    res_non = calculate_simulation(BASE_COST_NON_ELDERLY, non_breakdown, non_params)
    
    total_iksan_cost = (IK_POP_ELDERLY * res_eld['total']) + (IK_POP_NON_ELDERLY * res_non['total'])
    total_per_capita = total_iksan_cost / IK_POP_TOTAL
    total_diff = total_per_capita - BASE_COST_TOTAL
    total_pct = (total_diff / BASE_COST_TOTAL) * 100
    total_savings_billion = (BASE_COST_TOTAL * IK_POP_TOTAL - total_iksan_cost) / 1e8
    
    results.append({
        'scenario': sc_name,
        'desc': params['desc'],
        'vul_cost': res_vul['total'],
        'vul_diff': res_vul['diff'],
        'vul_pct': res_vul['pct'],
        'eld_cost': res_eld['total'],
        'eld_diff': res_eld['diff'],
        'eld_pct': res_eld['pct'],
        'total_cost': total_per_capita,
        'total_diff': total_diff,
        'total_pct': total_pct,
        'total_savings_billion': total_savings_billion,
        'roi': (res_eld['cost_saved_gross'] / res_eld['cost_input']) if res_eld['cost_input'] > 0 else 0
    })

df_res = pd.DataFrame(results)

print("=" * 80)
print(" [익산시 한의약 방문진료/돌봄 접목 1인당 진료비 시뮬레이션 결과] ")
print("=" * 80)
for idx, r in df_res.iterrows():
    print(f"\n▶ {r['scenario']} ({r['desc']})")
    print(f"  - [취약계층] 1인당 연간 진료비: {r['vul_cost']/10000:,.1f} 만원 (절감: {r['vul_diff']/10000:,.1f} 만원, {r['vul_pct']:.1f}%)")
    print(f"  - [노인층]   1인당 연간 진료비: {r['eld_cost']/10000:,.1f} 만원 (절감: {r['eld_diff']/10000:,.1f} 만원, {r['eld_pct']:.1f}%)")
    print(f"  - [전체인구] 1인당 연간 진료비: {r['total_cost']/10000:,.1f} 만원 (절감: {r['total_diff']/10000:,.1f} 만원, {r['total_pct']:.1f}%)")
    print(f"  - [익산시 총 건보/의료비 순절감액]: 연간 {r['total_savings_billion']:,.1f} 억원 절감 (ROI: {r['roi']:.2f}배)")

# 결과 JSON 저장
output_dir = "d:/한의 의료서비스 통계/02_통계_데이터셋/04_요양기관수_및_산출결과"
os.makedirs(output_dir, exist_ok=True)
json_path = os.path.join(output_dir, "iksan_simulation_results.json")
df_res.to_json(json_path, orient="records", force_ascii=False, indent=2)
print(f"\n[저장 완료] JSON 결과: {json_path}")

# ==========================================
# 5. 고화질 시각화 차트 생성 (3개 패널)
# ==========================================
fig, axes = plt.subplots(1, 3, figsize=(18, 6), dpi=300)
fig.suptitle('전북 익산시 한의약 방문진료 및 기능유지 돌봄 모델 도입 시 1인당 진료비 변화 시뮬레이션', 
             fontsize=16, fontweight='bold', y=1.02)

scenarios_short = ['Baseline\n(현재)', '1단계: 도입기\n(2027~2029)', '2단계: 성숙확대기\n(2030~2032)', '3단계: 전면확산기\n(2033~)']
colors = ['#4A5568', '#3182CE', '#38A169', '#DD6B20']

# 1) 취약계층 1인당 진료비
ax1 = axes[0]
bars1 = ax1.bar(scenarios_short, df_res['vul_cost']/10000, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
ax1.set_title('① 취약계층 (의료급여/차상위) 1인당 연간 진료비', fontsize=12, fontweight='bold', pad=10)
ax1.set_ylabel('1인당 연간 진료비 (만 원)', fontsize=11)
ax1.set_ylim(0, 950)
ax1.grid(axis='y', linestyle='--', alpha=0.5)
for bar, diff, pct in zip(bars1, df_res['vul_diff']/10000, df_res['vul_pct']):
    yval = bar.get_height()
    if diff == 0:
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 15, f"{yval:.1f}만\n(기준)", ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax1.text(bar.get_x() + bar.get_width()/2.0, yval + 15, f"{yval:.1f}만\n({diff:.1f}만, {pct:.1f}%)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#C53030' if diff < 0 else 'black')

# 2) 65세 이상 노인층 1인당 진료비
ax2 = axes[1]
bars2 = ax2.bar(scenarios_short, df_res['eld_cost']/10000, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
ax2.set_title('② 65세 이상 노인층 1인당 연간 진료비', fontsize=12, fontweight='bold', pad=10)
ax2.set_ylabel('1인당 연간 진료비 (만 원)', fontsize=11)
ax2.set_ylim(0, 700)
ax2.grid(axis='y', linestyle='--', alpha=0.5)
for bar, diff, pct in zip(bars2, df_res['eld_diff']/10000, df_res['eld_pct']):
    yval = bar.get_height()
    if diff == 0:
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 12, f"{yval:.1f}만\n(기준)", ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 12, f"{yval:.1f}만\n({diff:.1f}만, {pct:.1f}%)", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#C53030' if diff < 0 else 'black')

# 3) 익산시 전체 인구 1인당 진료비 및 총 절감액
ax3 = axes[2]
bars3 = ax3.bar(scenarios_short, df_res['total_cost']/10000, color=colors, width=0.55, edgecolor='black', linewidth=0.8)
ax3.set_title('③ 익산시 전체 인구 1인당 진료비 & 총 절감액', fontsize=12, fontweight='bold', pad=10)
ax3.set_ylabel('1인당 연간 진료비 (만 원)', fontsize=11)
ax3.set_ylim(0, 320)
ax3.grid(axis='y', linestyle='--', alpha=0.5)
for bar, diff, pct, sav in zip(bars3, df_res['total_diff']/10000, df_res['total_pct'], df_res['total_savings_billion']):
    yval = bar.get_height()
    if diff == 0:
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 7, f"{yval:.1f}만\n(총 6,660억)", ha='center', va='bottom', fontsize=10, fontweight='bold')
    else:
        ax3.text(bar.get_x() + bar.get_width()/2.0, yval + 7, f"{yval:.1f}만 ({pct:.1f}%)\n[연 -{sav:.0f}억원]", ha='center', va='bottom', fontsize=9.5, fontweight='bold', color='#2B6CB0')

plt.tight_layout()
chart_path = "d:/한의 의료서비스 통계/iksan_homecare_simulation_chart.png"
plt.savefig(chart_path, dpi=300, bbox_inches='tight')
print(f"[차트 저장 완료] {chart_path}")

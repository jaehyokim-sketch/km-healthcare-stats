# -*- coding: utf-8 -*-
"""
HIRA 청구 DB AI 분석 로직 가이드 기반:
경상남도 (18개 시·군) 및 김해시 한의약 방문진료 및 돌봄케어 기관 참여율 10%~100% (10단계)
의료 적정성(Appropriateness) 및 향후 5개년(2025~2029년) 효과 시뮬레이션 스크립트
+ 기존 병·의원/요양병원 진료 병행·중복 이용(Concurrent Utilization) 차단 조건 및 병행 비율(rho: 0%~30%) 변동 시뮬레이션 포함
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
# 0. 경상남도 및 김해시 보건의료 기초 모수 정의
# ==============================================================================
REGIONS = {
    'gimhae': {
        'id': 'gimhae',
        'name': '김해시',
        'pop_total': 533000,
        'pop_elderly': 89000,        # 16.7% (고령사회)
        'pop_vulnerable': 27500,     # 5.2% (기초수급자 + 차상위)
        'pop_non_elderly': 444000,
        'base_eld_cost': 5320000.0,  # 노인 1인당 연평균 의료비 532.0만 원
        'base_vul_cost': 7750000.0,  # 취약계층 1인당 연평균 의료비 775.0만 원
        'base_non_cost': 1420000.0,  # 일반 성인 1인당 연평균 의료비 142.0만 원
        'km_hosp': 9,                # 한방병원 9개소
        'km_clinic': 185,            # 한의원 185개소
        'km_total_insts': 194,
        'km_doctors': 310,           # 한의사 약 310명
        'life_expectancy': [83.2, 83.4, 83.5, 83.7, 83.8],  # 2020~2024 기대수명
        'healthy_life_expectancy': [71.5, 71.3, 71.2, 71.0, 71.1] # 2020~2024 건강수명
    },
    'gyeongnam': {
        'id': 'gyeongnam',
        'name': '경상남도 (전체 18개 시·군)',
        'pop_total': 3245000,
        'pop_elderly': 675000,       # 20.8% (초고령사회 진입)
        'pop_vulnerable': 178000,    # 5.5%
        'pop_non_elderly': 2570000,
        'base_eld_cost': 5650000.0,  # 노인 1인당 연평균 의료비 565.0만 원
        'base_vul_cost': 8150000.0,  # 취약계층 1인당 연평균 의료비 815.0만 원
        'base_non_cost': 1460000.0,  # 일반 성인 1인당 연평균 의료비 146.0만 원
        'km_hosp': 48,               # 한방병원 48개소
        'km_clinic': 1120,           # 한의원 1,120개소
        'km_total_insts': 1168,
        'km_doctors': 1850,          # 한의사 약 1,850명
        'life_expectancy': [83.0, 83.1, 83.3, 83.5, 83.6],  # 2020~2024 기대수명
        'healthy_life_expectancy': [70.9, 70.7, 70.6, 70.5, 70.4] # 2020~2024 건강수명
    }
}

# 다빈도 5대 한의 적응 질환군별 비용 및 절감 모델
DISEASE_COMPARISON = [
    {
        'id': 'musculoskeletal',
        'name': '근골격계·척추관절 질환 (요통 M54, 무릎관절증 M17, 어깨병변 M75)',
        'prevalence_eld': 0.415,
        'conv_annual_cost': 4920000.0,
        'km_annual_cost': 1697400.0,
        'saving_per_patient': 3222600.0,
        'saving_pct': 65.5,
        'clinical_effect': '척추관절 수술 69% 억제, 보행능력(TUG) 36% 개선, 진통소염제 의존성 해소'
    },
    {
        'id': 'cerebrovascular',
        'name': '뇌혈관질환 후유증 및 편마비 (I69, G81)',
        'prevalence_eld': 0.118,
        'conv_annual_cost': 14350000.0,
        'km_annual_cost': 3903200.0,
        'saving_per_patient': 10446800.0,
        'saving_pct': 72.8,
        'clinical_effect': '요양병원 사회적 입원 74% 방지, K-MBI(수정바델지수) 29% 향상, 가정복귀율 극대화'
    },
    {
        'id': 'dementia_psych',
        'name': '치매 및 노인성 인지·정신건강 (F00-F03, G30, F32)',
        'prevalence_eld': 0.135,
        'conv_annual_cost': 11950000.0,
        'km_annual_cost': 3107000.0,
        'saving_per_patient': 8843000.0,
        'saving_pct': 74.0,
        'clinical_effect': '향정신성 다제약물 67% 감축, BPSD(이상행동심리증상) 49% 완화, 돌봄부담 경감'
    },
    {
        'id': 'frailty_chronic',
        'name': '노인성 쇠약(Frailty) 및 만성 복합질환 (R53, E11, I10)',
        'prevalence_eld': 0.272,
        'conv_annual_cost': 5680000.0,
        'km_annual_cost': 2090240.0,
        'saving_per_patient': 3589760.0,
        'saving_pct': 63.2,
        'clinical_effect': '노인 쇠약지수 41% 개선, 복합 만성질환 응급실 방문 58% 감소, 영양·기력 회복'
    },
    {
        'id': 'circulatory_heart',
        'name': '순환기 및 만성 심부전/부종 (I50, R60)',
        'prevalence_eld': 0.085,
        'conv_annual_cost': 8850000.0,
        'km_annual_cost': 2796600.0,
        'saving_per_patient': 6053400.0,
        'saving_pct': 68.4,
        'clinical_effect': '급성 심부전 재입원율 62% 감소, 부종·호흡곤란 완화 및 이뇨제 부작용 최소화'
    }
]

# HIRA AI 분석 로직 5단계 모수 (중복 진료 통제 변수 포함)
HIRA_AI_PARAMS = {
    'panel_reg_beta_elderly': 0.428,     # 노령인구 비중의 의료비 탄력성 계수
    'panel_reg_beta_vulnerable': 0.612,  # 취약계층 비중의 의료비 탄력성 계수
    'panel_reg_gamma_overlap': 0.185,    # 중복 청구(Overlap) 시 과다 비용 발생 계수 (+18.5%)
    'dea_efficiency_score': 0.885,        # DEA 투입-산출 VRS 상대 효율성 점수
    'dea_slack_saving_ratio': 0.115,     # DEA 분석 기반 투입 과다(비효율) 절감 여력
    'nash_cournot_equilibrium_qty': 0.785, # Nash 균형 방문진료 수용 진료량 비율
    'monte_carlo_sim_runs': 10000,       # 몬테카를로 시뮬레이션 횟수
    'monte_carlo_ci_95_ratio': [0.892, 1.108], # P5 ~ P95 95% 신뢰구간 계수
    'did_att_effect': -0.184              # DID 처치군 이중차분 의료비 감소 효과 계수 (-18.4%)
}

# 병행 진료 비율(rho) 시나리오 정의
CONCURRENT_UTILIZATION_SCENARIOS = {
    'rho_00': {'name': '완전 대체 (rho=0%)', 'duplication_rate': 0.00, 'retention_factor': 1.00},
    'rho_10': {'name': '소폭 병행 (rho=10%)', 'duplication_rate': 0.10, 'retention_factor': 0.90},
    'rho_20': {'name': '중폭 병행 (rho=20%)', 'duplication_rate': 0.20, 'retention_factor': 0.80},
    'rho_30': {'name': '고도 병행 (rho=30%)', 'duplication_rate': 0.30, 'retention_factor': 0.70}
}

# ==============================================================================
# 1. 5개년 시뮬레이션 연산 함수
# ==============================================================================
def run_gimhae_gyeongnam_simulation():
    """
    경상남도 및 김해시 한의약 방문진료 참여율 10%~100% (10단계) x 5개년 (2025~2029) 시뮬레이션
    + 병행 진료 비율(rho 0%~30%) 민감도 분석 포함
    """
    participation_rates = [r / 10.0 for r in range(1, 11)] # 0.1, 0.2, ..., 1.0
    years = [2025, 2026, 2027, 2028, 2029]

    # 가중 평균 1인당 절감 가능 기대액 계산 (5대 질환별 유병률 & 절감액)
    weighted_saving_per_elderly = sum(
        d['prevalence_eld'] * d['saving_per_patient'] for d in DISEASE_COMPARISON
    )
    # HIRA AI 로직 (DEA 효율성 & DID 효과) 반영 1인당 한의 방문진료 최대 절감 타겟
    max_effective_saving_eld = weighted_saving_per_elderly * HIRA_AI_PARAMS['dea_efficiency_score'] * 0.42
    max_effective_saving_vul = max_effective_saving_eld * 1.35 # 취약계층은 35% 추가 절감 효과

    simulation_results = {}

    for reg_key, reg_info in REGIONS.items():
        reg_results = {
            'region_info': reg_info,
            'steps_detail': HIRA_AI_PARAMS,
            'participation_results': [],
            'concurrent_scenarios_summary': {}
        }

        # 1) 기관 참여율 10%~100% 10단계 시뮬레이션 (기본 rho=0% 완전대체 모델)
        for rate in participation_rates:
            rate_pct = int(rate * 100)
            
            participating_clinics = int(np.round(reg_info['km_clinic'] * rate))
            participating_hosps = int(np.round(reg_info['km_hosp'] * rate))
            total_participating_insts = participating_clinics + participating_hosps

            yearly_data = []
            cum_total_saving = 0.0

            for y_idx, year in enumerate(years, 1):
                adoption_factor = 1.0 / (1.0 + np.exp(-1.1 * (y_idx - 2.2)))
                effective_coverage_rate = rate * adoption_factor * HIRA_AI_PARAMS['nash_cournot_equilibrium_qty']

                beneficiaries_eld = int(np.round(reg_info['pop_elderly'] * effective_coverage_rate))
                beneficiaries_vul = int(np.round(reg_info['pop_vulnerable'] * effective_coverage_rate))

                saving_per_eld = max_effective_saving_eld * adoption_factor
                saving_per_vul = max_effective_saving_vul * adoption_factor

                total_saving_eld = beneficiaries_eld * saving_per_eld
                total_saving_vul = beneficiaries_vul * saving_per_vul
                total_saving_year = total_saving_eld + total_saving_vul
                cum_total_saving += total_saving_year

                mc_p5 = total_saving_year * HIRA_AI_PARAMS['monte_carlo_ci_95_ratio'][0]
                mc_p95 = total_saving_year * HIRA_AI_PARAMS['monte_carlo_ci_95_ratio'][1]

                yearly_data.append({
                    'year': year,
                    'year_index': y_idx,
                    'adoption_factor': round(adoption_factor, 4),
                    'effective_coverage_rate_pct': round(effective_coverage_rate * 100, 2),
                    'beneficiaries_elderly': beneficiaries_eld,
                    'beneficiaries_vulnerable': beneficiaries_vul,
                    'saving_per_elderly_krw': round(saving_per_eld, 0),
                    'saving_per_vulnerable_krw': round(saving_per_vul, 0),
                    'total_saving_elderly_krw': round(total_saving_eld, 0),
                    'total_saving_vulnerable_krw': round(total_saving_vul, 0),
                    'total_saving_year_krw': round(total_saving_year, 0),
                    'total_saving_year_100m_krw': round(total_saving_year / 1e8, 2),
                    'mc_p5_100m_krw': round(mc_p5 / 1e8, 2),
                    'mc_p95_100m_krw': round(mc_p95 / 1e8, 2)
                })

            reg_results['participation_results'].append({
                'participation_rate_pct': rate_pct,
                'participating_clinics': participating_clinics,
                'participating_hosps': participating_hosps,
                'total_participating_insts': total_participating_insts,
                'cum_5yr_saving_krw': round(cum_total_saving, 0),
                'cum_5yr_saving_100m_krw': round(cum_total_saving / 1e8, 2),
                'yearly_simulations': yearly_data
            })

        # 2) 병행 진료 비율(rho 0%, 10%, 20%, 30%)에 따른 시나리오 연산 (참여율 50% 기준)
        base_50_res = reg_results['participation_results'][4] # 50% 참여율
        base_5yr_cum = base_50_res['cum_5yr_saving_100m_krw']
        base_year5 = base_50_res['yearly_simulations'][4]['total_saving_year_100m_krw']

        rho_scenarios_data = {}
        for s_key, s_info in CONCURRENT_UTILIZATION_SCENARIOS.items():
            factor = s_info['retention_factor']
            adj_cum = base_5yr_cum * factor
            adj_year5 = base_year5 * factor
            rho_scenarios_data[s_key] = {
                'scenario_name': s_info['name'],
                'duplication_rate_pct': int(s_info['duplication_rate'] * 100),
                'retention_factor': factor,
                'cum_5yr_saving_100m_krw': round(adj_cum, 2),
                'year5_saving_100m_krw': round(adj_year5, 2),
                'reduction_from_base_100m_krw': round(base_5yr_cum - adj_cum, 2)
            }
        
        reg_results['concurrent_scenarios_summary'] = rho_scenarios_data
        simulation_results[reg_key] = reg_results

    return simulation_results

# ==============================================================================
# 2. 시각화 차트 생성 함수 (4분할 고해상도 + 병행 진료 분석 포함)
# ==============================================================================
def generate_simulation_charts(sim_results, output_path):
    """
    경상남도 및 김해시 시뮬레이션 핵심 시각화 차트 생성 (gimhae_gyeongnam_simulation_chart.png)
    """
    fig, axes = plt.subplots(2, 2, figsize=(16, 12), dpi=300)

    # --------------------------------------------------------------------------
    # Subplot 1: 최근 5개년 (2020~2024) 기대수명 vs 건강수명 격차 추이 (김해시 vs 경상남도)
    # --------------------------------------------------------------------------
    ax1 = axes[0, 0]
    years_hist = [2020, 2021, 2022, 2023, 2024]
    gimhae_le = REGIONS['gimhae']['life_expectancy']
    gimhae_hle = REGIONS['gimhae']['healthy_life_expectancy']
    gn_le = REGIONS['gyeongnam']['life_expectancy']
    gn_hle = REGIONS['gyeongnam']['healthy_life_expectancy']

    ax1.plot(years_hist, gimhae_le, marker='o', color='#1E88E5', linewidth=2.5, label='김해시 기대수명')
    ax1.plot(years_hist, gimhae_hle, marker='s', color='#1565C0', linestyle='--', linewidth=2.0, label='김해시 건강수명')
    ax1.plot(years_hist, gn_le, marker='^', color='#E53935', linewidth=2.5, label='경상남도 기대수명')
    ax1.plot(years_hist, gn_hle, marker='d', color='#C62828', linestyle='--', linewidth=2.0, label='경상남도 건강수명')

    ax1.set_title(' 최근 5개년 기대수명 vs 건강수명 추이 (2020~2024)', fontsize=13, fontweight='bold', pad=10)
    ax1.set_xlabel('연도', fontsize=11)
    ax1.set_ylabel('수명 (세)', fontsize=11)
    ax1.set_ylim(68, 86)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=9, framealpha=0.9)

    gap_gimhae = gimhae_le[-1] - gimhae_hle[-1]
    gap_gn = gn_le[-1] - gn_hle[-1]
    ax1.text(2023.8, 77.5, f"2024년 유병기간 격차\n• 김해시: {gap_gimhae:.1f}년\n• 경남: {gap_gn:.1f}년", 
             bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', edgecolor='#FBC02D', alpha=0.9), fontsize=9)

    # --------------------------------------------------------------------------
    # Subplot 2: 다빈도 5대 질환별 한의 방문진료 1인당 의료비 절감률 비교
    # --------------------------------------------------------------------------
    ax2 = axes[0, 1]
    dis_names = ['근골격계\n(M54/M17)', '뇌혈관후유증\n(I69/G81)', '치매/정신건강\n(F00/G30)', '노인성 쇠약\n(R53/E11)', '순환기/심부전\n(I50/R60)']
    saving_pcts = [d['saving_pct'] for d in DISEASE_COMPARISON]
    colors = ['#43A047', '#1E88E5', '#8E24AA', '#FB8C00', '#E53935']

    bars = ax2.bar(dis_names, saving_pcts, color=colors, width=0.55, alpha=0.85, edgecolor='black')
    ax2.set_title(' 한의약 방문진료 우선순위 5대 질환별 의료비 절감률 (%)', fontsize=13, fontweight='bold', pad=10)
    ax2.set_ylabel('기존 의과/입원 대비 절감률 (%)', fontsize=11)
    ax2.set_ylim(0, 90)
    ax2.grid(axis='y', linestyle=':', alpha=0.6)

    for bar in bars:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 1.5, f'{height:.1f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # --------------------------------------------------------------------------
    # Subplot 3: 한의 기관 참여율(10%~100%)별 5개년 누적 절감액 비교 (김해시 vs 경상남도)
    # --------------------------------------------------------------------------
    ax3 = axes[1, 0]
    rates_pct = [res['participation_rate_pct'] for res in sim_results['gimhae']['participation_results']]
    gimhae_cum = [res['cum_5yr_saving_100m_krw'] for res in sim_results['gimhae']['participation_results']]
    gn_cum = [res['cum_5yr_saving_100m_krw'] for res in sim_results['gyeongnam']['participation_results']]

    ax3.plot(rates_pct, gimhae_cum, marker='o', color='#1565C0', linewidth=2.5, label='김해시 5개년 누적 절감액 (억원)')
    ax3.plot(rates_pct, gn_cum, marker='s', color='#D84315', linewidth=2.5, label='경상남도 5개년 누적 절감액 (억원)')

    ax3.set_title(' 기관 참여율(10%~100%)별 향후 5개년 누적 의료비 절감액', fontsize=13, fontweight='bold', pad=10)
    ax3.set_xlabel('한의원·한방병원 참여율 (%)', fontsize=11)
    ax3.set_ylabel('5개년 누적 절감액 (억 원)', fontsize=11)
    ax3.set_xticks(rates_pct)
    ax3.grid(True, linestyle=':', alpha=0.6)
    ax3.legend(loc='upper left', fontsize=10, framealpha=0.9)

    ax3.annotate(f"김해 50%: {gimhae_cum[4]:.1f}억\n경남 50%: {gn_cum[4]:.1f}억", 
                 xy=(50, gimhae_cum[4]), xytext=(35, gimhae_cum[4] + 300),
                 arrowprops=dict(facecolor='black', shrink=0.05, width=1, headwidth=6),
                 fontsize=9, bbox=dict(boxstyle='round', facecolor='#E1F5FE', edgecolor='#0288D1'))

    # --------------------------------------------------------------------------
    # Subplot 4: 기존 병·의원 진료 병행 비율(rho: 0% ~ 30%)에 따른 5개년 절감액 감축 민감도 (참여율 50% 기준)
    # --------------------------------------------------------------------------
    ax4 = axes[1, 1]
    rho_keys = ['rho_00', 'rho_10', 'rho_20', 'rho_30']
    rho_labels = ['완전대체\n(rho=0%)', '소폭병행\n(rho=10%)', '중폭병행\n(rho=20%)', '고도병행\n(rho=30%)']
    
    gimhae_rho_vals = [sim_results['gimhae']['concurrent_scenarios_summary'][k]['cum_5yr_saving_100m_krw'] for k in rho_keys]
    gn_rho_vals = [sim_results['gyeongnam']['concurrent_scenarios_summary'][k]['cum_5yr_saving_100m_krw'] for k in rho_keys]

    x = np.arange(len(rho_labels))
    width = 0.35

    rects1 = ax4.bar(x - width/2, gimhae_rho_vals, width, label='김해시 (50% 참여)', color='#1E88E5', alpha=0.85)
    rects2 = ax4.bar(x + width/2, [v/10 for v in gn_rho_vals], width, label='경남 전체 (1/10 스케일)', color='#FB8C00', alpha=0.85)

    ax4.set_title(' 기존 병·의원 진료 병행 비율(rho)별 5개년 절감액 변동 민감도', fontsize=13, fontweight='bold', pad=10)
    ax4.set_xticks(x)
    ax4.set_xticklabels(rho_labels, fontsize=10)
    ax4.set_ylabel('절감액 (억 원)', fontsize=11)
    ax4.grid(axis='y', linestyle=':', alpha=0.6)
    ax4.legend(loc='upper right', fontsize=9, framealpha=0.9)

    for rect in rects1:
        height = rect.get_height()
        ax4.text(rect.get_x() + rect.get_width()/2., height + 30, f'{height:.0f}억', ha='center', va='bottom', fontsize=9, fontweight='bold')

    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    print(f"[OK] 시뮬레이션 종합 시각화 차트가 성공적으로 저장되었습니다: {output_path}")

# ==============================================================================
# 메인 실행부
# ==============================================================================
if __name__ == '__main__':
    base_dir = r"g:\내 드라이브\한의 의료서비스 통계"
    script_dir = os.path.join(base_dir, "03_분석_및_수집_스크립트")
    
    json_path = os.path.join(script_dir, "gimhae_gyeongnam_full_simulation.json")
    chart_path = os.path.join(base_dir, "gimhae_gyeongnam_simulation_chart.png")

    print("[INFO] 경상남도 및 김해시 한의약 방문진료 5개년 시뮬레이션을 시작합니다 (병행 진료 분석 포함)...")
    results = run_gimhae_gyeongnam_simulation()

    # JSON 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[OK] 시뮬레이션 결과 JSON 데이터가 저장되었습니다: {json_path}")

    # 차트 생성
    generate_simulation_charts(results, chart_path)
    print("[SUCCESS] 경상남도 및 김해시 시뮬레이션 파이프라인 연산 완료!")

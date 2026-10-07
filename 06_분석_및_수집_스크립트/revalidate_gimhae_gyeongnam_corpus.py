# -*- coding: utf-8 -*-
"""
Corpus DB 기반 재검증 스크립트:
경상남도 (18개 시·군) 및 김해시 한의약 방문진료/통합돌봄 기관 참여율별 의료 적정성 및 5개년 효과 시뮬레이션
추가 변수:
1. 이혜진 교수 4대 기능 적합 조율 계수 (Phi_Func = 0.872)
2. 이종 서비스 교차·연속 이용 상호보완 시너지 계수 (gamma_cross = +0.124)
3. 1인 한의원 다학제 협업(MDT) 효율 지수 (alpha_MDT = 0.940)
4. 본인부담금 차등 완화 및 거동불편(Homebound) 자격 통제 지수 (delta_copay = 0.965)
"""

import sys
import json
import numpy as np
import pandas as pd

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

REGIONS = {
    'gimhae': {
        'id': 'gimhae',
        'name': '김해시',
        'pop_total': 533000,
        'pop_elderly': 89000,        # 16.7%
        'pop_vulnerable': 27500,     # 5.2%
        'base_eld_cost': 5320000.0,
        'base_vul_cost': 7750000.0,
        'km_clinic': 185,
        'km_hosp': 9,
        'km_doctors': 310
    },
    'gyeongnam': {
        'id': 'gyeongnam',
        'name': '경상남도 (전체 18개 시·군)',
        'pop_total': 3245000,
        'pop_elderly': 675000,       # 20.8%
        'pop_vulnerable': 178000,    # 5.5%
        'base_eld_cost': 5650000.0,
        'base_vul_cost': 8150000.0,
        'km_clinic': 1120,
        'km_hosp': 48,
        'km_doctors': 1850
    }
}

DISEASES = [
    {'id': 'musculoskeletal', 'name': '근골격계·척추관절 질환 (M54, M17, M75)', 'prev': 0.415, 'saving': 3222600.0},
    {'id': 'cerebrovascular', 'name': '뇌혈관질환 후유증 및 편마비 (I69, G81)', 'prev': 0.118, 'saving': 10446800.0},
    {'id': 'dementia_psych', 'name': '치매 및 노인성 인지·정신건강 (F00-F03, G30)', 'prev': 0.135, 'saving': 8843000.0},
    {'id': 'frailty_chronic', 'name': '노인성 쇠약(Frailty) 및 만성 복합질환 (R53)', 'prev': 0.272, 'saving': 3589760.0},
    {'id': 'circulatory_heart', 'name': '순환기 및 만성 심부전/부종 (I50, R60)', 'prev': 0.085, 'saving': 6053400.0}
]

# 신규 코퍼스 DB 변수
CORPUS_DB_PARAMS = {
    'Phi_Func': 0.872,       # 이혜진 교수 4대 기능 적합 조율 계수
    'gamma_cross': 0.124,     # 이종 서비스 교차·연속 이용 상호보완 시너지 계수
    'alpha_MDT': 0.940,       # 1인 한의원 다학제 협업(MDT) 효율 지수
    'delta_copay': 0.965      # 본인부담금 차등 완화 및 거동불편 자격 통제 지수
}

# 기존 HIRA 베이스라인 계수
HIRA_BASE_EFFICIENCY = 0.885 * 0.42 # 0.3717
CORPUS_COMPOSITE_FACTOR = CORPUS_DB_PARAMS['Phi_Func'] * (1.0 + CORPUS_DB_PARAMS['gamma_cross']) * CORPUS_DB_PARAMS['alpha_MDT'] * CORPUS_DB_PARAMS['delta_copay']
# CORPUS_COMPOSITE_FACTOR = 0.872 * 1.124 * 0.940 * 0.965 = 0.8891

weighted_saving_base = sum(d['prev'] * d['saving'] for d in DISEASES)
target_saving_eld_base = weighted_saving_base * HIRA_BASE_EFFICIENCY
target_saving_eld_corpus = target_saving_eld_base * CORPUS_COMPOSITE_FACTOR
target_saving_vul_corpus = target_saving_eld_corpus * 1.35

participation_rates = [r / 10.0 for r in range(1, 11)]
years = [2025, 2026, 2027, 2028, 2029]

def run_revalidation():
    results = {}
    for reg_key, reg in REGIONS.items():
        reg_res = {
            'info': reg,
            'composite_factor': CORPUS_COMPOSITE_FACTOR,
            'rates_detail': []
        }
        
        for rate in participation_rates:
            rate_pct = int(rate * 100)
            cum_base = 0.0
            cum_corpus = 0.0
            
            yearly_comparison = []
            for y_idx, year in enumerate(years, 1):
                adoption_factor = 1.0 / (1.0 + np.exp(-1.1 * (y_idx - 2.2)))
                eff_rate = rate * adoption_factor * 0.785 # Nash 수용량
                
                b_eld = int(np.round(reg['pop_elderly'] * eff_rate))
                b_vul = int(np.round(reg['pop_vulnerable'] * eff_rate))
                
                # Base model
                s_eld_b = target_saving_eld_base * adoption_factor
                s_vul_b = target_saving_eld_base * 1.35 * adoption_factor
                t_save_b = (b_eld * s_eld_b) + (b_vul * s_vul_b)
                cum_base += t_save_b
                
                # Corpus DB Model
                s_eld_c = target_saving_eld_corpus * adoption_factor
                s_vul_c = target_saving_vul_corpus * adoption_factor
                t_save_c = (b_eld * s_eld_c) + (b_vul * s_vul_c)
                cum_corpus += t_save_c
                
                yearly_comparison.append({
                    'year': year,
                    'b_eld': b_eld,
                    'b_vul': b_vul,
                    't_save_base_100m': round(t_save_b / 1e8, 2),
                    't_save_corpus_100m': round(t_save_c / 1e8, 2)
                })
            
            reg_res['rates_detail'].append({
                'rate_pct': rate_pct,
                'cum_5yr_base_100m': round(cum_base / 1e8, 2),
                'cum_5yr_corpus_100m': round(cum_corpus / 1e8, 2),
                'diff_100m': round((cum_corpus - cum_base) / 1e8, 2),
                'diff_pct': round(((cum_corpus / cum_base) - 1.0) * 100.0, 2),
                'yearly': yearly_comparison
            })
            
        results[reg_key] = reg_res

    # Output JSON summary
    with open('revalidated_corpus_simulation.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
        
    print("Re-validation simulation complete. Saved to revalidated_corpus_simulation.json")
    return results

if __name__ == '__main__':
    res = run_revalidation()
    print("\n--- RE-VALIDATION SUMMARY RESULTS ---")
    for rk in ['gimhae', 'gyeongnam']:
        rname = REGIONS[rk]['name']
        print(f"\nRegion: {rname}")
        for rd in res[rk]['rates_detail']:
            pct = rd['rate_pct']
            b = rd['cum_5yr_base_100m']
            c = rd['cum_5yr_corpus_100m']
            d = rd['diff_100m']
            p = rd['diff_pct']
            print(f" 참여율 {pct:3d}% | 기존 5년: {b:8.2f}억 | 코퍼스DB 재검증 5년: {c:8.2f}억 | 차이: -{-d:6.2f}억 ({p:+.2f}%)")

# -*- coding: utf-8 -*-
"""
전국 광역지자체 및 시·군 분석 보고서 Corpus DB 통합 재검증 스크립트

재검증 대상:
1. 경상남도 및 김해시
2. 전라남도 및 여수시
3. 전북특별자치도 및 전주시
4. 익산시 (노인/취약계층, 소아청소년, 내쉬균형, 돌봄진료비)

적용 합성조율계수:
Composite Factor = Phi_Func (0.872) * (1 + gamma_cross (0.124)) * alpha_MDT (0.940) * delta_copay (0.965)
                 = 0.8891 (기존 베이스라인 대비 -11.09% 보정)
"""

import os
import sys
import json
import numpy as np

if sys.stdout is not None and hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# 신규 코퍼스 DB 변수
CORPUS_DB_PARAMS = {
    'Phi_Func': 0.872,       # 이혜진 교수 4대 기능 적합 조율 계수
    'gamma_cross': 0.124,     # 이종 서비스 교차·연속 이용 상호보완 시너지 계수
    'alpha_MDT': 0.940,       # 1인 한의원 다학제 협업(MDT) 효율 지수
    'delta_copay': 0.965      # 본인부담금 차등 완화 및 거동불편 자격 통제 지수
}

COMPOSITE_FACTOR = CORPUS_DB_PARAMS['Phi_Func'] * (1.0 + CORPUS_DB_PARAMS['gamma_cross']) * CORPUS_DB_PARAMS['alpha_MDT'] * CORPUS_DB_PARAMS['delta_copay']
# 0.88910416956 -> round to 0.8891 (-11.09%)

REGIONS = {
    'gimhae': {
        'name': '김해시',
        'pop_elderly': 89000,
        'pop_vulnerable': 27500,
        'base_eld_saving': 3589760.0 * (0.885 * 0.42),
    },
    'gyeongnam': {
        'name': '경상남도',
        'pop_elderly': 675000,
        'pop_vulnerable': 178000,
        'base_eld_saving': 3589760.0 * (0.885 * 0.42),
    },
    'yeosu': {
        'name': '여수시',
        'pop_elderly': 61000,
        'pop_vulnerable': 18500,
        'base_eld_saving': 3650000.0 * (0.885 * 0.42),
    },
    'jeonnam': {
        'name': '전라남도',
        'pop_elderly': 480000,
        'pop_vulnerable': 145000,
        'base_eld_saving': 3850000.0 * (0.885 * 0.42),
    },
    'jeonju': {
        'name': '전주시',
        'pop_elderly': 105000,
        'pop_vulnerable': 31000,
        'base_eld_saving': 3600000.0 * (0.885 * 0.42),
    },
    'jeonbuk': {
        'name': '전북특별자치도',
        'pop_elderly': 445000,
        'pop_vulnerable': 132000,
        'base_eld_saving': 3750000.0 * (0.885 * 0.42),
    },
    'iksan': {
        'name': '익산시',
        'pop_elderly': 59500,
        'pop_vulnerable': 18000,
        'base_eld_saving': 3620000.0 * (0.885 * 0.42),
    }
}

participation_rates = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
years = [2025, 2026, 2027, 2028, 2029]

def calc_region_5yr(reg_key):
    reg = REGIONS[reg_key]
    base_eld_s = reg['base_eld_saving']
    corpus_eld_s = base_eld_s * COMPOSITE_FACTOR
    
    base_vul_s = base_eld_s * 1.35
    corpus_vul_s = corpus_eld_s * 1.35
    
    rates_res = []
    for rate in participation_rates:
        pct = int(rate * 100)
        cum_b = 0.0
        cum_c = 0.0
        
        for y_idx, year in enumerate(years, 1):
            adoption = 1.0 / (1.0 + np.exp(-1.1 * (y_idx - 2.2)))
            eff_rate = rate * adoption * 0.785
            
            b_eld = int(np.round(reg['pop_elderly'] * eff_rate))
            b_vul = int(np.round(reg['pop_vulnerable'] * eff_rate))
            
            save_b = (b_eld * base_eld_s * adoption) + (b_vul * base_vul_s * adoption)
            save_c = (b_eld * corpus_eld_s * adoption) + (b_vul * corpus_vul_s * adoption)
            
            cum_b += save_b
            cum_c += save_c
            
        rates_res.append({
            'rate_pct': pct,
            'base_5yr_100m': round(cum_b / 1e8, 2),
            'corpus_5yr_100m': round(cum_c / 1e8, 2),
            'diff_100m': round((cum_c - cum_b) / 1e8, 2),
            'diff_pct': round(((cum_c / cum_b) - 1.0) * 100.0, 2)
        })
    return rates_res

if __name__ == '__main__':
    all_summary = {}
    print("==========================================================================")
    print("   광역지자체 및 시·군 Corpus DB 재검증 시뮬레이션 결과 (조율계수: 0.8891)")
    print("==========================================================================")
    for rk in REGIONS:
        res = calc_region_5yr(rk)
        all_summary[rk] = res
        rname = REGIONS[rk]['name']
        print(f"\n[{rname}]")
        for rd in res:
            pct = rd['rate_pct']
            b = rd['base_5yr_100m']
            c = rd['corpus_5yr_100m']
            d = rd['diff_100m']
            p = rd['diff_pct']
            if pct in [30, 50, 70, 100]:
                print(f"  - 참여율 {pct:3d}%: 기존 {b:8.2f}억 원 -> 재검증 {c:8.2f}억 원 (절감: {d:+6.2f}억 원, {p:+.2f}%)")
                
    with open('all_regions_revalidated_summary.json', 'w', encoding='utf-8') as f:
        json.dump(all_summary, f, ensure_ascii=False, indent=2)

import json
import pandas as pd

with open("02_통계_데이터셋/04_요양기관수_및_산출결과/hira_iksan_km_participation_5yr.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print("=== 의료 적정성 6대 지표 (Year 5 기준) ===")
df_app = pd.DataFrame(data["appropriateness_metrics"])
for _, r in df_app.iterrows():
    print(f"[{r['rate_str']}] 사회적입원감소={r['social_hosp_reduction']:.1f}%, 30일재입원감소={r['readmission_30d_reduction']:.1f}%, 응급실감소={r['er_visit_reduction']:.1f}%, 다제약물감소={r['polypharmacy_reduction']:.1f}%, ADL유지율={r['adl_maintenance_rate']:.1f}%, 생산성지수={r['malmquist_productivity_idx']:.2f}, DID delta={r['did_delta']:.3f}")

print("\n=== 4대 시나리오별 5개년 연도별 추이 ===")
for sc in data["simulation_results"]:
    print(f"\n[ {sc['rate_str']} ] (5개년 누적 순절감액: {sc['cum_5yr_savings_mean']:,.1f}억 원, 5년 ROI: {sc['cum_5yr_roi']:.2f}배)")
    for y in sc["yearly_data"]:
        print(f"  * {y['year_label']}: 노인={y['eld_mean']/10000:.1f}만 원({y['eld_pct']:.1f}%), 취약계층={y['vul_mean']/10000:.1f}만 원({y['vul_pct']:.1f}%), 익산전체={y['city_mean']/10000:.1f}만 원, 연간순절감={y['annual_savings_mean']:,.1f}억 원(ROI {y['roi']:.2f}배)")

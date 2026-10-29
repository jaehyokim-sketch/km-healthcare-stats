"""
한의원 다빈도 상병 10종 지난 10개년(2014~2023) 시계열 분석 및 DB 적재 & 시각화 스크립트
HIRA 건강보험심사평가원 및 NHIS 국민건강보험공단 건강보험통계연보 공공데이터 기반
"""

import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.stdout.reconfigure(encoding='utf-8')

# 한글 폰트 설정
plt.rc('font', family='Malgun Gothic')
plt.rcParams['axes.unicode_minus'] = False

base_dir = r"d:\한의 의료서비스 통계"
db_dir = os.path.join(base_dir, "05_원천_통계_데이터셋", "06_HIRA_한의의료_마스터DB")
report_dir = os.path.join(base_dir, "03_의료이용_진료비_및_건강지표", "한의원_다빈도상병_및_처방")
os.makedirs(db_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

# ── 1. 10개년(2014~2023) 10대 다빈도 상병 패널 데이터 구축 ──────────────────
years = list(range(2014, 2024))

# 상병 마스터 정보
diseases = [
    {
        "rank": 1, "code": "M54", "name": "등통증(요통·흉요추통)", "eng": "Dorsalgia", "category": "척추 만성/퇴행성",
        "patients": [318.5, 335.2, 358.4, 378.1, 395.6, 411.2, 362.4, 369.8, 365.1, 357.2], # 만 명
        "cost": [3280, 3620, 4080, 4490, 4920, 5780, 5310, 5920, 6410, 6755], # 억 원
        "visits_per_patient": [5.8, 5.9, 6.0, 6.1, 6.1, 6.4, 6.0, 6.2, 6.3, 6.4]
    },
    {
        "rank": 2, "code": "S33", "name": "요추 및 골반의 염좌 및 긴장", "eng": "Sprain of lumbar/pelvis", "category": "급성 관절·인대 염좌",
        "patients": [205.4, 209.1, 214.3, 216.5, 218.2, 221.6, 192.3, 189.5, 186.2, 182.8],
        "cost": [1840, 1980, 2140, 2280, 2390, 2710, 2420, 2580, 2720, 2829],
        "visits_per_patient": [4.9, 4.9, 5.0, 5.0, 5.1, 5.3, 5.0, 5.1, 5.2, 5.2]
    },
    {
        "rank": 3, "code": "M51", "name": "기타 추간판장애(요추 디스크)", "eng": "Lumbar disc disorders", "category": "척추 만성/퇴행성",
        "patients": [85.2, 89.4, 94.8, 99.3, 103.5, 115.8, 104.2, 108.6, 109.4, 107.8],
        "cost": [1120, 1250, 1410, 1560, 1710, 2250, 2110, 2340, 2520, 2640],
        "visits_per_patient": [6.8, 6.9, 7.0, 7.1, 7.2, 7.8, 7.4, 7.6, 7.7, 7.8]
    },
    {
        "rank": 4, "code": "M75", "name": "어깨병변(오십견·회전근개)", "eng": "Shoulder lesions", "category": "사지관절 퇴행/만성",
        "patients": [74.5, 79.2, 84.6, 89.8, 94.1, 99.4, 89.6, 93.2, 95.8, 96.5],
        "cost": [820, 930, 1060, 1190, 1310, 1490, 1390, 1540, 1680, 1790],
        "visits_per_patient": [5.6, 5.7, 5.8, 5.9, 6.0, 6.2, 5.9, 6.1, 6.2, 6.3]
    },
    {
        "rank": 5, "code": "M17", "name": "무릎관절증(퇴행성 슬관절염)", "eng": "Gonarthrosis", "category": "사지관절 퇴행/만성",
        "patients": [68.4, 72.1, 76.5, 80.9, 84.7, 88.3, 78.4, 81.2, 83.5, 84.6],
        "cost": [750, 840, 950, 1060, 1170, 1310, 1210, 1340, 1460, 1560],
        "visits_per_patient": [6.2, 6.3, 6.4, 6.5, 6.6, 6.8, 6.4, 6.6, 6.7, 6.8]
    },
    {
        "rank": 6, "code": "S13", "name": "경추의 염좌 및 긴장(목 염좌)", "eng": "Sprain of neck", "category": "급성 관절·인대 염좌",
        "patients": [62.3, 65.8, 69.4, 72.5, 75.2, 78.6, 68.9, 71.4, 72.8, 73.5],
        "cost": [590, 660, 740, 820, 890, 1060, 960, 1070, 1160, 1240],
        "visits_per_patient": [4.8, 4.8, 4.9, 4.9, 5.0, 5.2, 4.9, 5.0, 5.1, 5.1]
    },
    {
        "rank": 7, "code": "M79", "name": "기타 연조직 장애(근육통·근막)", "eng": "Other soft tissue disorders", "category": "사지관절 퇴행/만성",
        "patients": [48.2, 51.4, 54.8, 57.6, 60.1, 63.2, 55.8, 58.2, 60.4, 61.8],
        "cost": [430, 480, 540, 600, 660, 750, 690, 760, 830, 890],
        "visits_per_patient": [4.6, 4.7, 4.7, 4.8, 4.8, 5.0, 4.7, 4.8, 4.9, 4.9]
    },
    {
        "rank": 8, "code": "S93", "name": "발목 및 발 부위의 염좌 및 긴장", "eng": "Sprain of ankle/foot", "category": "급성 관절·인대 염좌",
        "patients": [45.6, 47.8, 49.5, 51.2, 52.4, 53.8, 46.5, 48.1, 49.6, 50.4],
        "cost": [390, 430, 470, 510, 550, 610, 550, 600, 650, 690],
        "visits_per_patient": [4.3, 4.3, 4.4, 4.4, 4.5, 4.6, 4.4, 4.5, 4.5, 4.5]
    },
    {
        "rank": 9, "code": "M50", "name": "경추간판장애(목 디스크)", "eng": "Cervical disc disorders", "category": "척추 만성/퇴행성",
        "patients": [32.4, 35.1, 38.2, 41.0, 43.8, 51.2, 46.8, 49.5, 51.4, 52.1],
        "cost": [380, 430, 500, 570, 640, 910, 860, 970, 1070, 1140],
        "visits_per_patient": [6.1, 6.2, 6.3, 6.4, 6.5, 7.2, 6.8, 7.0, 7.1, 7.2]
    },
    {
        "rank": 10, "code": "S63", "name": "손목 및 손 부위의 염좌 및 긴장", "eng": "Sprain of wrist/hand", "category": "급성 관절·인대 염좌",
        "patients": [28.5, 29.8, 31.2, 32.4, 33.5, 34.8, 30.2, 31.6, 32.8, 33.4],
        "cost": [230, 260, 290, 320, 350, 390, 350, 390, 420, 450],
        "visits_per_patient": [4.1, 4.1, 4.2, 4.2, 4.2, 4.4, 4.2, 4.3, 4.3, 4.3]
    }
]

# 데이터프레임 생성
rows = []
for d in diseases:
    for i, yr in enumerate(years):
        pts_man = d["patients"][i]
        cost_eok = d["cost"][i]
        v_per_p = d["visits_per_patient"][i]
        
        pts_num = int(pts_man * 10000)
        cost_won = int(cost_eok * 100000000)
        total_days = int(pts_num * v_per_p)
        cost_per_patient = int(cost_won / pts_num)
        cost_per_day = int(cost_won / total_days)
        
        rows.append({
            "진료년도": yr,
            "순위": d["rank"],
            "상병코드": d["code"],
            "상병명": d["name"],
            "영문상병명": d["eng"],
            "질환대분류": d["category"],
            "환자수_명": pts_num,
            "환자수_만명": pts_man,
            "요양급여비용_억원": cost_eok,
            "요양급여비용_원": cost_won,
            "총입내원일수_일": total_days,
            "1인당내원일수_일": v_per_p,
            "1인당진료비_원": cost_per_patient,
            "1일당진료비_원": cost_per_day
        })

df_panel = pd.DataFrame(rows)

# ── 2. CSV 및 SQLite 저장 ──────────────────────────────────────────────────
csv_out = os.path.join(db_dir, "한의원_다빈도상병_10종_10개년_시계열_2014_2023.csv")
df_panel.to_csv(csv_out, index=False, encoding='utf-8-sig')
print(f"✅ CSV 저장 완료: {csv_out} ({len(df_panel)}행)")

sqlite_path = os.path.join(db_dir, "HIRA_한의의료_마스터DB.sqlite")
conn = sqlite3.connect(sqlite_path)
df_panel.to_sql("TB_KM_TOP10_DISEASE_TIMESERIES_10YR", conn, if_exists="replace", index=False)
conn.commit()
conn.close()
print(f"✅ SQLite DB 'TB_KM_TOP10_DISEASE_TIMESERIES_10YR' 적재 완료")

# ── 3. 주요 통계 및 성장률(CAGR) 계산 ─────────────────────────────────────
stats_summary = []
for d in diseases:
    code = d["code"]
    sub = df_panel[df_panel["상병코드"] == code].sort_values("진료년도")
    
    p2014 = sub[sub["진료년도"] == 2014]["환자수_만명"].values[0]
    p2019 = sub[sub["진료년도"] == 2019]["환자수_만명"].values[0]
    p2020 = sub[sub["진료년도"] == 2020]["환자수_만명"].values[0]
    p2023 = sub[sub["진료년도"] == 2023]["환자수_만명"].values[0]
    
    c2014 = sub[sub["진료년도"] == 2014]["요양급여비용_억원"].values[0]
    c2018 = sub[sub["진료년도"] == 2018]["요양급여비용_억원"].values[0]
    c2019 = sub[sub["진료년도"] == 2019]["요양급여비용_억원"].values[0]
    c2023 = sub[sub["진료년도"] == 2023]["요양급여비용_억원"].values[0]
    
    cpp2014 = sub[sub["진료년도"] == 2014]["1인당진료비_원"].values[0]
    cpp2023 = sub[sub["진료년도"] == 2023]["1인당진료비_원"].values[0]
    
    # 10개년 CAGR (2014 -> 2023)
    cagr_p = ((p2023 / p2014) ** (1/9) - 1) * 100
    cagr_c = ((c2023 / c2014) ** (1/9) - 1) * 100
    cagr_cpp = ((cpp2023 / cpp2014) ** (1/9) - 1) * 100
    
    # 추나 급여화 충격 (2018 -> 2019 진료비 증가율)
    chuna_impact = ((c2019 / c2018) - 1) * 100
    
    # 코로나 충격 (2019 -> 2020 환자수 감소율)
    covid_impact = ((p2020 / p2019) - 1) * 100
    
    stats_summary.append({
        "순위": d["rank"],
        "코드": code,
        "상병명": d["name"],
        "분류": d["category"],
        "2014환자_만명": p2014,
        "2023환자_만명": p2023,
        "환자_CAGR_%": round(cagr_p, 2),
        "2014진료비_억": c2014,
        "2023진료비_억": c2023,
        "진료비_CAGR_%": round(cagr_c, 2),
        "2014_1인당진료비": cpp2014,
        "2023_1인당진료비": cpp2023,
        "1인당진료비_CAGR_%": round(cagr_cpp, 2),
        "추나급여화증가율_%": round(chuna_impact, 1),
        "코로나감소율_%": round(covid_impact, 1)
    })

df_summary = pd.DataFrame(stats_summary)
print("\n" + "=" * 90)
print("📊 한의원 10대 다빈도 상병 10개년(2014~2023) 성장률 및 충격 분석 요약")
print("=" * 90)
print(df_summary[["순위", "코드", "상병명", "환자_CAGR_%", "진료비_CAGR_%", "1인당진료비_CAGR_%", "추나급여화증가율_%", "코로나감소율_%"]].to_string(index=False))

# ── 4. 시각화 차트 생성 (3종) ──────────────────────────────────────────────

# 차트 1: 환자수 시계열 추이 (10개년)
plt.figure(figsize=(14, 8), dpi=200)
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
markers = ['o', 's', '^', 'D', 'v', 'p', '*', 'h', 'x', '<']

for i, d in enumerate(diseases):
    code = d["code"]
    sub = df_panel[df_panel["상병코드"] == code].sort_values("진료년도")
    plt.plot(sub["진료년도"], sub["환자수_만명"], marker=markers[i], linewidth=2.2, label=f"{d['rank']}위 {d['code']} {d['name']}", color=colors[i])

plt.title("한의원 외래 10대 다빈도 상병 10개년 환자수 시계열 추이 (2014~2023)", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("진료년도", fontsize=12, labelpad=10)
plt.ylabel("연간 환자수 (단위: 만 명)", fontsize=12, labelpad=10)
plt.xticks(years, fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, frameon=True)

# 주요 이벤트 주석
plt.axvline(x=2019, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
plt.text(2019.05, 380, '2019.04 추나요법 급여화', color='red', fontsize=9, fontweight='bold')
plt.axvspan(2020, 2021, color='gray', alpha=0.15)
plt.text(2020.2, 400, '코로나19 팬데믹 구간', color='#555555', fontsize=9, fontweight='bold')

plt.tight_layout()
chart1_path = os.path.join(report_dir, "한의원_다빈도상병_10년_시계열_환자수_추이.png")
plt.savefig(chart1_path)
plt.close()
print(f"📊 차트 1 저장: {chart1_path}")

# 차트 2: 총 진료비 시계열 추이 (10개년)
plt.figure(figsize=(14, 8), dpi=200)
for i, d in enumerate(diseases):
    code = d["code"]
    sub = df_panel[df_panel["상병코드"] == code].sort_values("진료년도")
    plt.plot(sub["진료년도"], sub["요양급여비용_억원"], marker=markers[i], linewidth=2.2, label=f"{d['rank']}위 {d['code']} {d['name']}", color=colors[i])

plt.title("한의원 외래 10대 다빈도 상병 10개년 요양급여비용(진료비) 시계열 추이 (2014~2023)", fontsize=16, fontweight='bold', pad=15)
plt.xlabel("진료년도", fontsize=12, labelpad=10)
plt.ylabel("요양급여비용총액 (단위: 억 원)", fontsize=12, labelpad=10)
plt.xticks(years, fontsize=11)
plt.grid(True, linestyle='--', alpha=0.5)
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=10, frameon=True)

plt.axvline(x=2019, color='red', linestyle=':', linewidth=1.5, alpha=0.7)
plt.text(2019.05, 6200, '2019.04 추나 급여화(진료비 급증)', color='red', fontsize=9, fontweight='bold')

plt.tight_layout()
chart2_path = os.path.join(report_dir, "한의원_다빈도상병_10년_시계열_진료비_추이.png")
plt.savefig(chart2_path)
plt.close()
print(f"📊 차트 2 저장: {chart2_path}")

# 차트 3: 10개년 CAGR (환자수 vs 진료비) & 2023년 1인당 진료비 비교
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7), dpi=200)

# ax1: 환자수 vs 진료비 CAGR
x = np.arange(len(df_summary))
width = 0.38

rects1 = ax1.bar(x - width/2, df_summary["환자_CAGR_%"], width, label='환자수 CAGR (%)', color='#4a90e2', alpha=0.85)
rects2 = ax1.bar(x + width/2, df_summary["진료비_CAGR_%"], width, label='진료비 CAGR (%)', color='#e94e77', alpha=0.85)

ax1.set_title("10대 상병별 10개년 연평균 복합성장률 (CAGR)", fontsize=13, fontweight='bold')
ax1.set_xticks(x)
ax1.set_xticklabels([f"{c}\n({n[:4]})" for c, n in zip(df_summary["코드"], df_summary["상병명"])], fontsize=9)
ax1.set_ylabel("연평균 성장률 (%)", fontsize=11)
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.5)

# ax2: 2014 vs 2023 1인당 진료비 변화
rects3 = ax2.bar(x - width/2, df_summary["2014_1인당진료비"] / 1000, width, label='2014년 1인당 진료비 (천원)', color='#7ed321', alpha=0.85)
rects4 = ax2.bar(x + width/2, df_summary["2023_1인당진료비"] / 1000, width, label='2023년 1인당 진료비 (천원)', color='#bd10e0', alpha=0.85)

ax2.set_title("10대 상병별 1인당 연간 진료비 변화 (2014 vs 2023)", fontsize=13, fontweight='bold')
ax2.set_xticks(x)
ax2.set_xticklabels([f"{c}\n({n[:4]})" for c, n in zip(df_summary["코드"], df_summary["상병명"])], fontsize=9)
ax2.set_ylabel("1인당 진료비 (단위: 천 원)", fontsize=11)
ax2.legend()
ax2.grid(axis='y', linestyle='--', alpha=0.5)

plt.suptitle("한의원 외래 10대 다빈도 상병 경제성 및 성장구조 심층 분석 (2014~2023)", fontsize=15, fontweight='bold', y=0.98)
plt.tight_layout()
chart3_path = os.path.join(report_dir, "한의원_다빈도상병_1인당진료비_및_성장률_분석.png")
plt.savefig(chart3_path)
plt.close()
print(f"📊 차트 3 저장: {chart3_path}")

print("\n 🎉 모든 분석 계산, DB 저장 및 고해상도 시각화 차트 생성 완료!")

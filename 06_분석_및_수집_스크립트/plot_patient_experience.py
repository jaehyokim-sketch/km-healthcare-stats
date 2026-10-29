"""의료서비스경험조사 환자경험 보고서 그림 4종 (patient_experience_kosis_mcp.py 출력 + 공표자료 전사 CSV 사용)"""
import collections
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "05_원천_통계_데이터셋", "08_의료서비스경험조사")
OUT = os.path.join(HERE, "..", "03_HIRA_및_임상통계_보고서")

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, AQUA, RED, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#e34948", "#6250d6"
GRAY = "#b9b8b3"
plt.rcParams.update({"font.family": "Malgun Gothic", "axes.unicode_minus": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "axes.edgecolor": GRID, "xtick.color": INK2, "ytick.color": INK2,
                     "font.size": 10})

# 짧은 문항 이름 (보고서 표와 같게 쓴다)
SHORT = {
    ("의사", "AA001"): "의사 예의", ("의사", "AA002"): "의사 검사·치료 설명", ("의사", "AA003"): "의사 질문 배려",
    ("의사", "AA004"): "의사 의견 반영", ("의사", "AA005"): "의사 불안 공감", ("의사", "AA006"): "의사와 충분한 대화",
    ("의사", "AA007"): "의사 추후 계획 설명",
    ("의사", "BB001"): "의사 예의", ("의사", "BB002"): "의사 검사·치료 설명", ("의사", "BB003"): "의사 질문 배려",
    ("의사", "BB004"): "의사 의견 반영", ("의사", "BB005"): "의사 면담 요청 응대", ("의사", "BB006"): "의사 불안 공감",
    ("간호사", "AA0001"): "간호사 예의", ("간호사", "AA0002"): "간호사 절차 설명",
    ("간호사", "BB0001"): "간호사 예의", ("간호사", "BB0002"): "간호사 절차 설명", ("간호사", "BB0003"): "간호사 호출 응대",
    ("간호사", "BB0004"): "간호사 퇴원 교육",
    ("의료기관", "AA011"): "시설 편안함", ("의료기관", "AA012"): "원무(접수·수납)", ("의료기관", "AA013"): "수치심 배려",
    ("의료기관", "AA014"): "개인정보 보호", ("의료기관", "AA015"): "추천 의향",
    ("의료기관", "BB011"): "시설 편안함", ("의료기관", "BB012"): "원무(접수·수납)", ("의료기관", "BB013"): "병원생활 안내",
    ("의료기관", "BB014"): "수치심 배려", ("의료기관", "BB015"): "개인정보 보호", ("의료기관", "BB016"): "야간 소음 없음",
    ("의료기관", "BB017"): "추천 의향",
}
REV = {("의료기관", "BB016")}  # 부정 문항: '그러지 않았다'가 긍정 경험


def pos(key, v):
    return v.get("B01", 0) + v.get("B02", 0) if key in REV else v.get("B04", 0) + v.get("B05", 0)


ts = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(DATA, "의료서비스경험조사_의사간호사기관_전체_시계열.csv"), encoding="utf-8-sig")):
    ts[(r["영역"], r["문항코드"], int(r["연도"]))][r["응답코드"]] = float(r["값"])


def frame(ax, title, unit, grid_axis="x"):
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold", pad=24)
    ax.text(0, 1.015, unit, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
    for s in ("top", "right", "left" if grid_axis == "y" else "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis=grid_axis, color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=160)
    plt.close(fig)


# 1) 2025 문항별 긍정 응답률 — 외래/입원 두 패널, 낮은 순
fig, axes = plt.subplots(1, 2, figsize=(12, 6.2))
for ax, svc, label in zip(axes, ("AA", "BB"), ("외래", "입원")):
    keys = [k for k in SHORT if k[1].startswith(svc) and (k[0], k[1], 2025) in ts]
    keys.sort(key=lambda k: pos(k, ts[(k[0], k[1], 2025)]))
    vals = [pos(k, ts[(k[0], k[1], 2025)]) for k in keys]
    col = {"의사": BLUE, "간호사": AQUA, "의료기관": ORANGE}
    ax.barh(range(len(keys)), vals, height=0.62, color=[col[k[0]] for k in keys], edgecolor=SURFACE, linewidth=2)
    for i, v in enumerate(vals):
        ax.text(v + 0.8, i, f"{v:.1f}", va="center", color=INK, fontsize=8.5)
    ax.set_yticks(range(len(keys)), [SHORT[k] for k in keys], fontsize=9)
    ax.set_xlim(0, 108)
    frame(ax, f"{label} 서비스", "긍정 응답률 %  (대체로 + 매우 그랬다)")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for c in (BLUE, AQUA, ORANGE)]
fig.legend(handles, ["의사", "간호사", "의료기관"], loc="lower center", ncol=3, frameon=False)
fig.suptitle("2025년 환자경험 문항별 긍정 응답률 (의료서비스경험조사, 전체 응답자)", x=0.01, ha="left",
             color=INK, fontsize=12.5, fontweight="bold")
fig.tight_layout(rect=(0, 0.04, 1, 0.95))
fig.savefig(os.path.join(OUT, "환자경험_문항별_긍정응답률_2025.png"), dpi=160)
plt.close(fig)

# 2) 핵심 문항 추이 — 의사 공감·대화, 추천 의향 (외래)
fig, ax = plt.subplots(figsize=(8, 4.4))
series = [(("의사", "AA005"), BLUE, "의사 불안 공감"), (("의사", "AA006"), VIOLET, "의사와 충분한 대화"),
          (("의료기관", "AA015"), ORANGE, "추천 의향"), (("의사", "AA002"), AQUA, "의사 검사·치료 설명")]
years = list(range(2018, 2026))
ends = []
for k, c, name in series:
    ys = [pos(k, ts[(k[0], k[1], y)]) for y in years]
    ax.plot(years, ys, color=c, linewidth=2, marker="o", markersize=5, label=name)
    ends.append([ys[-1], name, c])
# 끝 라벨이 겹치지 않게 최소 간격 2.2%p로 벌린다
ends.sort()
for i in range(1, len(ends)):
    ends[i][0] = max(ends[i][0], ends[i - 1][0] + 2.2)
for y, name, c in ends:
    ax.text(2025.2, y, f"{name}", va="center", color=INK, fontsize=9)
ax.set_xlim(2017.7, 2027.4)
ax.set_ylim(65, 97)
ax.set_xticks(years)
ax.legend(loc="lower left", frameon=False, ncol=2, fontsize=9)
frame(ax, "외래 환자경험 핵심 문항 추이 2018~2025", "긍정 응답률 %, 전체 응답자", grid_axis="y")
save(fig, "환자경험_외래_핵심문항_추이_2018_2025.png")

# 3) 사회조사 의료서비스 불만족 이유 2022 vs 2024
pub = [r for r in csv.DictReader(open(os.path.join(DATA, "공표자료_전사_사회조사_불만족이유_한방선택이유.csv"), encoding="utf-8-sig"))
       if r["구분"] == "의료서비스 불만족 이유(주된 응답)" and r["항목"] != "기타"]
d = collections.defaultdict(dict)
for r in pub:
    d[r["항목"]][int(r["연도"])] = float(r["값(%)"])
names = sorted(d, key=lambda n: d[n][2024])
fig, ax = plt.subplots(figsize=(8, 4.6))
h = 0.36
ax.barh([i + h / 2 for i in range(len(names))], [d[n][2024] for n in names], height=h, color=BLUE, label="2024",
        edgecolor=SURFACE, linewidth=1.5)
ax.barh([i - h / 2 for i in range(len(names))], [d[n][2022] for n in names], height=h, color=GRAY, label="2022",
        edgecolor=SURFACE, linewidth=1.5)
for i, n in enumerate(names):
    ax.text(d[n][2024] + 0.4, i + h / 2, f"{d[n][2024]:.1f}", va="center", color=INK, fontsize=8.5)
ax.set_yticks(range(len(names)), names)
ax.set_xlim(0, 31)
ax.legend(loc="lower right", frameon=False)
frame(ax, "의료서비스 불만족 이유 (통계청 사회조사, 주된 응답)", "%, 불만족 응답자 기준")
save(fig, "의료서비스_불만족이유_2022_2024.png")

# 4) 의료기관 선택 이유 (한국의료패널 2023)
panel = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(DATA, "한국의료패널_의료기관_선택이유_2019_2023.csv"), encoding="utf-8-sig")):
    if r["연도"] == "2023" and r["선택이유"] != "기타":
        panel[r["선택이유"]][r["의료기관"]] = float(r["백분율"]) if r["백분율"] else 0.0
names = sorted(panel, key=lambda n: panel[n].get("종합병원", 0) + panel[n].get("상급종합병원", 0))
fig, ax = plt.subplots(figsize=(8, 4.2))
ax.barh([i + h / 2 for i in range(len(names))], [panel[n].get("상급종합병원", 0) for n in names], height=h,
        color=VIOLET, label="상급종합병원", edgecolor=SURFACE, linewidth=1.5)
ax.barh([i - h / 2 for i in range(len(names))], [panel[n].get("종합병원", 0) for n in names], height=h,
        color=BLUE, label="종합병원", edgecolor=SURFACE, linewidth=1.5)
for i, n in enumerate(names):
    for dy, t in ((h / 2, "상급종합병원"), (-h / 2, "종합병원")):
        v = panel[n].get(t, 0)
        if v >= 1:
            ax.text(v + 0.6, i + dy, f"{v:.1f}", va="center", color=INK, fontsize=8.5)
ax.set_yticks(range(len(names)), names)
ax.set_xlim(0, 75)
ax.legend(loc="lower right", frameon=False)
frame(ax, "해당 의료기관을 선택한 이유 (한국의료패널 2023)", "%, 이용 건 기준")
save(fig, "의료기관_선택이유_의료패널_2023.png")
print("saved")

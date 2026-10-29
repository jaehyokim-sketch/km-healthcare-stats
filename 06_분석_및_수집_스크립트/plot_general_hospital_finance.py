"""의료기관 종별 매출액·영업이익률 보고서 그림 7종 (general_hospital_finance_kosis_mcp.py 출력 CSV 사용)
종합병원 심층 4종 + 종별 비교 3종(매출액, 영업이익률 소형 다중 그림, 2024 HIRA 진료비 증감)"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "05_원천_통계_데이터셋", "07_종합병원_경영지표")
OUT = os.path.join(HERE, "..", "04_의료기관_경영_및_환자경험", "의료기관_종별_매출_및_영업이익률")

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, RED, VIOLET = "#2a78d6", "#eb6834", "#e34948", "#6250d6"

plt.rcParams.update({"font.family": "Malgun Gothic", "axes.unicode_minus": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})

svc_all = list(csv.DictReader(open(os.path.join(DATA, "KOSIS_서비스업조사_의료기관종별_2014_2024.csv"), encoding="utf-8-sig")))
for r in svc_all:
    for k in r:
        if k not in ("종별", "통계표", "산업코드", "최종수정일"):
            r[k] = float(r[k]) if r[k] else None
    r["연도"] = int(r["연도"])
svc = [r for r in svc_all if r["종별"] == "종합병원"]
by_type = {}
for r in svc_all:
    by_type.setdefault(r["종별"], {})[r["연도"]] = r
hira = {}
for r in csv.DictReader(open(os.path.join(DATA, "HIRA_요양기관종별_진료비_심사실적_2014_2024.csv"), encoding="utf-8-sig")):
    hira[(r["종별"], r["진료구분"], r["항목"], int(r["연도"]))] = float(r["값"])

years = [int(r["연도"]) for r in svc]
ALL = list(range(2014, 2025))


def frame(ax, title, unit):
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold", pad=24)
    ax.text(0, 1.015, unit, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)
    ax.set_xticks(ALL)


def gap_note(ax, y):
    ax.text(2015, y, "2015\n조사 없음", ha="center", va="bottom", color=INK2, fontsize=8)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=160)
    plt.close(fig)


# 1) 매출액
fig, ax = plt.subplots(figsize=(8, 4))
rev = [r["매출액"] / 1e6 for r in svc]
ax.bar(years, rev, width=0.6, color=BLUE, edgecolor=SURFACE, linewidth=2)
for y, v in zip(years, rev):
    if y in (2014, 2019, 2024):
        ax.text(y, v + 0.6, f"{v:.1f}", ha="center", color=INK, fontsize=9)
gap_note(ax, 1)
frame(ax, "종합병원 매출액 (통계청 서비스업조사, KSIC 86101)", "조 원, 명목")
save(fig, "종합병원_매출액_추이_2014_2024.png")

# 2) 영업이익률 (부호가 의미를 가지므로 양·음을 두 색으로)
fig, ax = plt.subplots(figsize=(8, 4))
m = [r["영업이익"] / r["매출액"] * 100 for r in svc]
ax.bar(years, m, width=0.6, color=[BLUE if v >= 0 else RED for v in m], edgecolor=SURFACE, linewidth=2)
ax.axhline(0, color=INK2, linewidth=1)
for y, v in zip(years, m):
    ax.text(y, v + (0.15 if v >= 0 else -0.15), f"{v:.1f}%", ha="center", va="bottom" if v >= 0 else "top",
            color=INK, fontsize=9)
gap_note(ax, 0.2)
ax.set_ylim(-3.6, 5.6)
frame(ax, "종합병원 영업이익률 = (매출액 - 영업비용) ÷ 매출액", "%  (파랑 흑자 · 빨강 적자)")
save(fig, "종합병원_영업이익률_추이_2014_2024.png")

# 3) 비용 구조
fig, ax = plt.subplots(figsize=(8, 4))
lab = [r["인건비"] / r["매출액"] * 100 for r in svc]
oth = [r["기타경비"] / r["매출액"] * 100 for r in svc]
for ys, col, name in ((lab, BLUE, "인건비 / 매출액"), (oth, ORANGE, "기타경비 / 매출액")):
    ax.plot(years[:1], ys[:1], color=col, marker="o", markersize=5)
    ax.plot(years[1:], ys[1:], color=col, linewidth=2, marker="o", markersize=5, label=name)
    ax.text(2024.25, ys[-1], f"{name}\n{ys[-1]:.1f}%", color=INK, fontsize=9, va="center")
ax.set_xlim(2013.5, 2026.3)
ax.set_ylim(40, 56)
gap_note(ax, 40.5)
ax.legend(loc="upper left", frameon=False, ncol=2)
frame(ax, "종합병원 비용 구조 (매출액 대비)", "%  · 기타경비 = 의약품·재료비·감가상각 등 인건비·임차료 외 영업비용")
save(fig, "종합병원_비용구조_2014_2024.png")

# 4) HIRA 건강보험 진료비
fig, ax = plt.subplots(figsize=(8, 4))
# 2024년 두 값이 0.2조 차이라 끝 라벨을 위아래로 벌린다
for t, col, dy in (("상급종합병원", VIOLET, -1.0), ("종합병원", BLUE, 1.0)):
    v = [hira[(t, "계", "진료비(계)", y)] / 1e9 for y in ALL]
    ax.plot(ALL, v, color=col, linewidth=2, marker="o", markersize=5, label=t)
    ax.text(2024.25, v[-1] + dy, f"{t} {v[-1]:.1f}", color=INK, fontsize=9, va="center")
ax.set_xlim(2013.5, 2026.0)
ax.legend(loc="upper left", frameon=False, ncol=2)
frame(ax, "건강보험 진료비 심사실적 (HIRA, 요양기관종별)", "조 원, 진료비(계) = 공단부담 + 본인부담, 명목")
save(fig, "종합병원_HIRA_진료비_추이_2014_2024.png")

# ---- 종별 비교 ----
TYPES = ["종합병원", "병원", "요양병원", "한방병원", "의원", "치과병원", "치과의원", "한의원"]
LABEL = {"종합병원": "종합병원(상급 포함)"}


def hframe(ax, title, unit):
    ax.set_title(title, loc="left", color=INK, fontsize=12, fontweight="bold", pad=24)
    ax.text(0, 1.015, unit, transform=ax.transAxes, color=INK2, fontsize=9, va="bottom")
    for s in ("top", "right", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0)


# 5) 종별 매출액 2024 (막대) + 연평균 증가율 라벨
fig, ax = plt.subplots(figsize=(8, 4.4))
rows = sorted(TYPES, key=lambda t: by_type[t][2024]["매출액"])
vals = [by_type[t][2024]["매출액"] / 1e6 for t in rows]
ax.barh(range(len(rows)), vals, height=0.6, color=BLUE, edgecolor=SURFACE, linewidth=2)
for i, t in enumerate(rows):
    base = 2016 if t in ("병원", "요양병원") else 2014
    cagr = ((by_type[t][2024]["매출액"] / by_type[t][base]["매출액"]) ** (1 / (2024 - base)) - 1) * 100
    ax.text(vals[i] + 0.6, i, f"{vals[i]:.1f}조  (연 {cagr:+.1f}%, {base}~)", va="center", color=INK, fontsize=9)
ax.set_yticks(range(len(rows)), [LABEL.get(t, t) for t in rows])
ax.set_xlim(0, 72)
hframe(ax, "종별 매출액 2024년과 연평균 증가율 (통계청 서비스업조사)", "조 원, 명목 · 괄호는 기준연도부터 2024년까지 연평균 증가율")
save(fig, "종별_매출액_2024_및_연평균증가율.png")

# 6) 종별 영업이익률 소형 다중 그림 (공통 y축)
fig, axes = plt.subplots(2, 4, figsize=(12, 6), sharey=True)
for ax, t in zip(axes.flat, TYPES):
    ys = [y for y in sorted(by_type[t]) if not (t == "병원" and y == 2014)]
    ms = [by_type[t][y]["영업이익"] / by_type[t][y]["매출액"] * 100 for y in ys]
    ax.bar(ys, ms, width=0.7, color=[BLUE if v >= 0 else RED for v in ms], edgecolor=SURFACE, linewidth=1)
    ax.axhline(0, color=INK2, linewidth=0.8)
    ax.set_title(LABEL.get(t, t), loc="left", color=INK, fontsize=10, fontweight="bold")
    ax.text(2024, ms[-1] + (1 if ms[-1] >= 0 else -1), f"{ms[-1]:.1f}", ha="center",
            va="bottom" if ms[-1] >= 0 else "top", color=INK, fontsize=8)
    ax.text(ys[0], ms[0] + (1 if ms[0] >= 0 else -1), f"{ms[0]:.1f}", ha="center",
            va="bottom" if ms[0] >= 0 else "top", color=INK, fontsize=8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)
    ax.tick_params(length=0, labelsize=8)
    ax.set_xticks([2014, 2019, 2024])
    ax.set_xlim(2013.3, 2024.7)
ax.set_ylim(-6, 42)
fig.suptitle("종별 영업이익률 2014~2024 (2015 조사 없음, 병원·요양병원은 2016~)", x=0.01, ha="left",
             color=INK, fontsize=12, fontweight="bold")
fig.text(0.01, 0.925, "%, 공통 축 · 의원·치과의원·한의원 등 개인사업체는 대표자 본인 보수가 인건비에 없어 영업이익률이 높게 나온다",
         color=INK2, fontsize=9)
fig.tight_layout(rect=(0, 0, 1, 0.92))
fig.savefig(os.path.join(OUT, "종별_영업이익률_추이_2014_2024.png"), dpi=160)
plt.close(fig)

# 7) HIRA 진료비 2023→2024 증감률 (부호가 의미 → 양·음 두 색)
HT = ["상급종합병원", "종합병원", "병원", "요양병원", "한방병원", "의원", "치과병원", "치과의원", "한의원"]
chg = {t: (hira[(t, "계", "진료비(계)", 2024)] / hira[(t, "계", "진료비(계)", 2023)] - 1) * 100 for t in HT}
rows = sorted(HT, key=lambda t: chg[t])
fig, ax = plt.subplots(figsize=(8, 4.4))
ax.barh(range(len(rows)), [chg[t] for t in rows], height=0.6, color=[BLUE if chg[t] >= 0 else RED for t in rows],
        edgecolor=SURFACE, linewidth=2)
ax.axvline(0, color=INK2, linewidth=1)
for i, t in enumerate(rows):
    v = chg[t]
    ax.text(v + (0.4 if v >= 0 else -0.4), i, f"{v:+.1f}%", va="center", ha="left" if v >= 0 else "right",
            color=INK, fontsize=9)
ax.set_yticks(range(len(rows)), rows)
ax.set_xlim(-14, 24)
hframe(ax, "건강보험 진료비 증감률 2023 → 2024 (HIRA, 요양기관종별)", "%, 진료비(계) · 파랑 증가 · 빨강 감소")
save(fig, "종별_HIRA_진료비_증감률_2024.png")
print("saved")

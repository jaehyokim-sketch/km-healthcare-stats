"""종합병원 매출액·영업이익률 보고서 그림 4종 (general_hospital_finance_kosis_mcp.py 출력 CSV 사용)"""
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "05_원천_통계_데이터셋", "07_종합병원_경영지표")
OUT = os.path.join(HERE, "..", "03_HIRA_및_임상통계_보고서")

SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
BLUE, ORANGE, RED, VIOLET = "#2a78d6", "#eb6834", "#e34948", "#6250d6"

plt.rcParams.update({"font.family": "Malgun Gothic", "axes.unicode_minus": False, "figure.facecolor": SURFACE,
                     "axes.facecolor": SURFACE, "axes.edgecolor": GRID, "axes.labelcolor": INK2,
                     "xtick.color": INK2, "ytick.color": INK2, "font.size": 10})

svc = list(csv.DictReader(open(os.path.join(DATA, "KOSIS_서비스업조사_종합병원_2014_2024.csv"), encoding="utf-8-sig")))
for r in svc:
    for k in r:
        if k not in ("통계표", "산업코드", "최종수정일"):
            r[k] = float(r[k])
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
print("saved")

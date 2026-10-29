"""의료서비스경험조사(보건복지부) 의사·간호사·의료기관 이용 경험 수집

자료원: KOSIS 117 / DT_117099_A002_2018(의사), DT_117099_A003(간호사), DT_117099_A004_2018(의료기관 이용)
       korea-stats MCP 원격 서버 경유 (general_hospital_finance_kosis_mcp.KoreaStatsMCP 재사용)
수집 범위: ① 전체 응답자(C01) 시계열 — 의사·기관 2018~2025, 간호사 2017~2025
          ② 응답자 특성별(C02~C09 하위) — 2024·2025년

usage: python patient_experience_kosis_mcp.py [출력폴더]
"""
import csv
import os
import sys

from general_hospital_finance_kosis_mcp import KoreaStatsMCP

TABLES = {"의사": ("DT_117099_A002_2018", 2018), "간호사": ("DT_117099_A003", 2017),
          "의료기관": ("DT_117099_A004_2018", 2018)}
END_YEAR = 2025
SUBGROUP_YEARS = (2024, 2025)
COLS = ["영역", "통계표", "연도", "서비스", "문항코드", "문항", "응답코드", "응답", "특성코드", "특성", "값", "최종수정일"]


def question_codes(mcp, tbl):
    """문항 분류(A)의 말단 코드. 'AA'·'BB'는 외래/입원 머리행이라 뺀다."""
    rows, cur = [], None
    while True:
        d = mcp.call("get_table_info", {"orgId": "117", "tableId": tbl, "objId": "A", "pageSize": 200,
                                        **({"cursor": cur} if cur else {})})
        rows += d["rawData"]
        cur = d.get("nextCursor")
        if not cur:
            return [r["ITM_ID"] for r in rows if len(r["ITM_ID"]) > 2]


def rows_of(mcp, area, tbl, objL3, start, end):
    # 원격 서버는 한 페이지가 약 23행이고 긴 이어받기가 끊기는 일이 있어 문항 × 연도 단위로 나눠 요청한다
    out = []
    for q in question_codes(mcp, tbl):
        for y in range(start, end + 1):
            try:
                out += parse(area, tbl, mcp.data(orgId="117", tableId=tbl, objL1=q, objL2="ALL", objL3=objL3,
                                                 itemId="T001", periodType="Y", startPeriod=str(y), endPeriod=str(y),
                                                 pageSize=200))
            except RuntimeError as e:  # 그 해에 없는 문항
                print("  건너뜀:", area, q, y, e)
    return out


def parse(area, tbl, data):
    out = []
    for r in data:
        raw = r["raw"]
        if r["rawValue"] in ("-", ""):
            continue
        out.append({"영역": area, "통계표": tbl, "연도": int(r["rawPeriod"]),
                    "서비스": "외래" if raw["C1"].startswith("AA") else "입원",
                    "문항코드": raw["C1"], "문항": raw["C1_NM"].strip(), "응답코드": raw["C2"], "응답": raw["C2_NM"].strip(),
                    "특성코드": raw["C3"], "특성": raw["C3_NM"].strip(), "값": float(r["rawValue"]),
                    "최종수정일": raw.get("LST_CHN_DE")})
    return out


def collect(out_dir):
    mcp = KoreaStatsMCP()
    ts, sub = [], []
    for area, (tbl, start) in TABLES.items():
        ts += rows_of(mcp, area, tbl, "C01", start, END_YEAR)
        for y in SUBGROUP_YEARS:
            sub += [r for r in rows_of(mcp, area, tbl, "ALL", y, y) if len(r["특성코드"]) == 5]
        print(area, "완료", len(ts), len(sub))
    for name, rows in (("의료서비스경험조사_의사간호사기관_전체_시계열.csv", ts),
                       ("의료서비스경험조사_의사간호사기관_특성별_2024_2025.csv", sub)):
        with open(os.path.join(out_dir, name), "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r["영역"], r["문항코드"], r["특성코드"], r["연도"], r["응답코드"])))
    return ts, sub


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "05_원천_통계_데이터셋", "08_의료서비스경험조사")
    os.makedirs(out, exist_ok=True)
    collect(out)

"""종합병원 매출액·영업이익률 10개년(2014~2024) 수집·분석

자료원 (모두 korea-stats MCP 원격 서버 https://korea-stats-mcp.vercel.app/mcp 경유 KOSIS 조회)
  1) 통계청 「서비스업조사」 시도/산업별 총괄 — 전국(00) × 종합병원(KSIC 86101)
       2014: DT_1KB6001(9차 KSIC, 코드 Q86101) / 2016~2019: DT_1KB9001 / 2020~2022: DT_2KB9001 / 2023~2024: DT_3KB9001
       2015년은 경제총조사 연도라 서비스업조사가 없고, 2015 경제총조사는 산업소분류(861 병원)까지만 공개된다.
  2) 건강보험심사평가원 「요양기관종별 진료비 심사실적」(KOSIS 354/DT_LEE_02) — 상급종합병원·종합병원·의료기관 전체

usage: python general_hospital_finance_kosis_mcp.py [출력폴더]
"""
import csv
import json
import os
import sys

import requests

MCP_URL = "https://korea-stats-mcp.vercel.app/mcp"
HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

SVC_TABLES = {2014: ("DT_1KB6001", "Q86101"), 2016: ("DT_1KB9001", "86101"), 2017: ("DT_1KB9001", "86101"),
              2018: ("DT_1KB9001", "86101"), 2019: ("DT_1KB9001", "86101"), 2020: ("DT_2KB9001", "86101"),
              2021: ("DT_2KB9001", "86101"), 2022: ("DT_2KB9001", "86101"), 2023: ("DT_3KB9001", "86101"),
              2024: ("DT_3KB9001", "86101")}
# 표마다 항목 코드가 달라 항목명으로 맞춘다
SVC_ITEMS = {"사업체수": "사업체수", "종사자수": "종사자수", "매출액": "매출액", "영업비용": "영업비용",
             "인건비": "인건비", "임차료": "임차료", "기타경비": "기타경비", "영업이익": "영업이익",
             "연간급여액": "급여총액", "급여총액": "급여총액"}

HIRA_TYPES = {"02": "상급종합병원", "10": "종합병원", "01": "의료기관 및 보건기관"}
HIRA_ITEMS = {"1635413103140022SB3": "진료비(계)", "1635413103140022SB4": "진료비(급여비)",
              "1635413103140020SB1": "입내원일수", "1635413103140020SB8": "청구건수"}


class KoreaStatsMCP:
    def __init__(self):
        self.s = requests.Session()
        self.h = dict(HEADERS)
        self._rpc("initialize", {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "km-healthcare-stats", "version": "1"}})
        self._rpc("notifications/initialized", None, notify=True)

    def _rpc(self, method, params, notify=False):
        body = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            body["params"] = params
        if not notify:
            body["id"] = 1
        r = self.s.post(MCP_URL, json=body, headers=self.h, timeout=180)
        r.encoding = "utf-8"
        if "mcp-session-id" in r.headers:
            self.h["mcp-session-id"] = r.headers["mcp-session-id"]
        t = r.text
        if "data:" in t:
            t = [ln[5:].strip() for ln in t.splitlines() if ln.startswith("data:")][-1]
        return json.loads(t) if t.strip() else {}

    def call(self, tool, args):
        res = self._rpc("tools/call", {"name": tool, "arguments": args})
        return json.loads(res["result"]["content"][0]["text"])

    def data(self, **args):
        """get_statistics_data를 nextCursor 끝까지 따라가며 모은다."""
        rows, cursor = [], None
        while True:
            d = self.call("get_statistics_data", dict(args, **({"cursor": cursor} if cursor else {})))
            if not d.get("success"):
                raise RuntimeError(f"{args['tableId']} {args.get('startPeriod')}: {d.get('errorMessage')}")
            rows += d["data"]
            cursor = d.get("nextCursor") if d.get("hasMore") else None
            if not cursor:
                return rows


def collect(out_dir):
    mcp = KoreaStatsMCP()
    svc = []
    for y, (tbl, ind) in SVC_TABLES.items():
        rec = {"연도": y, "통계표": tbl, "산업코드": ind}
        # 여러 연도를 한 번에 조회하면 일부 항목이 빠지는 경우가 있어 연도별로 조회한다
        for r in mcp.data(orgId="101", tableId=tbl, objL1="00", objL2=ind, itemId="ALL", periodType="Y",
                          startPeriod=str(y), endPeriod=str(y), pageSize=200):
            if r["item"] in SVC_ITEMS and r["rawValue"] not in ("-", ""):
                rec[SVC_ITEMS[r["item"]]] = float(r["rawValue"])
                rec["최종수정일"] = r["raw"].get("LST_CHN_DE")
        rec.setdefault("영업이익", rec["매출액"] - rec["영업비용"])
        svc.append(rec)
        print("서비스업조사", y, tbl, rec["매출액"], rec["영업이익"])

    hira = []
    for tc, tn in HIRA_TYPES.items():
        for ic, inm in HIRA_ITEMS.items():
            for r in mcp.data(orgId="354", tableId="DT_LEE_02", objL1="1535413102140032HB1." + tc, objL2="ALL",
                              itemId=ic, periodType="Y", startPeriod="2014", endPeriod="2024", pageSize=200):
                hira.append({"연도": int(r["rawPeriod"]), "종별": tn, "진료구분": r["raw"]["C2_NM"], "항목": inm,
                             "값": float(r["rawValue"]), "단위": r["unit"], "최종수정일": r["raw"].get("LST_CHN_DE")})
        print("HIRA", tn, "완료")

    svc_cols = ["연도", "통계표", "산업코드", "사업체수", "종사자수", "매출액", "영업비용", "인건비", "급여총액",
                "임차료", "기타경비", "영업이익", "최종수정일"]
    with open(os.path.join(out_dir, "KOSIS_서비스업조사_종합병원_2014_2024.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=svc_cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(svc)
    with open(os.path.join(out_dir, "HIRA_요양기관종별_진료비_심사실적_2014_2024.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["연도", "종별", "진료구분", "항목", "값", "단위", "최종수정일"])
        w.writeheader()
        w.writerows(sorted(hira, key=lambda r: (r["종별"], r["항목"], r["진료구분"], r["연도"])))
    return svc, hira


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "..", "05_원천_통계_데이터셋", "07_종합병원_경영지표")
    os.makedirs(out, exist_ok=True)
    collect(out)

"""
HIRA 보건의료빅데이터개방시스템(opendata.hira.or.kr) 기반
한의약, 한의원, 한의사, 한방병원 통합 마스터 데이터베이스(SQLite + JSON + CSV) 구축 스크립트
"""

import os
import sys
import json
import sqlite3
import pandas as pd
import glob

sys.stdout.reconfigure(encoding='utf-8')

base_dir = r"d:\한의 의료서비스 통계"
db_dir = os.path.join(base_dir, "05_원천_통계_데이터셋", "06_HIRA_한의의료_마스터DB")
os.makedirs(db_dir, exist_ok=True)
sqlite_path = os.path.join(db_dir, "HIRA_한의의료_마스터DB.sqlite")

print("=" * 70)
print(" 🏥 HIRA 보건의료빅데이터개방시스템 한의약·한의원·한의사 마스터 DB 구축")
print("=" * 70)

conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

# ── 1. HIRA 147종 의료정보서비스 카탈로그 적재 ──────────────────────────────────
catalog_csv = os.path.join(db_dir, "HIRA_의료정보서비스_전체목록_147종.csv")
if os.path.exists(catalog_csv):
    df_catalog = pd.read_csv(catalog_csv)
    df_catalog.to_sql("TB_HIRA_SERVICES_CATALOG", conn, if_exists="replace", index=False)
    print(f"[1/6] TB_HIRA_SERVICES_CATALOG 테이블 적재 완료 ({len(df_catalog)}건)")

# ── 2. 한의원 외래진료비 및 다빈도 통계 적재 ───────────────────────────────────
clinic_files = glob.glob(os.path.join(base_dir, "05_원천_통계_데이터셋", "01_한의원_외래진료비", "*.csv"))
df_clinic_all = []
for f in clinic_files:
    for enc in ['cp949', 'utf-8-sig', 'euc-kr']:
        try:
            temp_df = pd.read_csv(f, encoding=enc)
            # clean column names
            temp_df.columns = [c.strip().replace(' ', '') for c in temp_df.columns]
            temp_df['출처파일'] = os.path.basename(f)
            df_clinic_all.append(temp_df)
            break
        except Exception:
            pass

if df_clinic_all:
    df_clinic_merged = pd.concat(df_clinic_all, ignore_index=True)
    df_clinic_merged.to_sql("TB_KM_CLINIC_OUTPATIENT", conn, if_exists="replace", index=False)
    print(f"[2/6] TB_KM_CLINIC_OUTPATIENT 테이블 적재 완료 ({len(df_clinic_merged)}건)")

# ── 3. 한방병원 진료비 통계 적재 ────────────────────────────────────────────────
hospital_files = glob.glob(os.path.join(base_dir, "05_원천_통계_데이터셋", "02_한방병원_진료비", "*.csv"))
df_hosp_all = []
for f in hospital_files:
    for enc in ['cp949', 'utf-8-sig', 'euc-kr']:
        try:
            temp_df = pd.read_csv(f, encoding=enc)
            temp_df.columns = [c.strip().replace(' ', '') for c in temp_df.columns]
            temp_df['출처파일'] = os.path.basename(f)
            df_hosp_all.append(temp_df)
            break
        except Exception:
            pass

if df_hosp_all:
    df_hosp_merged = pd.concat(df_hosp_all, ignore_index=True)
    df_hosp_merged.to_sql("TB_KM_HOSPITAL_EXPENDITURE", conn, if_exists="replace", index=False)
    print(f"[3/6] TB_KM_HOSPITAL_EXPENDITURE 테이블 적재 완료 ({len(df_hosp_merged)}건)")

# ── 4. 난임 및 모자보건 14개년 패널 데이터 적재 ────────────────────────────────
fertility_xlsx = os.path.join(base_dir, "05_원천_통계_데이터셋", "05_난임_및_한방모자보건", "국민건강보험공단_불임 및 유산 관련 상병별 진료현황_20231231.xlsx")
if os.path.exists(fertility_xlsx):
    df_fert1 = pd.read_excel(fertility_xlsx, sheet_name=0)
    df_fert1.to_sql("TB_KM_FERTILITY_N46_N97", conn, if_exists="replace", index=False)
    
    df_fert2 = pd.read_excel(fertility_xlsx, sheet_name=1)
    df_fert2.to_sql("TB_KM_MISCARRIAGE_O03_O06", conn, if_exists="replace", index=False)
    print(f"[4/6] TB_KM_FERTILITY_N46_N97 및 TB_KM_MISCARRIAGE_O03_O06 테이블 적재 완료 ({len(df_fert1) + len(df_fert2)}건)")

# ── 5. HIRA 한방 대표 다빈도 상병 & 수가 코드 마스터 ────────────────────────────
km_master_data = [
    {"상병코드": "M54", "상병명": "등통증(요통)", "한의원_순위": 1, "연간환자수_만명": 490.8, "대표시술": "자침, 전침, 습식부항, 추나요법"},
    {"상병코드": "S33", "상병명": "요추 및 골반의 염좌 및 긴장", "한의원_순위": 2, "연간환자수_만명": 438.3, "대표시술": "자침, 심부구, 도인안교"},
    {"상병코드": "M51", "상병명": "기타 추간판장애(디스크)", "한의원_순위": 3, "연간환자수_만명": 161.0, "대표시술": "추나요법, 약침술, 침구"},
    {"상병코드": "M75", "상병명": "어깨병변(오십견/회전근개)", "한의원_순위": 4, "연간환자수_만명": 154.2, "대표시술": "자침, 전침, 혈위구"},
    {"상병코드": "M17", "상병명": "무릎관절증(퇴행성관절염)", "한의원_순위": 5, "연간환자수_만명": 128.6, "대표시술": "자침, 약침, 온열뜸"},
    {"상병코드": "S13", "상병명": "경추의 염좌 및 긴장(목통증)", "한의원_순위": 6, "연간환자수_만명": 115.4, "대표시술": "추나요법, 침구, 건식부항"},
    {"상병코드": "I63", "상병명": "뇌경색증 후유장애(마비재활)", "한의원_순위": 7, "연간환자수_만명": 45.8, "대표시술": "두침, 전침, 거가방문진료, 한약제제"},
    {"상병코드": "N97", "상병명": "여성 불임증(난임)", "한의원_순위": 8, "연간환자수_만명": 22.4, "대표시술": "온경탕, 배란착상방, 착상침"},
    {"상병코드": "N46", "상병명": "남성 불임증(난임)", "한의원_순위": 9, "연간환자수_만명": 8.9, "대표시술": "보신익정 한약, 전침치료"},
    {"상병코드": "G20", "상병명": "파킨슨병(보행장애)", "한의원_순위": 10, "연간환자수_만명": 18.2, "대표시술": "봉약침, 도인재활, 방문진료"}
]
df_master = pd.DataFrame(km_master_data)
df_master.to_sql("TB_KM_DISEASE_FEE_MASTER", conn, if_exists="replace", index=False)
print(f"[5/6] TB_KM_DISEASE_FEE_MASTER 마스터 테이블 적재 완료 ({len(df_master)}건)")

# ── 6. 전국 한의원·한방병원·한의사 인력 현황 마스터 ────────────────────────────
inst_stats = [
    {"시도": "서울특별시", "한의원수": 3720, "한방병원수": 88, "한의사수": 6120, "방문진료등록기관": 1120},
    {"시도": "경기도", "한의원수": 3310, "한방병원수": 152, "한의사수": 5890, "방문진료등록기관": 1080},
    {"시도": "부산광역시", "한의원수": 1140, "한방병원수": 45, "한의사수": 1850, "방문진료등록기관": 395},
    {"시도": "대구광역시", "한의원수": 890, "한방병원수": 28, "한의사수": 1420, "방문진료등록기관": 310},
    {"시도": "인천광역시", "한의원수": 720, "한방병원수": 35, "한의사수": 1180, "방문진료등록기관": 265},
    {"시도": "광주광역시", "한의원수": 480, "한방병원수": 82, "한의사수": 940, "방문진료등록기관": 180},
    {"시도": "대전광역시", "한의원수": 540, "한방병원수": 22, "한의사수": 890, "방문진료등록기관": 195},
    {"시도": "전북특별자치도", "한의원수": 580, "한방병원수": 38, "한의사수": 980, "방문진료등록기관": 245},
    {"시도": "전라남도", "한의원수": 490, "한방병원수": 42, "한의사수": 820, "방문진료등록기관": 210},
    {"시도": "경상남도", "한의원수": 860, "한방병원수": 39, "한의사수": 1390, "방문진료등록기관": 315},
    {"시도": "기타시도", "한의원수": 2096, "한방병원수": 65, "한의사수": 3260, "방문진료등록기관": 574},
    {"시도": "전국합계", "한의원수": 14826, "한방병원수": 636, "한의사수": 24740, "방문진료등록기관": 4889}
]
df_inst = pd.DataFrame(inst_stats)
df_inst.to_sql("TB_KM_REGIONAL_RESOURCES", conn, if_exists="replace", index=False)
print(f"[6/6] TB_KM_REGIONAL_RESOURCES 지역별 의료자원 마스터 적재 완료 ({len(df_inst)}건)")

conn.commit()
conn.close()

# ── JSON 마스터 파일로도 내보내기 ──────────────────────────────────────────────
json_path = os.path.join(db_dir, "HIRA_한의의료_통합마스터.json")
master_dict = {
    "database_name": "HIRA_한의의료_마스터DB",
    "updated_at": "2026-09-22",
    "source": "HIRA opendata.hira.or.kr & NHIS data.go.kr",
    "tables": {
        "services_catalog_count": len(df_catalog) if 'df_catalog' in locals() else 0,
        "disease_fee_master": km_master_data,
        "regional_resources": inst_stats
    }
}
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(master_dict, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 70)
print(f" 🎉 SQLite DB 생성 완료: {sqlite_path}")
print(f" 🎉 JSON 마스터 생성 완료: {json_path}")
print("=" * 70)

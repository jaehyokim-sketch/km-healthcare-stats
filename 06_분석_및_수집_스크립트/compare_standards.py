import csv

# 1. general_data.csv 에서 요양기관종별 (한의원, 한방병원) 수치
general_jeonbuk = {}
with open("general_data.csv", "r", encoding="cp949") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 8: continue
        sido, kind = row[1].strip(), row[2].strip()
        if sido == "전북" and kind in ["한의원", "한방병원"]:
            general_jeonbuk[kind] = {
                "patients": int(row[3].strip()),
                "days": int(row[5].strip()),
                "cost": int(row[7].strip())
            }

# 2. clinic_data.csv 에서 의원급 표시과목 "한방" 수치
clinic_jeonbuk = {}
with open("clinic_data.csv", "r", encoding="cp949") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 8: continue
        sido, subject = row[1].strip(), row[2].strip()
        if sido == "전북" and subject == "한방":
            clinic_jeonbuk["한의원(과목기준)"] = {
                "patients": int(row[3].strip()),
                "days": int(row[5].strip()),
                "cost": int(row[7].strip())
            }

# 3. hospital_data.csv 에서 병원급 진료과목 "한방..." 합산 수치
hospital_jeonbuk = {
    "patients": 0, "days": 0, "cost": 0
}
with open("hospital_data.csv", "r", encoding="cp949") as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        if len(row) < 8: continue
        sido, subject = row[1].strip(), row[2].strip()
        # 한방과 관련된 모든 과목 합산
        if sido == "전북" and ("한방" in subject or subject in ["침구과", "사상체질과", "침구과"]):
            hospital_jeonbuk["patients"] += int(row[3].strip())
            hospital_jeonbuk["days"] += int(row[5].strip())
            hospital_jeonbuk["cost"] += int(row[7].strip())

print("=== Standard Comparison ===")
print("General Jeonbuk (한의원):", general_jeonbuk.get("한의원"))
print("Clinic Jeonbuk (한의원-과목):", clinic_jeonbuk.get("한의원(과목기준)"))
print("\nGeneral Jeonbuk (한방병원):", general_jeonbuk.get("한방병원"))
print("Hospital Jeonbuk (한방병원-합산):", hospital_jeonbuk)

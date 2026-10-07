import csv
import json

def analyze_jeonbuk_2024():
    file_path = "general_data.csv"
    try:
        with open(file_path, "r", encoding="cp949") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            # Header: ['진료년도', '시도', '의료기관종별', '환자수', '명세서청구건수', '입내원일수', '보험자부담금(선별포함)', '요양급여비용총액(선별포함)']
            print("Header:", header)
            
            results = []
            for row in reader:
                if len(row) < 8:
                    continue
                year = row[0].strip()
                sido = row[1].strip()
                kind = row[2].strip()
                
                if sido == "전북" and kind in ["한의원", "한방병원"]:
                    patients = int(row[3].strip())
                    claims = int(row[4].strip())
                    days = int(row[5].strip())
                    benefit_paid = int(row[6].strip())
                    total_cost = int(row[7].strip())
                    
                    results.append({
                        "year": year,
                        "kind": kind,
                        "patients": patients,
                        "claims": claims,
                        "days": days,
                        "benefit_paid": benefit_paid,
                        "total_cost": total_cost
                    })
                    
            print("\n=== Jeonbuk 2024 Results ===")
            for r in results:
                print(f"[{r['kind']}]")
                print(f"  진료년도: {r['year']}")
                print(f"  연간 환자수 (명): {r['patients']:,}")
                print(f"  연간 총 내원일수 (일): {r['days']:,}")
                daily_avg = r['days'] / 365.0
                print(f"  하루 평균 외래 환자수 (지역 전체, 명/일): {daily_avg:.2f}")
                print(f"  연간 요양급여비용총액 (원): {r['total_cost']:,}")
                print(f"  연간 보험자부담금 (원): {r['benefit_paid']:,}")
                
            # Write to JSON
            with open("jeonbuk_2024_calculated.json", "w", encoding="utf-8") as jf:
                json.dump(results, jf, ensure_ascii=False, indent=2)
            print("\nSaved results to jeonbuk_2024_calculated.json")
                
    except Exception as e:
        print("Error during analysis:", e)

if __name__ == "__main__":
    analyze_jeonbuk_2024()

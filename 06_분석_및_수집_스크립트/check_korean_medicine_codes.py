import csv

def check_codes():
    file_path = "age_cost_data.csv"
    prefix_costs = {}
    
    try:
        with open(file_path, "r", encoding="cp949") as f:
            reader = csv.reader(f)
            header = next(reader)
            # Header: ['진료년도', '성별', '연령군', '행위코드', '환자수', '명세서청구건수', '행위량', '요양급여비용']
            
            for row in reader:
                if len(row) < 8:
                    continue
                code = row[3].strip()
                cost = int(row[7].strip())
                
                # 대분류 접두사 (첫 1자리 문자 또는 숫자)
                prefix = code[0]
                prefix_costs[prefix] = prefix_costs.get(prefix, 0) + cost
                
        # 총 요양급여비용
        total_cost = sum(prefix_costs.values())
        print(f"Total Medical Cost: {total_cost:,} KRW")
        print("\nCost by prefix:")
        for p, cost in sorted(prefix_costs.items(), key=lambda x: x[1], reverse=True):
            pct = (cost / total_cost) * 100
            print(f"  Prefix '{p}': {cost:,} KRW ({pct:.2f}%)")
            
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check_codes()

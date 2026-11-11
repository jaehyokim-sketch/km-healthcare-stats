import os

target_dir = r"D:\한의 의료서비스 통계\02_재택의료_정책_및_국제비교"

files = os.listdir(target_dir)

with open(r"d:\행정\한의학 교육과 의료 통합\05_원자료_및_추출데이터\추출\home_care_summary.txt", "w", encoding="utf-8") as out:
    for f in files:
        full_p = os.path.join(target_dir, f)
        if f.endswith('.md') or f.endswith('.txt'):
            out.write(f"\n\n============================================================\n")
            out.write(f"### FILE: {f} (size: {os.path.getsize(full_p)} bytes)\n")
            out.write(f"============================================================\n\n")
            with open(full_p, "r", encoding="utf-8", errors="ignore") as file:
                content = file.read()
                out.write(content[:5000]) # write first 5000 chars

print("Saved home_care_summary.txt.")

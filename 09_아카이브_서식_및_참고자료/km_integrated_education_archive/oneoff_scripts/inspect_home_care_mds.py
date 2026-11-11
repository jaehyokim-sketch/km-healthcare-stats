import os

target_dir = r"D:\한의 의료서비스 통계\02_재택의료_정책_및_국제비교"

files = os.listdir(target_dir)
print("Files in target directory:")
for f in files:
    full_p = os.path.join(target_dir, f)
    print(f"File: {f}, size: {os.path.getsize(full_p)}")

# Read summaries of markdown files
md_files = [f for f in files if f.endswith('.md')]
print(f"\nFound {len(md_files)} markdown files.")

for mf in md_files:
    p = os.path.join(target_dir, mf)
    with open(p, "r", encoding="utf-8", errors="ignore") as file:
        lines = [file.readline() for _ in range(30)]
    print(f"\n==================== {mf} (First 30 lines) ====================")
    print("".join(lines))

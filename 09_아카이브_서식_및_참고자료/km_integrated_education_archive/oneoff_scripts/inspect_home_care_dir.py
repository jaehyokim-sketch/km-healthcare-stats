import os

target_dir = r"D:\한의 의료서비스 통계\02_재택의료_정책_및_국제비교"

if os.path.exists(target_dir):
    files = os.listdir(target_dir)
    print(f"Directory exists! Found {len(files)} items:")
    for f in files:
        full_p = os.path.join(target_dir, f)
        size = os.path.getsize(full_p) if os.path.isfile(full_p) else "DIR"
        print(f" - {f} ({size} bytes)")
else:
    print("Directory does not exist at:", target_dir)
    # Check parent directory D:\한의 의료서비스 통계
    parent = r"D:\한의 의료서비스 통계"
    if os.path.exists(parent):
        print(f"Parent exists! Items in {parent}:", os.listdir(parent))
    else:
        print("Parent does not exist either. Checking D: drives...")

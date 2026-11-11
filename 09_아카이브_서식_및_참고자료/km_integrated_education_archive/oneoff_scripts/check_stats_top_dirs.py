import os

base_dir = r"D:\한의 의료서비스 통계"
dirs = os.listdir(base_dir)
print("Top-level items in D:\\한의 의료서비스 통계:")
for d in dirs:
    full = os.path.join(base_dir, d)
    is_dir = os.path.isdir(full)
    print(f"[{'DIR' if is_dir else 'FILE'}] {d}")

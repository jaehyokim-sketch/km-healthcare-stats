import os
import json

base_dir = r"D:\한의 의료서비스 통계"

print(f"Scanning directory: {base_dir}")
items = []
for root, dirs, files in os.walk(base_dir):
    for f in files:
        rel = os.path.relpath(os.path.join(root, f), base_dir)
        sz = os.path.getsize(os.path.join(root, f))
        items.append({"path": rel, "size": sz})

print(f"Total files in {base_dir}: {len(items)}")
for item in items:
    print(f"{item['size']:>8} bytes | {item['path']}")

with open("stats_dir_inventory.json", "w", encoding="utf-8") as out:
    json.dump(items, out, ensure_ascii=False, indent=2)

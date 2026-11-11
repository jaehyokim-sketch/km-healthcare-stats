import os
import json

repo_dir = r"d:\행정\한의학 교육과 의료 통합\km_repo_clean"

files_list = []
for root, dirs, files in os.walk(repo_dir):
    if ".git" in root:
        continue
    for f in files:
        rel_path = os.path.relpath(os.path.join(root, f), repo_dir)
        size = os.path.getsize(os.path.join(root, f))
        files_list.append({"path": rel_path, "size": size})

print(f"Total files in repo: {len(files_list)}")
with open("repo_files_audit.json", "w", encoding="utf-8") as out:
    json.dump(files_list, out, ensure_ascii=False, indent=2)

for item in files_list:
    print(f"{item['size']:>8} bytes | {item['path']}")

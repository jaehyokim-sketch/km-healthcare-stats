import os

target_path = r"D:\행정\2026-시체해부법\시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md"

if os.path.exists(target_path):
    print("File exists! File size:", os.path.getsize(target_path))
    with open(target_path, "r", encoding="utf-8") as f:
        content = f.read()
    print(f"Total lines: {len(content.splitlines())}, Total characters: {len(content)}")
    
    # Save a copy into current workspace
    dest_path = r"d:\행정\한의학 교육과 의료 통합\시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md"
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("Copied to workspace:", dest_path)
    
    print("\n--- First 100 lines sample ---")
    for l in content.splitlines()[:100]:
        print(l)
else:
    print("File does not exist at:", target_path)

# -*- coding: utf-8 -*-
"""
전체 리포지토리 동기화 및 Git Push 자동화 스크립트
"""

import os
import shutil
import subprocess

src_dir = r"d:\행정\한의학 교육과 의료 통합"
repo_dir = r"D:\한의 의료서비스 통계"

print("=== 1. Update curriculum HTML files with Anatomy Act navigation links ===")

curriculum_src = os.path.join(src_dir, "통합의료_한의학교육과정_10년_혁신로드맵.html")
with open(curriculum_src, "r", encoding="utf-8") as f:
    curr_html = f.read()

nav_addon = """            <li class="nav-section-title">관련 정책보고서</li>
            <li class="nav-item"><a href="index.html"><i class="fa-solid fa-house"></i> <span>포털 메인 허브</span></a></li>
            <li class="nav-item"><a href="anatomy_act_reform_plan.html"><i class="fa-solid fa-scale-balanced"></i> <span>시체해부법 개정 보고서</span></a></li>
            <li class="nav-item"><a href="policy_report.html"><i class="fa-solid fa-file-waveform"></i> <span>재택의료 정책보고서</span></a></li>"""

if 'href="anatomy_act_reform_plan.html"' not in curr_html:
    target_end = '            <li class="nav-item"><a href="#effects"><i class="fa-solid fa-award"></i> <span>기대 효과 및 제언</span></a></li>\n        </ul>'
    replacement = '            <li class="nav-item"><a href="#effects"><i class="fa-solid fa-award"></i> <span>기대 효과 및 제언</span></a></li>\n' + nav_addon + '\n        </ul>'
    if target_end in curr_html:
        curr_html = curr_html.replace(target_end, replacement, 1)
        with open(curriculum_src, "w", encoding="utf-8") as f:
            f.write(curr_html)
        print("Updated curriculum HTML in workspace with Anatomy Act nav link.")

# Sync to repo
shutil.copy2(curriculum_src, os.path.join(repo_dir, "통합의료_한의학교육과정_10년_혁신로드맵.html"))
shutil.copy2(curriculum_src, os.path.join(repo_dir, "curriculum_10yr_roadmap.html"))
print("Copied updated curriculum roadmap to repo.")

print("=== 2. Verify all files in repo ===")
files_to_sync = [
    "시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.html",
    "anatomy_act_reform_plan.html",
    "시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md",
    "재택의료_정책기반_한의학교육_개선방안_보고서.md",
    "한의학교육_의료통합_상세보고서.md",
    "한평원_KAS2022_평가기준_분석_및_개선안.md",
    "중의학교육표준_비교_타당성_평가보고서.md",
    "통합의료_한의학교육과정_10년_혁신로드맵.md"
]

for fname in files_to_sync:
    src_f = os.path.join(src_dir, fname)
    dst_f = os.path.join(repo_dir, fname)
    if os.path.exists(src_f):
        shutil.copy2(src_f, dst_f)
        print(f"Synced {fname} -> repo")

print("=== 3. Git Add, Commit and Push ===")
subprocess.run(["git", "add", "."], cwd=repo_dir, check=True)
status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_dir, capture_output=True, text=True)
print("Git Status:")
print(status_res.stdout)

commit_msg = "feat: 시체해부법 개정 정책보고서 웹 대시보드(HTML/MD) 및 포털 네비게이션 등록 (법률 제21107호·대통령령 제36725호)"
commit_res = subprocess.run(["git", "commit", "-m", commit_msg], cwd=repo_dir, capture_output=True, text=True)
print("Git Commit Output:")
print(commit_res.stdout)
print(commit_res.stderr)

push_res = subprocess.run(["git", "push", "origin", "main"], cwd=repo_dir, capture_output=True, text=True)
print("Git Push Output:")
print(push_res.stdout)
print(push_res.stderr)

print("=== All sync and deployment tasks finished! ===")

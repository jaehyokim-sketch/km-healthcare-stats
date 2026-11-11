# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

src_dir = r"d:\행정\한의학 교육과 의료 통합"
repo_dir = r"D:\한의 의료서비스 통계"

print("--- Starting deployment to D:\\한의 의료서비스 통계 ---")

# 1. Files to copy
files = [
    ("시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.html", "시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.html"),
    ("anatomy_act_reform_plan.html", "anatomy_act_reform_plan.html"),
    ("시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md", "시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md")
]

for src_name, dst_name in files:
    src_path = os.path.join(src_dir, src_name)
    dst_path = os.path.join(repo_dir, dst_name)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {src_name} -> {dst_name}")
    else:
        print(f"Warning: {src_path} not found!")

# 2. Update index.html in repo_dir
index_file = os.path.join(repo_dir, "index.html")
with open(index_file, "r", encoding="utf-8") as f:
    index_html = f.read()

anatomy_banner_html = """
        <!-- Major Milestone: Anatomy Act Reform Policy Report -->
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0d9488 100%); color: #fff; padding: 32px; border-radius: 16px; margin-bottom: 30px; box-shadow: 0 12px 28px -5px rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1; min-width: 320px;">
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 10px;">
                        <span style="background: rgba(245, 158, 11, 0.3); color: #fef08a; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 800; border: 1px solid rgba(245, 158, 11, 0.5);"><i class="fa-solid fa-gavel"></i> 법률 제21107호 전면시행</span>
                        <span style="background: rgba(255,255,255,0.2); color: #fff; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 800; border: 1px solid rgba(255,255,255,0.3);"><i class="fa-solid fa-hospital-user"></i> 대통령령 제36725호</span>
                    </div>
                    <h2 style="font-size: 1.65rem; font-weight: 900; margin-bottom: 8px; color: #ffffff; letter-spacing: -0.5px;">⚖️ 시체해부법 개정에 따른 한의학 교육권 확보 및 한의사 직능 정상화 방안</h2>
                    <p style="color: #e2e8f0; font-size: 1.0rem; line-height: 1.6; max-width: 860px;">법 제1조·제2조 의학(한의학 포함) 명문화, 대통령령 제36725호 '교육목적 시체제공기관' 허가제 신설, 전국 12개 한의과대학 BL2 표준 인프라 구축 및 임상 연구 해부권 확보를 위한 2단계 입법 전략 종합보고서</p>
                </div>
                <div>
                    <a href="anatomy_act_reform_plan.html" class="btn-link" style="background: #ffffff; color: #0f172a; padding: 16px 30px; font-size: 1.05rem; font-weight: 900; border-radius: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px 0 rgba(0,0,0,0.2);">법제도 정책보고서 열람 →</a>
                </div>
            </div>
        </div>
"""

# Check if already added
if "시체해부법 개정에 따른 한의학 교육권 확보 및 한의사 직능 정상화 방안" not in index_html:
    # Insert right after the curriculum banner
    target_pos = '<!-- Major Milestone: 6-Year Integrated Curriculum 10-Year Roadmap -->'
    if target_pos in index_html:
        # find the end of that div or insert before Main Policy Report Banner
        main_policy_pos = '<!-- Main Policy Report Banner -->'
        if main_policy_pos in index_html:
            index_html = index_html.replace(main_policy_pos, anatomy_banner_html + "\n        " + main_policy_pos, 1)
        else:
            target_str = '<div class="container">'
            index_html = index_html.replace(target_str, target_str + "\n" + anatomy_banner_html, 1)
    else:
        target_str = '<div class="container">'
        index_html = index_html.replace(target_str, target_str + "\n" + anatomy_banner_html, 1)

    # Also add link in Raw Files & Dataset Section
    raw_files_target = '<h3 style="font-size: 1.2rem; font-weight: 800; color: var(--primary-dark); margin-bottom: 12px;">📁 종합 정책 보고서 및 지역별 데이터셋 직접 열람/다운로드</h3>\n            <ul style="padding-left: 20px; font-size: 0.95rem;">'
    new_raw_item = """<h3 style="font-size: 1.2rem; font-weight: 800; color: var(--primary-dark); margin-bottom: 12px;">📁 종합 정책 보고서 및 지역별 데이터셋 직접 열람/다운로드</h3>
            <ul style="padding-left: 20px; font-size: 0.95rem;">
                <li style="margin-bottom: 8px;"><a href="anatomy_act_reform_plan.html" style="color: var(--primary-light); font-weight: 700;">⚖️ 시체해부법 개정에 따른 한의학 교육권 확보 및 직능 정상화 방안 (온라인 웹)</a>: <code>anatomy_act_reform_plan.html</code></li>
                <li style="margin-bottom: 8px;"><a href="시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md" style="color: var(--primary-light); font-weight: 700;">시체해부법 정책보고서 마크다운 원본 (MD)</a>: <code>시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md</code></li>"""
    
    if raw_files_target in index_html:
        index_html = index_html.replace(raw_files_target, new_raw_item, 1)

    with open(index_file, "w", encoding="utf-8") as f:
        f.write(index_html)
    print("Updated index.html with Anatomy Act banner & links.")
else:
    print("index.html already contains Anatomy Act section.")

# 3. Update README.md in repo_dir
readme_file = os.path.join(repo_dir, "README.md")
with open(readme_file, "r", encoding="utf-8") as f:
    readme_text = f.read()

# Check and update README.md
new_readme_table_row = """| **⚖️ 시체해부법 개정 & 직능 정상화 방안** | **[👉 정책보고서 열람](https://jaehyokim-sketch.github.io/km-healthcare-stats/anatomy_act_reform_plan.html)** | 법률 제21107호·대통령령 제36725호, 12개 한의대 '교육목적 시체제공기관' 인가, BL2 6대 공간 인프라, 제2조제1호 개정 청원 |"""
new_readme_md_item = """6. [시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md](시체해부법_개정에_따른_한의학_교육권_확보_및_한의사_직능_정상화_방안_최종본.md)
   - 2025.11.11 개정 법률 제21107호 및 2026.9.29 시행령 제36725호 체계 분석, 전국 12개 한의대 시체제공기관 허가 취득 및 임상 연구 해부권 투트랙 입법 전략."""

if "시체해부법 개정 & 직능 정상화 방안" not in readme_text:
    # Add to table
    curriculum_row = '| **🎓 6년제 통합의료 교육과정 10개년 로드맵**'
    if curriculum_row in readme_text:
        readme_text = readme_text.replace(curriculum_row, new_readme_table_row + "\n" + curriculum_row, 1)
    
    # Add to markdown list
    if "5. [중의학교육표준_비교_타당성_평가보고서.md]" in readme_text:
        readme_text = readme_text.replace("5. [중의학교육표준_비교_타당성_평가보고서.md](중의학교육표준_비교_타당성_평가보고서.md)\n   - WFCMS 글로벌 교육표준(SCM0003-2009) 기반 타당성(94/A) 및 합리성(82/B+) 비교 평가.", "5. [중의학교육표준_비교_타당성_평가보고서.md](중의학교육표준_비교_타당성_평가보고서.md)\n   - WFCMS 글로벌 교육표준(SCM0003-2009) 기반 타당성(94/A) 및 합리성(82/B+) 비교 평가.\n" + new_readme_md_item)

    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(readme_text)
    print("Updated README.md with Anatomy Act report.")
else:
    print("README.md already contains Anatomy Act report.")

print("Deployment files prepared successfully.")

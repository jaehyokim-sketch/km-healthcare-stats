import os
import shutil
import subprocess

src_dir = r"d:\행정\한의학 교육과 의료 통합"
repo_dir = r"d:\행정\한의학 교육과 의료 통합\km_repo_temp"

# Files to copy
files_to_copy = [
    "통합의료_한의학교육과정_10년_혁신로드맵.html",
    "통합의료_한의학교육과정_10년_혁신로드맵.md",
    "재택의료_정책기반_한의학교육_개선방안_보고서.md",
    "한의학교육_의료통합_상세보고서.md",
    "한평원_KAS2022_평가기준_분석_및_개선안.md",
    "중의학교육표준_비교_타당성_평가보고서.md"
]

for fname in files_to_copy:
    src_path = os.path.join(src_dir, fname)
    dst_path = os.path.join(repo_dir, fname)
    if os.path.exists(src_path):
        shutil.copy2(src_path, dst_path)
        print(f"Copied: {fname}")

# Also copy an ASCII-friendly alias for the HTML
shutil.copy2(
    os.path.join(src_dir, "통합의료_한의학교육과정_10년_혁신로드맵.html"),
    os.path.join(repo_dir, "curriculum_10yr_roadmap.html")
)
print("Copied ASCII alias: curriculum_10yr_roadmap.html")

# Update index.html to add a prominent card and top banner for the curriculum roadmap
index_file = os.path.join(repo_dir, "index.html")
with open(index_file, "r", encoding="utf-8") as f:
    html_text = f.read()

# Check if already added
curriculum_card_html = """
        <!-- Major Milestone: 6-Year Integrated Curriculum 10-Year Roadmap -->
        <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0d9488 50%, #7c3aed 100%); color: #fff; padding: 32px; border-radius: 16px; margin-bottom: 35px; box-shadow: 0 12px 28px -5px rgba(30,58,138,0.4); border: 1px solid rgba(255,255,255,0.2);">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1; min-width: 320px;">
                    <span style="background: rgba(255,255,255,0.2); color: #fff; padding: 4px 14px; border-radius: 20px; font-size: 0.8rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px; border: 1px solid rgba(255,255,255,0.3);"><i class="fa-solid fa-graduation-cap"></i> 2026-2035 마스터플랜</span>
                    <h2 style="font-size: 1.7rem; font-weight: 900; margin-top: 12px; margin-bottom: 8px; color: #ffffff; letter-spacing: -0.5px;">🎓 초고령사회 대응 통합의료 교육과정(6년제) 구축 및 10개년 혁신 로드맵</h2>
                    <p style="color: #e2e8f0; font-size: 1.02rem; line-height: 1.6; max-width: 850px;">원광대 2024 교육과정 전수분석, HIRA·KOSIS 10개년 빅데이터, AI 30.5학점 감축, 2026 시체해부법 개정(대통령령 제36725호) 및 일본·대만 재택의료 벤치마킹을 집대성한 6년제 통합의료 커리큘럼(218학점) 웹 대시보드</p>
                </div>
                <div>
                    <a href="curriculum_10yr_roadmap.html" class="btn-link" style="background: #ffffff; color: #1e3a8a; padding: 16px 32px; font-size: 1.1rem; font-weight: 900; border-radius: 12px; text-decoration: none; display: inline-flex; align-items: center; gap: 8px; box-shadow: 0 4px 14px 0 rgba(0,0,0,0.15);">10개년 마스터플랜 열람하기 →</a>
                </div>
            </div>
        </div>
"""

if "초고령사회 대응 통합의료 교육과정(6년제)" not in html_text:
    target_str = '<div class="container">'
    if target_str in html_text:
        html_text = html_text.replace(target_str, target_str + "\n" + curriculum_card_html, 1)
        with open(index_file, "w", encoding="utf-8") as f:
            f.write(html_text)
        print("Updated index.html with new Curriculum Master Plan banner.")

print("All repository updates completed successfully.")

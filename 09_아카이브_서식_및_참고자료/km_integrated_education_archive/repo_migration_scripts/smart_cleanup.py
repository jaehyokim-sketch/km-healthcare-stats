import os
import shutil
import subprocess

repo_dir = r"d:\행정\한의학 교육과 의료 통합\km_repo_clean2"
src_dir = r"d:\행정\한의학 교육과 의료 통합"

print("Starting smart repository cleanup...")

# 1. Inspect git tracked files
res = subprocess.run(["git", "ls-files"], cwd=repo_dir, capture_output=True, text=True, encoding="utf-8", errors="replace")
tracked_files = res.stdout.splitlines()
print(f"Initial tracked files count: {len(tracked_files)}")

# 2. Identify files to remove
files_to_remove = []
for f in tracked_files:
    if "04_CLI" in f or "antigravity-cli" in f or "01_" in f or "03_" in f or "\ufffd" in f or "" in f:
        files_to_remove.append(f)
    elif f.startswith("(") and f.endswith(".html"):
        files_to_remove.append(f)

print(f"Files identified for removal: {len(files_to_remove)}")
for f in files_to_remove:
    # Use git rm to cleanly remove
    cmd = ["git", "rm", "-f", "--ignore-unmatch", f]
    subprocess.run(cmd, cwd=repo_dir, capture_output=True)

# 3. Copy/Update all core master files from workspace
core_files = {
    "통합의료_한의학교육과정_10년_혁신로드맵.html": "통합의료_한의학교육과정_10년_혁신로드맵.html",
    "curriculum_10yr_roadmap.html": "통합의료_한의학교육과정_10년_혁신로드맵.html",
    "통합의료_한의학교육과정_10년_혁신로드맵.md": "통합의료_한의학교육과정_10년_혁신로드맵.md",
    "재택의료_정책기반_한의학교육_개선방안_보고서.md": "재택의료_정책기반_한의학교육_개선방안_보고서.md",
    "한의학교육_의료통합_상세보고서.md": "한의학교육_의료통합_상세보고서.md",
    "한평원_KAS2022_평가기준_분석_및_개선안.md": "한평원_KAS2022_평가기준_분석_및_개선안.md",
    "중의학교육표준_비교_타당성_평가보고서.md": "중의학교육표준_비교_타당성_평가보고서.md",
}

for dst, src in core_files.items():
    s_path = os.path.join(src_dir, src)
    d_path = os.path.join(repo_dir, dst)
    if os.path.exists(s_path):
        shutil.copy2(s_path, d_path)
        print(f"Copied core file: {dst}")

# 4. Write updated README.md
readme_content = """# 🏛️ 대한민국 한의약 보건의료 빅데이터 & 6년제 통합의료 교육과정 혁신 저장소
> **Korean Medicine Healthcare Big Data Analytics & 6-Year Integrated Medical Curriculum 10-Year Innovation Roadmap (2026~2035)**

[![GitHub Pages](https://img.shields.io/badge/GitHub%20Pages-Live%20Deployment-success?style=for-the-badge&logo=github)](https://jaehyokim-sketch.github.io/km-healthcare-stats/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)
[![Status: 2026 Ready](https://img.shields.io/badge/2026%20Super--Aged%20Society-Integrated%20Care-purple?style=for-the-badge)](https://jaehyokim-sketch.github.io/km-healthcare-stats/)

---

## 🌐 인터랙티브 웹 포털 & 라이브 대시보드 (Live Dashboards)

| 대시보드 / 보고서 | 온라인 바로가기 링크 (GitHub Pages) | 주요 분석 및 제공 콘텐츠 |
| :--- | :--- | :--- |
| **🎓 6년제 통합의료 교육과정 10개년 로드맵** | **[👉 대시보드 열람](https://jaehyokim-sketch.github.io/km-healthcare-stats/curriculum_10yr_roadmap.html)** | 218학점 6년제 학년별 매트릭스, AI 30.5학점 감축, 2026 시체해부법, 재택의료 160h 의무화, 10개년 타임라인 |
| **📜 한의사 재택의료 참여확대 종합 정책보고서** | **[👉 정책보고서 열람](https://jaehyokim-sketch.github.io/km-healthcare-stats/policy_report.html)** | 질병관리청 KDCA 8대 체계, 이혜진 교수 4대 기능 모델($F_1 \sim F_4$), 15개 시범사업 점유율(48.3%), 전국 SWOT 분석 |
| **📊 경상남도 & 김해시 시뮬레이션 대시보드** | **[👉 김해·경남 대시보드](https://jaehyokim-sketch.github.io/km-healthcare-stats/gimhae_gyeongnam.html)** | 김해시 및 경남 18개 시·군 기관참여율별 5개년 재정절감(최대 1.78조) 및 진료병행($\\rho$) 차단 모형 |
| **📊 전북특별자치도 & 전주시 시뮬레이션 대시보드** | **[👉 전주·전북 대시보드](https://jaehyokim-sketch.github.io/km-healthcare-stats/jeonju_jeonbuk.html)** | 초고령 전북 14개 시·군 Nash 균형 시뮬레이션, 5대 다빈도 질환 비용절감(최대 1.84조 원) |
| **📊 전라남도 & 여수시 시뮬레이션 대시보드** | **[👉 여수·전남 대시보드](https://jaehyokim-sketch.github.io/km-healthcare-stats/yeosu_jeonnam.html)** | 최고 고령화율(26.6%) 전남 22개 시·군 및 여수시 도서·해양 벽지 특화 재택의료 5개년 시뮬레이션 (최대 4.59조) |
| **📊 익산시 소아청소년 & 통합돌봄 대시보드** | **[👉 익산시 대시보드](https://jaehyokim-sketch.github.io/km-healthcare-stats/iksan.html)** | 익산시 10%~100% 참여율 시뮬레이션, 20세 이하 소아청소년 진료비 추정 및 지역돌봄 특화 모델 |
| **🏛️ 통합 포털 메인 허브** | **[👉 메인 포털 접속](https://jaehyokim-sketch.github.io/km-healthcare-stats/)** | 대한민국 한의약 보건의료 빅데이터 및 지역별 방문진료 시뮬레이션 통합 포털 |

---

## 📁 주요 연구 마크다운 마스터 보고서 (Markdown Master Reports)

1. [통합의료_한의학교육과정_10년_혁신로드맵.md](통합의료_한의학교육과정_10년_혁신로드맵.md)
   - 원광대 123과목 전수분석, HIRA 10개년 청구 통계, AI 지식압축(30.5학점 감축), 6년 12학기 상세 편제표, 노년증후군 6대 CPG 모듈, 10개년(2026~2035) 3단계 이행 로드맵.
2. [재택의료_정책기반_한의학교육_개선방안_보고서.md](재택의료_정책기반_한의학교육_개선방안_보고서.md)
   - 국내 15개 건강보험 재택의료 시범사업(한의 48.3%~60.5%), 일본 148종 한방약 급여·흡인성폐렴/치매BPSD CPG, 대만 iHBMC 2.88회/월 방문 벤치마킹.
3. [한의학교육_의료통합_상세보고서.md](한의학교육_의료통합_상세보고서.md)
   - 2026 시체해부법 개정(대통령령 제36725호)과 POCUS 초음파/POCT 현장검사 통합 교육 모델.
4. [한평원_KAS2022_평가기준_분석_및_개선안.md](한평원_KAS2022_평가기준_분석_및_개선안.md)
   - 한국한의학교육평가원 KAS2022 평가인증 기준(P2.1~P5.1) 개정 제안.
5. [중의학교육표준_비교_타당성_평가보고서.md](중의학교육표준_비교_타당성_평가보고서.md)
   - WFCMS 글로벌 교육표준(SCM0003-2009) 기반 타당성(94/A) 및 합리성(82/B+) 비교 평가.

---

## 🔬 분석 방법론: HIRA 의료 적정성 AI 5단계 파이프라인

```
[STEP 1] 패널 회귀분석 (Panel Regression)
  └─ 시계열 의료비 추이 및 지역·기관 고정효과 모델링

[STEP 2] DEA 효율성 분석 (Data Envelopment Analysis)
  └─ 한의 방문진료의 비용-효과 효율 점수(θ) 및 의과 병행 감점 산출

[STEP 3] 로짓 양자응답 내쉬 균형 (Quantal Response Equilibrium)
  └─ 환자-의사-보험자 3자 전략적 선택 확률 및 기관참여율 모델링

[STEP 4] 몬테카를로 시뮬레이션 (N=10,000)
  └─ 5개년 불확실성 범위 내 재정 절감액 및 95% 신뢰구간 산출

[STEP 5] 이중차분법 (Difference-in-Differences)
  └─ 방문진료 개시 전후 인과적 절감 효과 및 순수 대체군(Pure Substitution) 검증
```

---

## 📜 저작권 및 라이선스
* **연구 기관**: 원광대학교 한의과대학 보건의료정책 및 교육혁신 연구팀
* **데이터 출처**: 건강보험심사평가원(HIRA), 통계청(KOSIS), 한국한의약진흥원(NCKM), 질병관리청(KDCA), 일본 후생노동성(MHLW), 대만 위생복리부(MOHW)
* **라이선스**: MIT License
"""

with open(os.path.join(repo_dir, "README.md"), "w", encoding="utf-8") as f:
    f.write(readme_content)
print("Wrote clean README.md")

# 5. Write updated index.html
index_html_content = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>대한민국 한의약 보건의료 빅데이터 & 6년제 통합의료 교육과정 포털</title>
    <!-- Google Fonts -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Noto+Sans+KR:wght@300;400;500;700;900&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">
    <!-- Font Awesome -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --primary-dark: #0f172a;
            --secondary: #0d9488;
            --accent: #7c3aed;
            --warning: #d97706;
            --bg-main: #f8fafc;
            --card-bg: #ffffff;
            --text-main: #334155;
            --text-heading: #0f172a;
            --text-muted: #64748b;
            --border-color: #e2e8f0;
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1);
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Inter', 'Noto Sans KR', sans-serif;
            background-color: var(--bg-main);
            color: var(--text-main);
            line-height: 1.65;
            -webkit-font-smoothing: antialiased;
        }

        /* Top Header */
        header {
            background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 50%, #0d9488 100%);
            color: #ffffff;
            padding: 3.5rem 2rem;
            text-align: center;
            box-shadow: var(--shadow-lg);
            position: relative;
        }

        header h1 {
            font-size: 2.3rem;
            font-weight: 800;
            margin-bottom: 12px;
            letter-spacing: -0.5px;
        }

        header p {
            color: #cbd5e1;
            font-size: 1.1rem;
            max-width: 850px;
            margin: 0 auto;
            line-height: 1.6;
        }

        .container {
            max-width: 1280px;
            margin: -30px auto 60px;
            padding: 0 24px;
            position: relative;
            z-index: 10;
        }

        /* Hero Banner */
        .hero-banner {
            background: linear-gradient(135deg, #1e3a8a 0%, #0f766e 50%, #6d28d9 100%);
            color: #fff;
            padding: 36px 40px;
            border-radius: 20px;
            margin-bottom: 36px;
            box-shadow: var(--shadow-xl);
            border: 1px solid rgba(255, 255, 255, 0.2);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 24px;
        }

        .hero-content {
            flex: 1;
            min-width: 320px;
        }

        .hero-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(255, 255, 255, 0.2);
            color: #fff;
            padding: 5px 14px;
            border-radius: 9999px;
            font-size: 0.8rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            border: 1px solid rgba(255, 255, 255, 0.3);
            margin-bottom: 14px;
        }

        .hero-banner h2 {
            font-size: 1.85rem;
            font-weight: 900;
            color: #ffffff;
            margin-bottom: 10px;
            line-height: 1.3;
        }

        .hero-banner p {
            color: #e2e8f0;
            font-size: 1.05rem;
            line-height: 1.6;
            max-width: 820px;
        }

        .btn-hero {
            background: #ffffff;
            color: #1e3a8a;
            padding: 16px 32px;
            font-size: 1.1rem;
            font-weight: 800;
            border-radius: 12px;
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            transition: all 0.2s;
            white-space: nowrap;
        }

        .btn-hero:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.25);
            background: #f8fafc;
        }

        /* Policy Card Banner */
        .policy-banner {
            background: #ffffff;
            border-radius: 16px;
            padding: 28px 32px;
            margin-bottom: 36px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-md);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        .section-header-title {
            font-size: 1.45rem;
            font-weight: 800;
            color: var(--text-heading);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-desc {
            color: var(--text-muted);
            font-size: 0.95rem;
            margin-bottom: 24px;
        }

        /* Grid */
        .portal-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
            gap: 24px;
            margin-bottom: 40px;
        }

        .portal-card {
            background: var(--card-bg);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-md);
            transition: transform 0.25s, box-shadow 0.25s;
            display: flex;
            flex-direction: column;
        }

        .portal-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-light);
        }

        .portal-card-header {
            padding: 20px 24px;
            color: #ffffff;
            font-weight: 800;
            font-size: 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-gimhae { background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%); }
        .header-jeonju { background: linear-gradient(135deg, #0d9488 0%, #14b8a6 100%); }
        .header-yeosu  { background: linear-gradient(135deg, #7c3aed 0%, #a855f7 100%); }
        .header-iksan  { background: linear-gradient(135deg, #d97706 0%, #f59e0b 100%); }

        .portal-card-body {
            padding: 24px;
            flex-grow: 1;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }

        .stat-list {
            list-style: none;
            margin-bottom: 20px;
        }

        .stat-list li {
            font-size: 0.92rem;
            margin-bottom: 10px;
            color: var(--text-main);
            display: flex;
            justify-content: space-between;
            border-bottom: 1px dashed var(--border-color);
            padding-bottom: 6px;
        }

        .stat-list li strong {
            color: var(--primary);
            font-weight: 700;
        }

        .btn-card {
            display: block;
            text-align: center;
            padding: 12px 20px;
            background-color: var(--primary);
            color: #ffffff;
            font-weight: 700;
            text-decoration: none;
            border-radius: 8px;
            transition: background 0.2s;
            font-size: 0.92rem;
        }

        .btn-card:hover {
            background-color: var(--primary-light);
        }

        .badge-new {
            background-color: #ef4444;
            color: #fff;
            font-size: 0.72rem;
            padding: 3px 8px;
            border-radius: 9999px;
            font-weight: 700;
        }

        /* Master Reports Table */
        .doc-list-card {
            background: #ffffff;
            border-radius: 16px;
            padding: 28px 32px;
            border: 1px solid var(--border-color);
            box-shadow: var(--shadow-md);
        }

        .doc-table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.92rem;
            margin-top: 16px;
        }

        .doc-table th {
            background: #f1f5f9;
            padding: 12px 16px;
            text-align: left;
            color: #475569;
            font-weight: 700;
            border-bottom: 1px solid var(--border-color);
        }

        .doc-table td {
            padding: 14px 16px;
            border-bottom: 1px solid var(--border-color);
        }

        .doc-table tr:hover td {
            background: #f8fafc;
        }

        footer {
            text-align: center;
            padding: 36px 20px;
            color: var(--text-muted);
            font-size: 0.88rem;
            border-top: 1px solid var(--border-color);
            background: #ffffff;
        }
    </style>
</head>
<body>

    <header>
        <h1>🏛️ 대한민국 한의약 보건의료 빅데이터 & 통합의료 포털</h1>
        <p>HIRA·KOSIS 10개년 청구 빅데이터, 2026 초고령사회 지역돌봄통합지원법, 그리고 6년제 통합의료 교육과정 10개년(2026~2035) 혁신 마스터플랜 통합 허브</p>
    </header>

    <div class="container">
        
        <!-- Major Milestone Banner: 6-Year Integrated Curriculum Roadmap -->
        <div class="hero-banner">
            <div class="hero-content">
                <div class="hero-badge"><i class="fa-solid fa-graduation-cap"></i> 2026-2035 마스터플랜</div>
                <h2>🎓 초고령사회 대응 통합의료 교육과정(6년제) 구축 및 10개년 혁신 로드맵</h2>
                <p>원광대 123과목 전수분석, HIRA 10개년 빅데이터, AI 30.5학점 감축, 2026 시체해부법 개정(대통령령 제36725호) 및 일본·대만 재택의료 벤치마킹을 집대성한 6년제 통합의료 커리큘럼(218학점) 웹 대시보드</p>
            </div>
            <div>
                <a href="curriculum_10yr_roadmap.html" class="btn-hero"><i class="fa-solid fa-table-columns"></i> 10개년 마스터플랜 열람하기 →</a>
            </div>
        </div>

        <!-- Policy Report Banner -->
        <div class="policy-banner">
            <div>
                <span style="background:#eff6ff;color:#1e40af;padding:4px 12px;border-radius:20px;font-size:0.75rem;font-weight:700;text-transform:uppercase;">종합 정책 보고서</span>
                <h3 style="font-size:1.35rem;font-weight:800;color:var(--text-heading);margin-top:6px;margin-bottom:4px;">📜 한의사 재택의료(방문진료) 참여 확대 종합분석 및 정책제언 보고서</h3>
                <p style="color:var(--text-muted);font-size:0.95rem;max-width:800px;">건보 15개 재택시범사업(한의 48.3%), 서울대 이혜진 교수 4대 기능 모델 및 전국 4개 권역 시뮬레이션 기반 종합 정책제안서</p>
            </div>
            <div>
                <a href="policy_report.html" class="btn-card" style="background:#0d9488;padding:12px 24px;font-size:0.95rem;">정책보고서 열람하기 →</a>
            </div>
        </div>

        <!-- Regional Simulation Dashboards Section -->
        <div class="section-header-title"><i class="fa-solid fa-chart-pie" style="color:var(--primary-light);"></i> 지역별 한의약 방문진료 시뮬레이션 대시보드</div>
        <p class="section-desc">KOSIS 국가통계포털 및 HIRA 청구 DB 기반의 HIRA AI 5단계 파이프라인 지역별 5개년 의료 적정성 및 재정 효과 분석 대시보드입니다.</p>

        <div class="portal-grid">

            <!-- Card 1: 경남 & 김해 -->
            <div class="portal-card">
                <div class="portal-card-header header-gimhae">
                    <span>경상남도 & 김해시</span>
                    <span class="badge-new">NEW</span>
                </div>
                <div class="portal-card-body">
                    <ul class="stat-list">
                        <li><span>분석 대상</span> <strong>김해시 & 경남 18개 시·군</strong></li>
                        <li><span>2024 유병격차</span> <strong>김해 12.7년 / 경남 13.2년</strong></li>
                        <li><span>50% 참여 5개년 절감</span> <strong>김해 2,367.6억 / 경남 1.78조</strong></li>
                        <li><span>특이 분석</span> <strong>진료 병행(rho) 차단 제약식</strong></li>
                    </ul>
                    <a href="gimhae_gyeongnam.html" class="btn-card">경상남도 & 김해시 대시보드 →</a>
                </div>
            </div>

            <!-- Card 2: 전북 & 전주 -->
            <div class="portal-card">
                <div class="portal-card-header header-jeonju">
                    <span>전주시 & 전북특별자치도</span>
                </div>
                <div class="portal-card-body">
                    <ul class="stat-list">
                        <li><span>분석 대상</span> <strong>전주시 & 전북 14개 시·군</strong></li>
                        <li><span>고령화율</span> <strong>전북 25.4% (초고령사회)</strong></li>
                        <li><span>50% 참여 5개년 절감</span> <strong>전주 2,510억 / 전북 1.84조</strong></li>
                        <li><span>특이 분석</span> <strong>Nash 균형 & 5대 상병 비교</strong></li>
                    </ul>
                    <a href="jeonju_jeonbuk.html" class="btn-card">전주시 & 전북 대시보드 →</a>
                </div>
            </div>

            <!-- Card 3: 전남 & 여수 -->
            <div class="portal-card">
                <div class="portal-card-header header-yeosu">
                    <span>전라남도 & 여수시</span>
                </div>
                <div class="portal-card-body">
                    <ul class="stat-list">
                        <li><span>분석 대상</span> <strong>여수시 & 전남 22개 시·군</strong></li>
                        <li><span>고령화율</span> <strong>전남 26.6% (전국 최상위)</strong></li>
                        <li><span>50% 참여 5개년 절감</span> <strong>여수 5,500.6억 / 전남 4.59조</strong></li>
                        <li><span>특이 분석</span> <strong>도서·해양 벽지 방문케어 모델</strong></li>
                    </ul>
                    <a href="yeosu_jeonnam.html" class="btn-card">전라남도 & 여수시 대시보드 →</a>
                </div>
            </div>

            <!-- Card 4: 익산시 -->
            <div class="portal-card">
                <div class="portal-card-header header-iksan">
                    <span>익산시 (돌봄 특화)</span>
                </div>
                <div class="portal-card-body">
                    <ul class="stat-list">
                        <li><span>분석 대상</span> <strong>전북특별자치도 익산시</strong></li>
                        <li><span>특화 모델</span> <strong>소아청소년 & 통합방문돌봄</strong></li>
                        <li><span>10%~100% 시뮬레이션</span> <strong>5개년 최대 7,483.5억 절감</strong></li>
                        <li><span>특이 분석</span> <strong>20세 이하 의료비 정밀 추정</strong></li>
                    </ul>
                    <a href="iksan.html" class="btn-card">익산시 대시보드 →</a>
                </div>
            </div>

        </div>

        <!-- Master Documents & Reports Repository Table -->
        <div class="doc-list-card">
            <h3 style="font-size:1.3rem;font-weight:800;color:var(--text-heading);margin-bottom:6px;"><i class="fa-solid fa-folder-open" style="color:var(--secondary);"></i> 종합 연구 보고서 및 교육과정 마크다운 문서 목록</h3>
            <p style="color:var(--text-muted);font-size:0.9rem;">본 저장소에 등록된 마스터 마크다운 보고서 파일들의 상세 목록입니다.</p>
            
            <table class="doc-table">
                <thead>
                    <tr>
                        <th>보고서 문서명</th>
                        <th>문서 구분</th>
                        <th>핵심 연구 내용</th>
                        <th>파일 링크</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>통합의료_한의학교육과정_10년_혁신로드맵.md</strong></td>
                        <td><span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;">마스터 플랜</span></td>
                        <td>6년제 218학점 편제표, 노년증후군 CPG 모듈, 10개년 로드맵</td>
                        <td><a href="통합의료_한의학교육과정_10년_혁신로드맵.md" style="color:var(--primary-light);font-weight:600;">MD 보기</a></td>
                    </tr>
                    <tr>
                        <td><strong>재택의료_정책기반_한의학교육_개선방안_보고서.md</strong></td>
                        <td><span style="background:#ccfbf1;color:#0f766e;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;">정책 분석</span></td>
                        <td>KDCA 8대 체계, 건보 15개 시범사업, 일본/대만 국제비교</td>
                        <td><a href="재택의료_정책기반_한의학교육_개선방안_보고서.md" style="color:var(--primary-light);font-weight:600;">MD 보기</a></td>
                    </tr>
                    <tr>
                        <td><strong>한의학교육_의료통합_상세보고서.md</strong></td>
                        <td><span style="background:#f3e8ff;color:#6b21a8;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;">의료 통합</span></td>
                        <td>2026 시체해부법(대통령령 제36725호) 및 POCUS/POCT 진단 실습</td>
                        <td><a href="한의학교육_의료통합_상세보고서.md" style="color:var(--primary-light);font-weight:600;">MD 보기</a></td>
                    </tr>
                    <tr>
                        <td><strong>한평원_KAS2022_평가기준_분석_및_개선안.md</strong></td>
                        <td><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;">평가 인증</span></td>
                        <td>한국한의학교육평가원 KAS2022 P2.1~P5.1 개정안</td>
                        <td><a href="한평원_KAS2022_평가기준_분석_및_개선안.md" style="color:var(--primary-light);font-weight:600;">MD 보기</a></td>
                    </tr>
                    <tr>
                        <td><strong>중의학교육표준_비교_타당성_평가보고서.md</strong></td>
                        <td><span style="background:#e0e7ff;color:#3730a3;padding:2px 8px;border-radius:6px;font-size:0.75rem;font-weight:700;">국제 비교</span></td>
                        <td>WFCMS 글로벌 표준(SCM0003-2009) 타당성 94점(A) 평가</td>
                        <td><a href="중의학교육표준_비교_타당성_평가보고서.md" style="color:var(--primary-light);font-weight:600;">MD 보기</a></td>
                    </tr>
                </tbody>
            </table>
        </div>

    </div>

    <footer>
        <p><strong>대한민국 한의약 보건의료 빅데이터 및 교육과정 혁신 저장소</strong></p>
        <p style="margin-top:4px;">원광대학교 한의과대학 보건의료정책 및 교육혁신 연구팀 | GitHub Repository: <a href="https://github.com/jaehyokim-sketch/km-healthcare-stats" style="color:var(--primary-light);">jaehyokim-sketch/km-healthcare-stats</a></p>
    </footer>

</body>
</html>
"""

with open(os.path.join(repo_dir, "index.html"), "w", encoding="utf-8") as f:
    f.write(index_html_content)
print("Wrote clean index.html")

print("Smart cleanup script completed!")
